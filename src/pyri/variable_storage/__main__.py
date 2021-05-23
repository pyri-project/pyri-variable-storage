import sys
import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
from .storage import VariableStorageDB
import argparse
from RobotRaconteurCompanion.Util.InfoFileLoader import InfoFileLoader
from RobotRaconteurCompanion.Util.AttributesUtil import AttributesUtil
from pyri.plugins import robdef as robdef_plugins
from pyri.util.service_setup import PyriServiceNodeSetup, PyriService_NodeSetup_Default_Flags

PyriService_VariableStorage_NodeSetup_Default_Flags = PyriService_NodeSetup_Default_Flags | RR.RobotRaconteurNodeSetupFlags_JUMBO_MESSAGE

def main():
    parser = argparse.ArgumentParser(description="PyRI Variable Storage Service Node")
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument("--db-file", type=str,default=None,help="Variable database filename")
    parser_group.add_argument("--db-url", type=str,default=None,help="SQLAlchemy connections string (use --db-file for SQLite)")
    args, _ = parser.parse_known_args()
        
    if args.db_file:
        db_url = f'sqlite:///{args.db_file}?check_same_thread=False'
    else:
        db_url = args.db_url

    db = VariableStorageDB(db_url, node = RRN)

    with PyriServiceNodeSetup("tech.pyri.variable_storage",59901, flags=PyriService_VariableStorage_NodeSetup_Default_Flags, \
        default_info = (__package__,"pyri_variable_storage_default_info.yml"), \
        arg_parser = parser, no_device_manager=True, register_plugin_robdef=True) as service_node_setup:

        extra_imports = RRN.GetRegisteredServiceTypes()
        db.device_info=service_node_setup.device_info_struct

        service_ctx = service_node_setup.register_service("variable_storage","tech.pyri.variable_storage.VariableStorage",db)
        for e in extra_imports:
            service_ctx.AddExtraImport(e)

        service_node_setup.wait_exit()        

        db.close()

if __name__ == "__main__":
    sys.exit(main() or 0)
