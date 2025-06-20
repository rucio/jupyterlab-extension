# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import os
import tempfile
import logging
from shutil import copyfile, which
import subprocess

logger = logging.getLogger(__name__)


class RucioClientEnvironment:
    """
    A context manager to create a temporary, isolated environment for the Rucio client.

    Handles the creation of a temporary rucio.cfg, setting of environment
    variables, and management of authentication credentials like X.509
    certificates and proxies. The environment is automatically cleaned up on exit.
    """

    def __init__(self, rucio):
        self.rucio = rucio
        self.instance_config = self.rucio.instance_config
        self.base_url = self.rucio.base_url
        self.auth_config = self.rucio.auth_config
        self.auth_type = self.rucio.auth_type
        self.auth_url = self.rucio.auth_url
        self.tempdir = None  # Initialize to None for robust cleanup

    def __enter__(self):
        try:
            self.tempdir = tempfile.TemporaryDirectory()
            logger.debug("Created temporary directory: %s", self.tempdir.name)

            rucio_home = self.tempdir.name
            os.environ['RUCIO_HOME'] = rucio_home
            logger.info("Set RUCIO_HOME to: %s", rucio_home)

            config = self._get_config()
            if not self.write_temp_config_file(rucio_home, config):
                # The helper method logs the specific error.
                raise RuntimeError("Failed to write rucio.cfg file. See logs for details.")

            site_name = self.instance_config.get("site_name")
            if site_name:
                os.environ['SITE_NAME'] = site_name
                logger.info("Set SITE_NAME to: %s", site_name)

            if self.auth_config:
                if self.auth_type == 'x509':
                    self.prepare_x509_user_authentication(rucio_home)
                elif self.auth_type == 'x509_proxy':
                    self.prepare_x509_proxy_authentication(rucio_home)

            return self.tempdir.name
        except Exception:
            logger.error("Failed to set up Rucio client environment. Cleaning up.")
            # Ensure cleanup is called if __enter__ fails after tempdir creation
            self.__exit__(None, None, None)
            raise  # Re-raise the exception to the caller

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tempdir:
            self.tempdir.cleanup()
            logger.debug("Cleaned up temporary directory: %s", self.tempdir.name)

    def prepare_x509_user_authentication(self, rucio_home):
        logger.info("Preparing x509 user authentication.")
        cert_path = self.auth_config.get('certificate')
        key_path = self.auth_config.get('key')

        if not (cert_path and key_path):
            logger.warning("x509 authentication selected, but certificate or key path is missing.")
            return

        tmp_cert_path, tmp_key_path = self.write_user_certificate_files(rucio_home, cert_path, key_path)
        if not (tmp_cert_path and tmp_key_path):
            return  # Error is logged within the helper method

        # Set certificate env variables regardless of proxy generation
        os.environ['X509_USER_CERT'] = tmp_cert_path
        os.environ['X509_USER_KEY'] = tmp_key_path
        logger.info("Set X509_USER_CERT and X509_USER_KEY.")

        # Generate a proxy from the temporary certificate
        tmp_proxy_path = self.generate_proxy_certificate(
            base_dir=rucio_home,
            cert_path=tmp_cert_path,
            key_path=tmp_key_path,
            voms_enabled=self.instance_config.get('voms_enabled', False),
            voms_nickname=self.instance_config.get('vo'),
            voms_certdir_path=self.instance_config.get('voms_certdir_path'),
            voms_vomsdir_path=self.instance_config.get('voms_vomsdir_path'),
            voms_vomses_path=self.instance_config.get('voms_vomses_path')
        )

        if tmp_proxy_path:
            os.environ['X509_USER_PROXY'] = tmp_proxy_path
            logger.info("Set X509_USER_PROXY to: %s", tmp_proxy_path)

    def prepare_x509_proxy_authentication(self, rucio_home):
        logger.info("Preparing x509 proxy authentication.")
        proxy_path = self.auth_config.get('proxy')

        if not proxy_path:
            logger.warning("x509_proxy authentication selected, but proxy path is missing.")
            return

        tmp_proxy_path = self.write_proxy_certificate_file(rucio_home, proxy_path)
        if tmp_proxy_path:
            os.environ['X509_USER_PROXY'] = tmp_proxy_path
            logger.info("Set X509_USER_PROXY to: %s", tmp_proxy_path)

    @staticmethod
    def write_temp_config_file(base_dir, config):
        lines = ['[client]\n'] + [f'{key}={config[key]}\n' for key in config]
        etc_path = os.path.join(base_dir, 'etc')
        cfg_path = os.path.join(etc_path, 'rucio.cfg')

        try:
            os.makedirs(etc_path, exist_ok=True)
            with open(cfg_path, 'w') as config_file:
                config_file.writelines(lines)
            logger.info("Successfully wrote Rucio config to: %s", cfg_path)
            return True
        except (IOError, OSError) as e:
            logger.error("Failed to write Rucio config file at %s: %s", cfg_path, e)
            return False

    @staticmethod
    def write_user_certificate_files(base_dir, cert_path, key_path):
        dest_cert_path = os.path.join(base_dir, 'usercert.pem')
        dest_key_path = os.path.join(base_dir, 'userkey.pem')

        try:
            copyfile(cert_path, dest_cert_path)
            copyfile(key_path, dest_key_path)
            # Use 0o400 (read-only by owner) for keys and certs for security.
            os.chmod(dest_cert_path, 0o400)
            os.chmod(dest_key_path, 0o400)
            logger.info("Copied user certificate and key to temporary directory.")
            return dest_cert_path, dest_key_path
        except (FileNotFoundError, IOError, OSError) as e:
            logger.error("Failed to copy or set permissions for certificate/key: %s", e)
            return None, None

    @staticmethod
    def write_proxy_certificate_file(base_dir, proxy_path):
        dest_proxy_path = os.path.join(base_dir, 'proxy.pem')
        try:
            copyfile(proxy_path, dest_proxy_path)
            os.chmod(dest_proxy_path, 0o400)
            logger.info("Copied proxy certificate to: %s", dest_proxy_path)
            return dest_proxy_path
        except (FileNotFoundError, IOError, OSError) as e:
            logger.error("Failed to copy or set permissions for proxy file: %s", e)
            return None

    @staticmethod
    def generate_proxy_certificate(base_dir, cert_path, key_path, **voms_opts):
        dest_proxy_path = os.path.join(base_dir, 'x509up')
        cmd_args = {
            '-cert': cert_path,
            '-key': key_path,
            '-out': dest_proxy_path
        }

        # Determine which executable to use
        if voms_opts.get('voms_enabled') and which('voms-proxy-init'):
            executable = "voms-proxy-init"
            if voms_opts.get('voms_nickname'):
                cmd_args['--voms'] = voms_opts['voms_nickname']
            if voms_opts.get('voms_certdir_path'):
                cmd_args['--certdir'] = voms_opts['voms_certdir_path']
            if voms_opts.get('voms_vomsdir_path'):
                cmd_args['--vomsdir'] = voms_opts['voms_vomsdir_path']
            if voms_opts.get('voms_vomses_path'):
                cmd_args['--vomses'] = voms_opts['voms_vomses_path']
        elif which('grid-proxy-init'):
            executable = "grid-proxy-init"
        else:
            logger.error("Neither 'voms-proxy-init' nor 'grid-proxy-init' found in PATH.")
            return None

        logger.info("Attempting to generate proxy certificate using '%s'.", executable)
        try:
            # Build the command as a list of strings
            args = []
            for option, value in cmd_args.items():
                args.extend([option, value])

            process = subprocess.Popen([executable] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error("Proxy generation with '%s' failed with exit code %d.", executable, process.returncode)
                logger.error("STDOUT: %s", stdout.strip())
                logger.error("STDERR: %s", stderr.strip())
                return None

            logger.info("Successfully generated proxy certificate at: %s", dest_proxy_path)
            return dest_proxy_path
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.exception("An exception occurred while trying to run %s.", executable)
            return None

    def _get_config(self):
        config_all = {
            'rucio_host': self.base_url,
            'auth_host': self.auth_url,
            'auth_type': self.auth_type,
            'username': self.auth_config.get('username') if self.auth_config else None,
            'password': self.auth_config.get('password') if self.auth_config else None,
            'account': self.auth_config.get('account') if self.auth_config else None,
            'client_cert': self.auth_config.get('certificate') if self.auth_config else None,
            'client_key': self.auth_config.get('key') if self.auth_config else None,
            'ca_cert': self.instance_config.get('rucio_ca_cert'),
            'vo': self.instance_config.get('vo')
        }
        # Filter out keys with None values to keep the config file clean
        return {k: v for k, v in config_all.items() if v is not None}
