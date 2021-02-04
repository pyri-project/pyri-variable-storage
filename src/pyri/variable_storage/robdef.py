from RobotRaconteurCompanion.Util import RobDef as robdef_util

def get_variable_storage_robdef():
    return robdef_util.get_service_types_from_resources(__package__,["tech.pyri.variable_storage"])