# PyRI Open Source Teach Pendant Variable Storage

The `pyri-variable-storage` package contains an SQL database Robot Raconteur node that is used to store all data, procedures, parameters, and state information for the system. The rest of the system is designed to be "stateless", with all state data stored within the variable storage database. This allows for other components in the system to be restarted without affecting the operation of the teach pendant itself. 

## Setup

The `pyri-variable-storage` package should be installed into a virtual environment using the command:

```
python3 -m pip install -e .
```

See https://github.com/pyri-project/pyri-core for more information on setting up the virtual environment.

## Startup

The variable storage node does not require any other services to be running to start. The following is the default command to run the database using the SQLite database provider, storing all data in a single file:

```
pyri-variable-storage-service --db-file=my_program.db --device-info-file=config/pyri_variable_storage_default_info.yml --robotraconteur-tcp-ipv4-discovery=true
```

## Variable Fields

Each variable contains the following fields:

| Field name | Field type | Description |
| ---        | ---        | ---         |
| name       | String(512) | Name of the variable |
| device     | String(128) | Name of the device that owns the variable |
| datatype  | String(128) | Robot Raconteur data type string |
| value      | LargeBinary | The data serialized as a Robot Raconteur message element |
| reset_value | LargeBinary | The reset value serialized as a Robot Raconteur message element |
| persistence | Integer | The persistence of the variable to reboots and resets |
| default_protection | Integer | The default protection level of the variable |
| doc | Text() | Documentation for the variable |
| created_on | LargeBinary | Robot Raconteur serialized time stamp |
| updated_on | LargeBinary | Robot Raconteur serialized time stamp |
| tags       | string array | Tags to describe the category and usage of variable |
| attributes | string dict | Key value string pairs for general purpose metadata |
| permissions | | User and group access permissions |



## Robot Raconteur type storage

The variable storage service needs to have the robdef types registered to store them in the database. Any types registered using a `pyri.plugins.robdef` plugin will automatically be registered.