from typing import List
from RobotRaconteurCompanion.Util import RobDef as robdef_util
from pyri.plugins.robdef import PyriRobDefPluginFactory

class VariableStorageRobDefPluginFactory(PyriRobDefPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self):
        return "pyri-variable-storage"

    def get_robdef_names(self) -> List[str]:
        return ["tech.pyri.variable_storage"]

    def  get_robdefs(self) -> List[str]:
        return get_variable_storage_robdef()

def get_robdef_factory():
    return VariableStorageRobDefPluginFactory()

def get_variable_storage_robdef():
    return robdef_util.get_service_types_from_resources(__package__,["tech.pyri.variable_storage"])