# Configuration Guide
## Operation Modes

The extension supports two distinct operation modes, which determine how files are made available to users.

### Replica Mode

In this mode, files are transferred by Rucio to a storage mounted to the JupyterLab server. This is the recommended mode for shared environments.

**Requirements:**
- At least one Rucio instance
- A POSIX mounted storage system attached to the JupyterLab installation:
  - The storage must be mounted on the host machine or Kubernetes nodes where JupyterLab pods run
  - Common FUSE implementations include:
    - **EOS**: CERN's disk-based storage system (via [`eos fuse mount`](https://eos-docs.web.cern.ch/configuration/fuse.html))
    - **CephFS**: Distributed filesystem (via [`ceph-fuse`](https://docs.ceph.com/en/latest/man/8/ceph-fuse/))
    - **XRootD**: High-performance data access protocol (via [`xrootdfs`](https://manpages.debian.org/testing/xrootd-fuse/xrootdfs.1.en.html))
  - The mounted storage must be registered as a Rucio Storage Element (RSE) in your Rucio instance
  - Should be shared among multiple users with read permissions for all users
  - It's recommended that quotas be disabled, as the extension does not handle quota errors gracefully

  For mounting examples, see the [ESCAPE VRE infrastructure documentation](https://github.com/vre-hub/vre/tree/master/infrastructure)

**Configuration Parameters:**
- `destination_rse`: The name of the Rucio Storage Element mounted to the JupyterLab server
- `rse_mount_path`: The base path where the RSE is mounted
- `path_begins_at`: Index indicating which part of the PFN should be appended to the mount path (defaults to 0)
- `replication_rule_lifetime_days`: Optional lifetime for replication rules in days

### Download Mode

In this mode, the extension downloads files directly to the user's home directory or another local storage location. This mode is useful when your JupyterLab installation does not have a Rucio Storage Element (RSE) mounted.

**Requirements:**
- At least one Rucio instance
- Network access to Rucio Storage Elements (RSE) from the notebook server to download files
- Sufficient local storage space available in the user directory for downloaded files

## Configuration
The extension can be configured locally or remotely via a JSON configuration file.

### Configuration File Location

The extension is configured via a `.json` file, usually located in `$HOME/.jupyter/` and named `jupyter_server_config.json`. This file must be present before the Jupyter server session starts and can be added via:
- Jupyter `before-notebook.d` hooks
- Docker `CMD` instruction or entrypoint scripts

### Base Local Configuration
In your Jupyter configuration (e.g., `~/.jupyter/jupyter_server_config.json`), add the following snippet for a basic setup:
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
                "destination_rse": "XRD1-EOS",
                "rse_mount_path": "/eos/rucio",
                "path_begins_at": 4,
                "mode": "replica"
            }
        ]
    }
}
```

### Advanced Local Configuration

For production environments with multiple instances and advanced features:

```json
{
    "RucioConfig": {
        "instances": [
            {
                "name": "experiment1.cern.ch",
                "display_name": "Experiment1",
                "rucio_base_url": "https://rucio1",
                "rucio_auth_url": "https://rucio1",
                "rucio_ca_cert": "/path/to/rucio_ca.pem",
                "site_name": "CERN",
                "vo": "experiment1-vo",
                "mode": "replica",
                "wildcard_enabled": true,
                "oidc_auth": "env",
                "oidc_env_name": "RUCIO_ACCESS_TOKEN1"
            },
            {
                "name": "experiment2.cern.ch",
                "display_name": "Experiment2",
                "rucio_base_url": "https://rucio2",
                "rucio_auth_url": "https://rucio2",
                "rucio_ca_cert": "/path/to/rucio_ca.pem",
                "site_name": "CERN",
                "vo": "experiment2-vo",
                "mode": "replica",
                "wildcard_enabled": true,
                "oidc_auth": "env",
                "oidc_env_name": "RUCIO_ACCESS_TOKEN2"
            }
        ],
        "default_instance": "experiment1.cern.ch",
        "default_auth_type": "oidc",
        "log_level": "debug"
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

In the JSON file pointed by the value in `$url`, use a snippet similar to this:
```json
{
    "rucio_base_url": "https://rucio",
    "destination_rse": "XRD1-EOS",
    "rucio_auth_url": "https://rucio",
    "rucio_ca_cert": "/path/to/rucio_ca.pem",
    "rse_mount_path": "/eos/rucio",
    "path_begins_at": 4,
    "mode": "replica",
    ...
}
```
**Note:** Attributes `name`, `display_name`, and `mode` must be defined locally (either in the configuration file or as environment variables). If an attribute is defined in both local and remote configuration, the local one takes precedence.

For a complete list of configuration parameters, see the next section or the [Rucio JupyterLab Extension GitHub repository](https://github.com/rucio/jupyterlab-extension/blob/master/CONFIGURATION.md)

## Configuration Parameters

### Instance Configuration

#### Name - `name`
A unique machine-readable identifier for the Rucio instance. It is recommended to use FQDN (Fully Qualified Domain Name). Must be declared locally in the configuration file or set via the `RUCIO_NAME` environment variable.

Example: `atlas.cern.ch`, `cms.cern.ch`

#### Display Name - `display_name`
A user-friendly name displayed in the extension interface. Must be declared locally in the configuration file or set via the `RUCIO_DISPLAY_NAME` environment variable.

Example: `ATLAS`, `CMS`

#### Mode - `mode`
The operation mode of the extension. Must be declared locally in the configuration file or set via the `RUCIO_MODE` environment variable.

Allowed values:
- `replica`: Files are transferred to a mounted storage
- `download`: Files are downloaded to user directory

#### Rucio Base URL - `rucio_base_url`
Base URL for the Rucio instance accessible from the JupyterLab server, **without trailing slash**.

Example: `https://rucio`

#### Rucio Auth URL - `rucio_auth_url`
Base URL for the Rucio authentication service (if separate) accessible from the JupyterLab server, **without trailing slash**.

Example: `https://rucio-auth`

#### Rucio CA Certificate File Path - `rucio_ca_cert`
Path to Rucio server certificate file, accessible via filesystem mount. Optional in Replica mode, mandatory in Download mode.

Example: `/opt/rucio/rucio_ca.pem`

#### App ID - `app_id`
Rucio App ID. Optional.

Example: `swan`

#### Site Name - `site_name`
Site name of the JupyterLab instance. Optional. Allows Rucio to determine whether to serve a proxied PFN or not.

Example: `ATLAS`

### Virtual Organizations

#### VO Name - `vo`
VO (Virtual Organization) of the instance. Optional, for use in multi-VO installations only. If VOMS is enabled, this value will be supplied as `--voms` option when invoking `voms-proxy-init`.

Example: `def`

#### VOMS Enabled - `voms_enabled`
Boolean flag to enable VOMS proxy certificate generation. When set to `true`, the extension uses `voms-proxy-init` to generate a proxy certificate for authenticated RSE access.

Default: `false`

#### VOMS `certdir` Path - `voms_certdir_path`
If VOMS is enabled, sets the `--certdir` option for `voms-proxy-init`. Refer to `voms-proxy-init` documentation.

Example: `/etc/grid-security/certificates`

#### VOMS `vomses` Path - `voms_vomses_path`
If VOMS is enabled, sets the `--vomses` option for `voms-proxy-init`. Refer to `voms-proxy-init` documentation.

Example: `/etc/grid-security/vomses`

**WARNING:** Earlier versions of `voms-proxy-init` do not support the `--vomses` option. In that case, this option must be omitted.

### Storage Elements and Search

#### Destination RSE - `destination_rse`
The name of the Rucio Storage Element mounted to the JupyterLab server. Mandatory in Replica mode.

Example: `SWAN-EOS`

#### RSE Mount Path - `rse_mount_path`
The base path where the RSE is mounted to the server. Mandatory in Replica mode.

Example: `/eos/rucio`

#### File Path Starting Index - `path_begins_at`
This configuration indicates which part of the PFN (Physical File Name) should be appended to the mount path. Only applicable in Replica mode. Defaults to `0`.

**Example:** For a PFN of `root://xrd1:1094//rucio/test/49/ad/f1.txt` and mount path `/eos/rucio`:
- `path_begins_at: 1` means start from the 2nd slash in the PFN
- Resulting path: `/eos/rucio/test/49/ad/f1.txt`

#### Replication Rule Lifetime (in days) - `replication_rule_lifetime_days`
Replication rule lifetime in days. Optional, only applicable in Replica mode.

Example: `365`

#### Wildcard Search Enabled - `wildcard_enabled`
Boolean flag to enable wildcard DID (Dataset Identifier) search. When enabled, users can search using wildcard patterns like `scope:*`.

Default: `false`

### Authentication Configuration

#### OpenID Connect Auth Source - `oidc_auth`
Specifies where the extension retrieves the OIDC token. Optional.

Allowed values:
- `file`: Read token from a file
- `env`: Read token from an environment variable

#### OpenID Connect Token Filename - `oidc_file_name`
Specifies an absolute path to a file containing the OIDC access token. Required if `oidc_auth` is set to `file`.

Example: `/var/run/secrets/oidc_token`

#### OpenID Connect Token Environment Variable Name - `oidc_env_name`
Specifies the environment variable name containing the OIDC access token. Required if `oidc_auth` is set to `env`.

Example: `RUCIO_ACCESS_TOKEN`

**IMPORTANT:** The `oidc_auth` parameter and either `oidc_file_name` or `oidc_env_name` are necessary if OIDC token authentication is to be used.

### Global Configuration

#### Default Instance - `default_instance`
The instance to be pre-selected in the settings menu of the extension.

Example: `atlas.cern.ch`

#### Default Authentication Type - `default_auth_type`
Default authentication method. Possible values:
- `oidc`: OpenID Connect tokens
- `x509`: X.509 user certificate
- `x509_proxy`: X.509 proxy certificate
- `userpass`: Username and password

#### Logging Level - `log_level`
Specifies the verbosity of logs. Possible values:
- `debug`: Most verbose
- `info`: Informational messages
- `warning`: Warnings and errors
- `error`: Errors only

## IPython Kernel Extension

To allow users to access file paths from within notebooks, the kernel extension must be enabled.

### Manual Activation

To enable the kernel extension inside a notebook, use the IPython magic:

```python
%load_ext rucio_jupyterlab.kernels.ipython
```

### Automatic Activation

To enable it by default for all users, add the following to the IPython configuration (e.g., `~/.ipython/profile_default/ipython_kernel_config.py`):

```python
c.IPKernelApp.extensions = ['rucio_jupyterlab.kernels.ipython']
```

## OpenID Connect Authentication Setup

OIDC authentication requires special configuration at the operator level, as it cannot be configured by users directly.

### Important Notes

- Users will only see the "OpenID Connect" authentication option if OIDC is properly configured by operators
- The extension does not handle user authentication directly; the OIDC token must be obtained through an external mechanism
- In multi-user setups with JupyterHub, operators must make the OIDC token accessible via file or environment variable
- JupyterHub must implement periodic token refresh to prevent expiration during active sessions

### Configuring JupyterHub with OIDC

#### Single User Dockerfile and Variables

The single-user container image must include:
1. The Rucio JupyterLab extension installed
2. OIDC token environment variables properly configured
3. A configuration script (like `configure.py`) to write environment variables to Jupyter configuration

#### JupyterHub Helm Chart Configuration

For Kubernetes deployments using the [Zero to JupyterHub](https://z2jh.jupyter.org/en/stable/) Helm Chart:

**1. Set the custom single-user image:**

```yaml
singleuser:
  image: <image-url>:<image-tag>
```

**2. Add a custom authenticator to `hub.extraConfig`:**

The `hub.extraConfig` section allows you to inject custom Python code into the JupyterHub configuration. Here, we define a custom authenticator class that handles OIDC token exchange with Rucio. This authenticator intercepts the user authentication flow, exchanges the OIDC token for a Rucio-specific token, and injects it into the spawned user environment.

See an example implementation in the [ESCAPE VRE Helm Chart](https://github.com/vre-hub/vre/blob/527982d0a9beeb6098dbb9f73e16ff65f4796b88/infrastructure/cluster/flux/jhub/jhub-release.yaml#L71).


**3. Add authenticator configuration to `hub.config`:**

The `hub.config` section configures the custom `RucioAuthenticator` class defined above. These settings specify the OIDC provider endpoints and client credentials needed for authentication. The authenticator uses these values to communicate with your identity provider and perform token exchanges.

See configuration example in the [ESCAPE VRE Helm Chart](https://github.com/vre-hub/vre/blob/527982d0a9beeb6098dbb9f73e16ff65f4796b88/infrastructure/cluster/flux/jhub/jhub-release.yaml#L55).

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

**4. Add extension parameters to `singleuser.extraEnv`:**

The `singleuser.extraEnv` section defines environment variables that will be injected into each user's JupyterLab pod. The Rucio JupyterLab extension reads these variables to configure itself automatically. This approach is particularly useful in containerized environments where configuration via environment variables is preferred over static configuration files.

See environment configuration in the [ESCAPE VRE Helm Chart](https://github.com/vre-hub/vre/blob/527982d0a9beeb6098dbb9f73e16ff65f4796b88/infrastructure/cluster/flux/jhub/jhub-release.yaml#L211).

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
    RUCIO_OAUTH_ID: "<your-rucio-oauth-id>"
    RUCIO_DEFAULT_INSTANCE: "<your-rucio-instance-name>"
    RUCIO_DESTINATION_RSE: "EOS RSE"
    RUCIO_RSE_MOUNT_PATH: "/eos/eos-rse"
    RUCIO_PATH_BEGINS_AT: "4"
    RUCIO_CA_CERT: "<your-rucio-ca-file-path>"
    OAUTH2_TOKEN: "FILE:/tmp/eos_oauth.token"
```

**5. Build the Docker image and install the Helm Chart with the specified values.**

*Note: This configuration works in replica mode and maps an EOS RSE as the target RSE, FUSE mounted on the JupyterHub nodes.*

