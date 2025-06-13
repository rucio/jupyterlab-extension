# Configuration Guide
## Modes

### Replica Mode
In this mode, the files are transferred by Rucio to a storage mounted to the JupyterLab server. In order to use the extension in this mode, you need to have the following set up:
- A JupyterLab version 2 installation.
- At least one Rucio instance.
- A storage system that is attached to the JupyterLab installation via FUSE.
    - The storage system should be compatible with Rucio and added as a Rucio Storage Element.
    - The storage element will be shared among multiple users, so be sure to allow all users who will be using the extension to have **read** permission to the path.
    - It's recommended that quotas be disabled, since the extension does not care if the replication fails because of quota error.

### Download Mode
In this mode, the extension downloads the files to the user directory. This is used when your JupyterLab installation does not use a storage as an RSE. To use the extension in this mode, you need to have the following set up:
- A JupyterLab version 2 installation.
- At least one Rucio instance.
- Rucio Storage Elements (RSE) that are accessible from the notebook server, with no authentication scheme.

## Configuration
The extension can be configured locally or remotely.

### Local Configuration
In your Jupyter configuration (could be `~/.jupyter/jupyter_notebook_config.json`), add the following snippet:
```json
{
    "RucioConfig": {
        "instances": [
            {
                "name": "experiment.cern.ch",
                "display_name": "Experiment",
                "rucio_base_url": "https://rucio",
                "rucio_auth_url": "https://rucio",
                "rucio_ca_cert": "/path/to/rucio_ca.pem",
                "destination_rse": "SWAN-EOS",
                "rse_mount_path": "/eos/rucio",
                "path_begins_at": 4,
                "mode": "replica"
            }
        ]
    }
}
```

### Remote Configuration
To use remote configuration, use the following snippet:
```json
{
    "RucioConfig": {
        "instances": [
            {
                "name": "experiment.cern.ch",
                "display_name": "Experiment",
                "$url": "https://url-to-rucio-configuration/config.json"
            }
        ]
    }
}
```

In the JSON file pointed by the value in `$url`, use the following snippet:
```json
{
    "rucio_base_url": "https://rucio",
    "destination_rse": "SWAN-EOS",
    "rucio_auth_url": "https://rucio",
    "rucio_ca_cert": "/path/to/rucio_ca.pem",
    "rse_mount_path": "/eos/rucio",
    "path_begins_at": 4,
    "mode": "replica"
}
```
Attributes `name`, `display_name`, and `mode` must be defined locally, while the rest can be defined remotely. If an attribute is defined in both local and remote configuration, the local one is used.

### Configuration Items
#### Name - `name`
A unique name to identify Rucio instance, should be machine readable. It is recommended to use FQDN. Must be declared locally.

Example: `atlas.cern.ch`, `cms.cern.ch`

#### Display Name - `display_name`
A name that will be displayed to users in the interface. Must be declared locally.

Example: `ATLAS`, `CMS`

#### Mode - `mode`
The mode in which the extension operates. Must be declared locally.
1. Replica mode (`replica`)
2. Download mode (`download`)

#### Rucio Base URL - `rucio_base_url`
Base URL for the Rucio instance accessible from the JupyterLab server, **without trailing slash**.

Example: `https://rucio`

#### Rucio Auth URL - `rucio_auth_url`
Base URL for the Rucio instance handling authentication (if separate) accessible from the JupyterLab server, **without trailing slash**.

Example: `https://rucio-auth`

#### Rucio CA Certificate File Path - `rucio_ca_cert`
Path to Rucio server certificate file, accessible via filesystem mount. Optional in Replica mode, mandatory in Download mode.

Example: `/opt/rucio/rucio_ca.pem`

#### App ID - `app_id`
Rucio App ID. Optional.

Example: `swan`

#### Site Name - `site_name`
Site name of the JupyterLab instance, optional. It allows Rucio to know whether to serve a proxied PFN or not.

Example: `ATLAS`

#### VO Name - `vo`
VO of the instance. Optional, for use in multi-VO installations only. If VOMS is enabled, this value will be supplied as `--voms` option when invoking `voms-proxy-init`.

Example: `def`

#### VOMS Enabled - `voms_enabled`
The extension uses `voms-proxy-init` to generate a Proxy certificate when downloading a file from an authenticated RSE.

