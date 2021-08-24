import os
import tempfile
import logging
import traceback
from shutil import copyfile, which
import subprocess


logger = logging.getLogger('RucioClientEnvironmentLogger')
logger.setLevel(logging.DEBUG)


class RucioClientEnvironment:
    def __init__(self, rucio):
        self.rucio = rucio
        self.instance_config = self.rucio.instance_config
        self.base_url = self.rucio.base_url
        self.auth_config = self.rucio.auth_config
        self.auth_type = self.rucio.auth_type
        self.auth_url = self.rucio.auth_url

    def __enter__(self):
        self.tempdir = tempfile.TemporaryDirectory()
        logger.debug("Created temporary directory: %s", self.tempdir.name)

        rucio_home = self.tempdir.name

        config = self._get_config()
        RucioClientEnvironment.write_temp_config_file(self.tempdir.name, config)
        os.environ['RUCIO_HOME'] = rucio_home

        site_name = self.instance_config.get("site_name")
        if site_name is not None:
            os.environ['SITE_NAME'] = site_name

        if self.auth_config is not None:
            if self.auth_type == 'x509':
                RucioClientEnvironment.prepare_x509_user_authentication(rucio_home, instance_config=self.instance_config, auth_config=self.auth_config)
            elif self.auth_type == 'x509_proxy':
                RucioClientEnvironment.prepare_x509_proxy_authentication(rucio_home, auth_config=self.auth_config)

        return self.tempdir.name

    def __exit__(self, *args, **kwargs):
        self.tempdir.cleanup()

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

    def _get_config(self):
        auth_config = self.auth_config
        cert_path = auth_config.get('certificate') if auth_config else None
        key_path = auth_config.get('key') if auth_config else None
        username = auth_config.get('username') if auth_config else None
        password = auth_config.get('password') if auth_config else None
        account = auth_config.get('account') if auth_config else None

        config = {
            'rucio_host': self.base_url,
            'auth_host': self.auth_url,
            'auth_type': self.auth_type,
            'username': username,
            'password': password,
            'client_cert': cert_path,
            'client_key': key_path,
            'account': account,
            'ca_cert': self.instance_config.get('rucio_ca_cert')
        }

        vo = self.instance_config.get('vo')  # pylint: disable=invalid-name
        if vo is not None:
            config['vo'] = vo

        return config
