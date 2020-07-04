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
In this mode, the extension downloads the files to the user directory. This is used when your JupyterLab installation does not use a storage as an RSE.
**TODO do this**

## Configuration
The extension can be configured locally or remotely.

### Local Configuration
In your Jupyter configuration (could be `~/.jupyter/jupyter_notebook_config.json`), add the following snippet:
```json
{
    ...,
    "RucioConfig": {
        "instances": [
            {
                "name": "experiment.cern.ch",
                "display_name": "Experiment",
                "rucio_base_url": "https://rucio",
                "destination_rse": "SWAN-EOS",
                "rse_mount_path": "/eos/rucio",
                "path_begins_at": 4,
                "mode": "replica"
            },
            ...
        ]
    }
}
```

### Remote Configuration
To use remote configuration, use the following snippet:
```json
{
    ...,
    "RucioConfig": {
        "instances": [
            {
                "name": "experiment.cern.ch",
                "display_name": "Experiment",
                "$url": "https://url-to-rucio-configuration/config.json"
            },
            ...
        ]
    }
}
```

In the JSON file pointed by the value in `$url`, use the following snippet:
```json
{
    "rucio_base_url": "https://rucio",
    "destination_rse": "SWAN-EOS",
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

#### Destination RSE - `destination_rse`
The name of the Rucio Storage Element that is mounted to the JupyterLab server. Only applicable in Replica mode.

Example: `SWAN-EOS`

#### RSE Mount Path - `rse_mount_path`
The base path in which the RSE is mounted to the server. Only applicable in Replica mode.

Example: `/eos/rucio`

#### File Path Starting Index - `path_begins_at`
This configuration indicates which part of the PFN should be appended to the mount path. Only applicable in Replica mode.

Example: let us say that the PFN of a file is `root://xrd1:1094//rucio/test/49/ad/f1.txt` and the mount path is `/eos/rucio`. A starting index of `1` means that the path starting from the 2nd slash (index 1) in the PFN will be appended to the mount path. The resulting path would be `/eos/rucio/test/49/ad/f1.txt`.


## IPython Kernel
To allow users to access the paths from within the notebook, a kernel extension must be enabled. The kernel resides in module `rucio_jupyterlab.kernels.ipython`.

To enable the extension, use `load_ext` IPython magic:

```py
%load_ext rucio_jupyterlab.kernels.ipython
```

Or, if you want to enable it by default, put the following snippet in your Jupyter configuration (could be `~/.jupyter/jupyter_notebook_config.json`).

```json
{
    ...,
    "IPKernelApp": {
        "extensions": [
            "rucio_jupyterlab.kernels.ipython"
        ]
    }
}
```