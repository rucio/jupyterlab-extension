import os
import tempfile
import logging
import multiprocessing as mp
import traceback
import base64
import json
from shutil import copyfile, which
import subprocess
import psutil
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile
import rucio_jupyterlab.utils as utils


logger = logging.getLogger('RucioClientEnvironmentLogger')
logger.setLevel(logging.DEBUG)


class RucioClientEnvironment:
    @staticmethod
    def prepare_x509_user_authentication(rucio_home, instance_config, auth_config):
        cert_path = auth_config.get('certificate')
        key_path = auth_config.get('key')
        voms_nickname = instance_config.get('vo')
        voms_enabled = instance_config.get('voms_enabled', False)
        voms_certdir_path = instance_config.get('voms_certdir_path')
        voms_vomsdir_path = instance_config.get('voms_vomsdir_path')
        voms_vomses_path = instance_config.get('voms_vomses_path')

        if cert_path and key_path:
            tmp_cert_path, tmp_key_path = RucioClientEnvironment.write_user_certificate_files(rucio_home, cert_path, key_path)
            tmp_proxy_path = RucioClientEnvironment.generate_proxy_certificate(
                rucio_home,
                tmp_cert_path,
                tmp_key_path,
                voms_enabled=voms_enabled,
                voms_nickname=voms_nickname,
                voms_certdir_path=voms_certdir_path,
                voms_vomsdir_path=voms_vomsdir_path,
                voms_vomses_path=voms_vomses_path
            )

            if tmp_proxy_path is not None:
                os.environ['X509_USER_PROXY'] = tmp_proxy_path

            if tmp_cert_path is not None and tmp_key_path is not None:
                os.environ['X509_USER_CERT'] = tmp_cert_path
                os.environ['X509_USER_KEY'] = tmp_key_path

    @staticmethod
    def prepare_x509_proxy_authentication(rucio_home, auth_config):
        proxy_path = auth_config.get('proxy')

        if proxy_path:
            tmp_proxy_path = RucioClientEnvironment.write_proxy_certificate_files(rucio_home, proxy_path)
            if tmp_proxy_path is not None:
                os.environ['X509_USER_PROXY'] = tmp_proxy_path

    @staticmethod
    def write_temp_config_file(base_dir, config):
        lines = ['[client]\n'] + [f'{x}={config[x]}\n' for x in config]

        etc_path = os.path.join(base_dir, 'etc')
        cfg_path = os.path.join(etc_path, 'rucio.cfg')
        os.makedirs(etc_path, exist_ok=True)

        config_file = open(cfg_path, 'w')
        config_file.writelines(lines)
        config_file.close()

    @staticmethod
    def write_user_certificate_files(base_dir, cert_path, key_path):
        dest_cert_path = os.path.join(base_dir, 'usercert.pem')
        dest_key_path = os.path.join(base_dir, 'userkey.pem')

        copyfile(cert_path, dest_cert_path)
        copyfile(key_path, dest_key_path)

        os.chmod(dest_cert_path, 0o400)
        os.chmod(dest_key_path, 0o400)

        return dest_cert_path, dest_key_path

    @staticmethod
    def write_proxy_certificate_files(base_dir, proxy_path):
        dest_proxy_path = os.path.join(base_dir, 'proxy.pem')
        copyfile(proxy_path, dest_proxy_path)
        os.chmod(dest_proxy_path, 0o400)
        return dest_proxy_path

    @staticmethod
    def generate_proxy_certificate(base_dir, cert_path, key_path, voms_enabled=False, voms_nickname=None, voms_certdir_path=None, voms_vomsdir_path=None, voms_vomses_path=None):
        dest_proxy_path = os.path.join(base_dir, 'x509up')
        cmd_args = {
            '-cert': cert_path,
            '-key': key_path,
            '-out': dest_proxy_path
        }

        if which('voms-proxy-init') is not None:
            executable = "voms-proxy-init"

            if voms_enabled:
                if voms_nickname is not None:
                    cmd_args['--voms'] = voms_nickname

                if voms_certdir_path is not None:
                    cmd_args['--certdir'] = voms_certdir_path

                if voms_vomsdir_path is not None:
                    cmd_args['--vomsdir'] = voms_vomsdir_path

                if voms_vomses_path is not None:
                    cmd_args['--vomses'] = voms_vomses_path
        else:
            executable = "grid-proxy-init"

        try:
            args = []
            for option in cmd_args:
                args.append(option)
                args.append(cmd_args[option])

            process = subprocess.Popen([executable] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()

            if process.returncode != 0:
                logger.error("Generating proxy certificate fails, process returns non-zero code.")
                logger.error(out)
                logger.error(err)
                return None

            return dest_proxy_path
        except subprocess.SubprocessError:
            traceback.print_exc()
            return None
