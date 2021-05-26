from pyri.plugins.service_node_launch import ServiceNodeLaunch, PyriServiceNodeLaunchFactory

def _var_storage_add_args(arg_parser):
    parser_group = arg_parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument("--db-file", type=str,default=None,help="Variable database filename")
    parser_group.add_argument("--db-url", type=str,default=None,help="SQLAlchemy connections string (use --db-file for SQLite)")

def _var_storage_prepare_args(arg_results):
    args = []
    if arg_results.db_file is not None:
        args.append(f"--db-file={arg_results.db_file}")
    if arg_results.db_url is not None:
        args.append(f"--db-url={arg_results.db_url}")
    return args


launches = [
    ServiceNodeLaunch("variable_storage", "pyri.variable_storage", "pyri.variable_storage", \
        _var_storage_add_args,_var_storage_prepare_args,[],default_devices=[("pyri_variable_storage","variable_storage")])
]

class VariableStorageLaunchFactory(PyriServiceNodeLaunchFactory):
    def get_plugin_name(self):
        return "pyri.variable_storage"

    def get_service_node_launch_names(self):
        return ["variable_storage"]

    def get_service_node_launches(self):
        return launches

def get_service_node_launch_factory():
    return VariableStorageLaunchFactory()

        
