from pyri.variable_storage.storage import VariableStorageDB
import RobotRaconteur as RR
import RobotRaconteurCompanion as RRC
from pyri.plugins import robdef as robdef_plugins

def test_init_db():
    node = RR.RobotRaconteurNode()
    node.Init(1)

    RRC.RegisterStdRobDefServiceTypes(node)
    robdef_plugins.register_all_plugin_robdefs(node)

    db = VariableStorageDB('sqlite:///:memory:', node = node)