<p align="center">
<img src="./doc/figures/pyri_logo_web.svg" height="200"/>
</p>

# PyRI Open Source Teach Pendant Variable Storage

This package is part of the PyRI project. See https://github.com/pyri-project/pyri-core#documentation for documentation. This package is included in the `pyri-robotics-superpack` Conda package.

The `pyri-variable-storage` package contains an SQL database Robot Raconteur node that is used to store all data, procedures, parameters, and state information for the system. The rest of the system is designed to be "stateless", with all state data stored within the variable storage database. This allows for other components in the system to be restarted without affecting the operation of the teach pendant itself. 

## Service

This service is started automatically by `pyri-core`, and does not normally need to be started manually.

Standalone service command line example:

```
pyri-variable-storage-service --db-file=my_program.db
```

This command uses the SQLite database provider, storing all user program data in a single file:

The variable storage node does not require any other services to be running to start.

Command line options:

| Option | Type | Required | Description |
| ---    | ---  | ---      | ---         |
| `--db-file=` | File | Either `--db-file` or `--db-url` | The file to store the user database in using SQLite format |
| `--db-url=`  | SQLAlchemy URL | Either `--db-file` or `--db-url` | The SQLAlchemy URL of the database to use |
| `--device-info-file=` | File | No | Robot Raconteur `DeviceInfo` YAML file. Defaults to contents of `pyri_variable_storage_default_info.yml` |

This service may use any standard `--robotraconteur-*` service node options.

This service adds the `--db-file=` and `--db-url=` options to `pyri-core`.

## Acknowledgment

This work was supported in part by Subaward No. ARM-TEC-19-01-F-24 from the Advanced Robotics for Manufacturing ("ARM") Institute under Agreement Number W911NF-17-3-0004 sponsored by the Office of the Secretary of Defense. ARM Project Management was provided by Christopher Adams. The views and conclusions contained in this document are those of the authors and should not be interpreted as representing the official policies, either expressed or implied, of either ARM or the Office of the Secretary of Defense of the U.S. Government. The U.S. Government is authorized to reproduce and distribute reprints for Government purposes, notwithstanding any copyright notation herein.

This work was supported in part by the New York State Empire State Development Division of Science, Technology and Innovation (NYSTAR) under contract C160142. 

![](doc/figures/arm_logo.jpg) ![](doc/figures/nys_logo.jpg)

PyRI is developed by Rensselaer Polytechnic Institute, Wason Technology, LLC, and contributors.
