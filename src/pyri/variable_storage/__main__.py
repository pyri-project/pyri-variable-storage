import sys
import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
from .storage import VariableStorageDB
import argparse
from RobotRaconteurCompanion.Util.InfoFileLoader import InfoFileLoader
from RobotRaconteurCompanion.Util.AttributesUtil import AttributesUtil
from pyri.plugins import robdef as robdef_plugins
from pyri.util.robotraconteur import add_default_ws_origins

def main():
    parser = argparse.ArgumentParser(description="PyRI Variable Storage Service Node")
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument("--db-file", type=str,default=None,help="Variable database filename")
    parser_group.add_argument("--db-url", type=str,default=None,help="SQLAlchemy connections string (use --db-file for SQLite)")
    parser.add_argument("--device-info-file", type=argparse.FileType('r'),default=None,required=True,help="Device info file for variable storage service (required)")
    parser.add_argument("--wait-signal",action='store_const',const=True,default=False, help="wait for SIGTERM orSIGINT (Linux only)")
    parser.add_argument("--pyri-webui-server-port",type=int,default=8000,help="The PyRI WebUI port for websocket origin (default 8000)")
    
    args, _ = parser.parse_known_args()

    rr_args = ["--robotraconteur-jumbo-message=true"] + sys.argv

    RRC.RegisterStdRobDefServiceTypes(RRN)
    robdef_plugins.register_all_plugin_robdefs(RRN)

    with args.device_info_file:
        device_info_text = args.device_info_file.read()

    info_loader = InfoFileLoader(RRN)
    device_info, device_ident_fd = info_loader.LoadInfoFileFromString(device_info_text, "com.robotraconteur.device.DeviceInfo", "device")

    attributes_util = AttributesUtil(RRN)
    device_attributes = attributes_util.GetDefaultServiceAttributesFromDeviceInfo(device_info)

    if args.db_file:
        db_url = f'sqlite:///{args.db_file}?check_same_thread=False'
    else:
        db_url = args.db_url

    db = VariableStorageDB(db_url, device_info=device_info, node = RRN)

    extra_imports = RRN.GetRegisteredServiceTypes()

    with RR.ServerNodeSetup("tech.pyri.variable_storage",59901,argv=rr_args) as node_setup:

        add_default_ws_origins(node_setup.tcp_transport,args.pyri_webui_server_port)

        service_ctx = RRN.RegisterService("variable_storage","tech.pyri.variable_storage.VariableStorage",db)
        service_ctx.SetServiceAttributes(device_attributes)
        for e in extra_imports:
            service_ctx.AddExtraImport(e)

        if args.wait_signal:  
            #Wait for shutdown signal if running in service mode          
            print("Press Ctrl-C to quit...")
            import signal
            signal.sigwait([signal.SIGTERM,signal.SIGINT])
        else:
            #Wait for the user to shutdown the service
            if (sys.version_info > (3, 0)):
                input("Server started, press enter to quit...")
            else:
                raw_input("Server started, press enter to quit...")

        db.close()

if __name__ == "__main__":
    sys.exit(main() or 0)