If set to `true`, `vo` option is specified, and X.509 User Certificate is used, the extension will invoke `voms-proxy-init` with the `--voms` argument set to the extension's `vo` option.

Optional, with default: `false`

#### VOMS `certdir` Path - `voms_certdir_path`
If VOMS is enabled and this configuration is set, the extension will set the `--certdir` option with this value. Refer to `voms-proxy-init` documentation.

Example: `/etc/grid-security/certificates`

#### VOMS `vomsdir` Path - `voms_vomsdir_path`
If VOMS is enabled and this configuration is set, the extension will set the `--vomsdir` option with this value. Refer to `voms-proxy-init` documentation.

Example: `/etc/grid-security/vomsdir`

**WARNING:** In earlier versions, `voms-proxy-init` does not support the `--vomsdir` option. In that case, this option must be omitted.

#### VOMS `vomses` File Path - `voms_vomses_path`
If VOMS is enabled and this configuration is set, the extension will set the `--vomses` option with this value. Refer to `voms-proxy-init` documentation.

Example: `/etc/vomses`

**WARNING:** In earlier versions, `voms-proxy-init` does not support the `--vomsdir` option. In that case, this option must be omitted.

#### Destination RSE - `destination_rse`
The name of the Rucio Storage Element that is mounted to the JupyterLab server. Mandatory, only applicable in Replica mode.

Example: `SWAN-EOS`

#### RSE Mount Path - `rse_mount_path`
The base path in which the RSE is mounted to the server. Mandatory, only applicable in Replica mode.

Example: `/eos/rucio`

#### File Path Starting Index - `path_begins_at`
This configuration indicates which part of the PFN should be appended to the mount path. Only applicable in Replica mode. Defaults to `0`.

Example: let us say that the PFN of a file is `root://xrd1:1094//rucio/test/49/ad/f1.txt` and the mount path is `/eos/rucio`. A starting index of `1` means that the path starting from the 2nd slash (index 1) in the PFN will be appended to the mount path. The resulting path would be `/eos/rucio/test/49/ad/f1.txt`.

#### Replication Rule Lifetime (in days) - `replication_rule_lifetime_days`
Replication rule lifetime in days. Optional, only applicable in Replica mode.

Example: `365`

#### Wildcard Search Enabled - `wildcard_enabled`
Whether or not wildcard DID search is allowed. Optional, defaults to `false`.


#### OpenID Connect Auth Source - `oidc_auth`
Specifies where should the extension gets the OIDC token from. Optional, the value should be `file` or `env`.

#### OpenID Connect Token Filename - `oidc_file_name`
Specifies an absolute path to a file containing the OIDC access token.

#### OpenID Connect Token Environment Variable Name - `oidc_env_name`
Specifies the environment variable name containing the OIDC access token.

## IPython Kernel
To allow users to access the paths from within the notebook, a kernel extension must be enabled. The kernel resides in module `rucio_jupyterlab.kernels.ipython`.

To enable the kernel extension from inside a notebook, use `load_ext` IPython magic:

```py
%load_ext rucio_jupyterlab.kernels.ipython
```

Or, if you want to enable it by default, put the following snippet in your IPython configuration (could be `~/.ipython/profile_default/ipython_kernel_config.py`).

```python
c.IPKernelApp.extensions = ['rucio_jupyterlab.kernels.ipython']
```

## Enabling OpenID Connect Authentication

Unlike the other authentication methods supported by the extension, which is configurable by users only, OIDC auth should be configured by the admins. Users won't see "OpenID Connect" option if OIDC auth is not configured properly.

This extension does not provide a way for users to authenticate directly from the extension. Instead, the OIDC token must be obtained from an external mechanism.

In a multi-user setup with JupyterHub, admins must make the OIDC token accessible from the single user's container via either a file or an environment variable. Then, they need to configure the `oidc_auth` and `oidc_env_name` or `oidc_file_name` parameters (see above).

Furthermore, the JupyterHub installation must have a mechanism of periodically refreshing the OIDC token so that an expired token is not used.

See the following sections for more details.

### Configuring JupyterHub with OIDC: Single user Dockerfile and Variables

The Docker image for the single-user container must include the Rucio extension and the defined OpenID Connect variables. To install the extension, refer to the provided [Dockerfile](Dockerfile). Additionally, the [configure.py](docker/configure.py) script takes care of writing the variables from the environment to the Jupyter configuration.

### Configuring JupyterHub with OIDC: JupyterHub Chart

JupyterHub installation is possible through the use of the Helm Chart provided by [Zero to JupyterHub with Kubernetes](https://z2jh.jupyter.org/en/stable/). In order to enable the Rucio extension, add the following customisation to the values.

1. Add the custom in `singleuser.image`:

```yaml
singleuser:
  image: <image-url>:<image-tag>
```

2. Add a custom authentication script to `hub.extraConfig`. For instance, label it as `token-exchange` and append the script in this format:

```yaml
hub:
  extraConfig:
    token-exchange: |
      import pprint
      import os
      import warnings
      import requests
      from oauthenticator.generic import GenericOAuthenticator

      # custom authenticator to enable auth_state and get access token to set as env var for rucio extension
      class RucioAuthenticator(GenericOAuthenticator):
          def __init__(self, **kwargs):
            super().__init__(**kwargs)
              self.enable_auth_state = True

          def exchange_token(self, token):
              params = {
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                  'subject_token': token,
                  'scope': 'openid profile',
                  'audience': 'rucio'
              }
              response = requests.post(self.token_url, data=params)
              rucio_token = response.json()['access_token']
              return rucio_token
        
          async def pre_spawn_start(self, user, spawner):
              auth_state = await user.get_auth_state()
              pprint.pprint(auth_state)
              if not auth_state:
                  # user has no auth state
                  return
            
              # define token environment variable from auth_state
              spawner.environment['RUCIO_ACCESS_TOKEN'] = self.exchange_token(auth_state['access_token'])
              spawner.environment['EOS_ACCESS_TOKEN'] = auth_state['access_token']

      # set the above authenticator as the default
      c.JupyterHub.authenticator_class = RucioAuthenticator

      # enable authentication state
      c.GenericOAuthenticator.enable_auth_state = True

      if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
          warnings.warn(
              "Need JUPYTERHUB_CRYPT_KEY env for persistent auth_state.\n"
              "    export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)"
          )
          c.CryptKeeper.keys = [os.urandom(32)]
```

3. Add the configuration parameters for the custom authenticator to the `hub.config`:

```yaml
hub:
  config:
    RucioAuthenticator:
      client_id: <your-client-id>
      client_secret: <your-client-secret>
      authorize_url: <your-auth-url>
      token_url: <your-token-url>
      userdata_url: <your-userinfo-url>
      username_key: preferred_username
      scope:
        - openid
        - profile
        - email
```

4. Add the required extension parameters to the `singleuser.extraEnv`:

```yaml
singleuser:
  extraEnv:
    RUCIO_MODE: "replica"
    RUCIO_WILDCARD_ENABLED: "1"
    RUCIO_BASE_URL: "<your-rucio-url>"
    RUCIO_AUTH_URL: "<your-rucio-auth-url>"
    RUCIO_WEBUI_URL: "<your-rucio-ui-url>"
    RUCIO_DISPLAY_NAME: "<your-rucio-instance-display-name>"
    RUCIO_NAME: "<your-rucio-instance-name>"
    RUCIO_SITE_NAME: "<your-rucio-instance-site-name>"
    RUCIO_OIDC_AUTH: "env"
    RUCIO_OIDC_ENV_NAME: "RUCIO_ACCESS_TOKEN"
    RUCIO_DEFAULT_AUTH_TYPE: "oidc"
    RUCIO_LOG_LEVEL: "warning"
    RUCIO_OAUTH_ID: "<your-rucio-oauth-id>" # audience
    RUCIO_DEFAULT_INSTANCE: "<your-rucio-instance-name>"
    RUCIO_DESTINATION_RSE: "EOS RSE"
    RUCIO_RSE_MOUNT_PATH: "/eos/eos-rse"
    RUCIO_PATH_BEGINS_AT: "4"
    RUCIO_CA_CERT: "<your-rucio-ca-file-path>"
    OAUTH2_TOKEN: "FILE:/tmp/eos_oauth.token"
```

5. Build the Docker image and install the Helm Chart with the specified values.

*Note: This configuration works in replica mode and maps an EOS RSE as the target RSE, which is FUSE mounted on the nodes where Jupyterhub is running.*
