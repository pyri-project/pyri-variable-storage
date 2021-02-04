import RobotRaconteur as RR
import RobotRaconteurCompanion as RRC
from pyri.plugins import robdef as robdef_plugins
from pyri.variable_storage.storage import VariableStorageDB

import pytest

def test_storage_object_basic():
    node = RR.RobotRaconteurNode()
    node.Init(1)

    RRC.RegisterStdRobDefServiceTypes(node)
    robdef_plugins.register_all_plugin_robdefs(node)

    db = VariableStorageDB('sqlite:///:memory:', node = node)

    _run_test_on_db(node,None,db)

def test_storage_object_rr():
    node = RR.RobotRaconteurNode.s
    
    #node._SetNodeName("test_variable_db")
    #node.Init()
    #node.SetLogLevelFromString("TRACE")

    RRC.RegisterStdRobDefServiceTypes(node)
    robdef_plugins.register_all_plugin_robdefs(node)

    

    node_transport = RR.LocalTransport()
    node.RegisterTransport(node_transport)
    node_transport.StartServerAsNodeName("test_variable_db")
    db = VariableStorageDB('sqlite:///C:/Users/user/Documents/pyri/software/testdb.db?check_same_thread=False', node = node)
    node.RegisterService("db","tech.pyri.variable_storage.VariableStorage",db)

    #client_node = RR.RobotRaconteurNode()
    #client_node.Init()
    #client_node.SetLogLevelFromString("TRACE")

    #client_node_transport = RR.LocalTransport()
    #client_node.RegisterTransport(client_node_transport)
    
    client_db = node.ConnectService('rr+local:///?nodename=test_variable_db&service=db')


    _run_test_on_db(node,client_db,client_db)

def _run_test_on_db(node,obj,db : VariableStorageDB):

    storage_consts = node.GetConstants("tech.pyri.variable_storage",obj)
    variable_persistence = storage_consts["VariablePersistence"]
    variable_protection_level = storage_consts["VariableProtectionLevel"]
    variable_user_permission = node.GetStructureType("tech.pyri.variable_storage.VariableUserPermission",obj)
    variable_group_permission = node.GetStructureType("tech.pyri.variable_storage.VariableGroupPermission",obj)

    # Test add_variable and add_variable2
    db.add_variable("test_device1", "test_var1", "string", RR.VarValue("This is a test string","string"), ["tag1", "tag2"])
    with pytest.raises(RR.InvalidOperationException):
        db.add_variable("test_device1", "test_var1", "string", RR.VarValue("This is a test string","string"), ["tag1", "tag2"])

    db.add_variable("test_device2", "test_var1", "string", RR.VarValue("1342543","string"), ["tag1", "tag7", "tag9"])

    test_var2_perms = []
    test_var2_perms_1 = variable_user_permission()
    test_var2_perms_1.username = "testuser1"
    test_var2_perms_1.permission = variable_protection_level["private"]
    test_var2_perms.append(RR.VarValue(test_var2_perms_1,"tech.pyri.variable_storage.VariableUserPermission"))
    test_var2_perms_2 = variable_group_permission()
    test_var2_perms_2.groupname = "testgroup1"
    test_var2_perms_2.permission = variable_protection_level["read_only"]
    test_var2_perms.append(RR.VarValue(test_var2_perms_2,"tech.pyri.variable_storage.VariableGroupPermission"))

    db.add_variable2("test_device1", "test_var2", "string", RR.VarValue("This is another test string","string"), ["tag3", "tag2"], \
        {"attr1": "some_value1", "attr2": "some_value2"}, variable_persistence["persistent"], RR.VarValue("This has been reset!","string"), \
        variable_protection_level["read_write"], test_var2_perms, True)

    # Test filter_variables

    filter_res = db.filter_variables("test_device1", "^test_var[0-9]+$", ["tag1", "tag2"])

    assert set(filter_res) == set(["test_var1", "test_var2"])

    # Test getf_device_names
    device_names = db.getf_device_names()
    assert set(device_names) == set(["test_device1", "test_device2"])

    # Test getf_variable_names
    var_names = db.getf_variable_names("test_device1")
    assert set(var_names) == set(["test_var1", "test_var2"])

    # Test getf_variable_value
    test_var1 = db.getf_variable_value("test_device1", "test_var1")
    assert test_var1.data == "This is a test string"
    assert test_var1.datatype == "string"

    # Test setf_variable_value
    db.setf_variable_value("test_device1", "test_var1", RR.VarValue("This is a different test string!","string"))
    test_var1_2 = db.getf_variable_value("test_device1", "test_var1")
    assert test_var1_2.data == "This is a different test string!"
    assert test_var1_2.datatype == "string"

    # Test getf_variable_reset_value
    test_var2_reset = db.getf_variable_reset_value("test_device1", "test_var2")
    assert test_var2_reset.data == "This has been reset!"
    assert test_var2_reset.datatype == "string"

    # Test setf_variable_reset_value
    db.setf_variable_reset_value("test_device1", "test_var2", RR.VarValue("This is a different reset!","string"))
    test_var2_reset_2 = db.getf_variable_reset_value("test_device1", "test_var2")
    assert test_var2_reset_2.data == "This is a different reset!"
    assert test_var2_reset_2.datatype == "string"

    # Test getf_variable_tags
    test_var1_tags = db.getf_variable_tags("test_device1", "test_var1")
    assert set(test_var1_tags) == set(["tag1", "tag2"])

    # Test add_variable_tags
    db.add_variable_tags("test_device1", "test_var1", ["tag11", "tag12", "tag13", "tag1"])
    test_var1_tags_2 = db.getf_variable_tags("test_device1", "test_var1")
    assert set(test_var1_tags_2) == set(["tag1", "tag2", "tag11", "tag12", "tag13"])

    # Test list_all_tags
    all_tags = db.list_all_tags()
    assert set(all_tags) == set(["tag1", "tag2", "tag3", "tag7", "tag9", "tag11", "tag12", "tag13"])
    
    # Test remove_variable_tags
    db.remove_variable_tags("test_device1", "test_var1", ["tag1","tag12"])
    test_var1_tags_3 = db.getf_variable_tags("test_device1", "test_var1")
    assert set(test_var1_tags_3) == set(["tag2", "tag11", "tag13"])

    # Test clear_variable_tags
    db.clear_variable_tags("test_device1", "test_var1")
    test_var1_tags_4 = db.getf_variable_tags("test_device1", "test_var1")
    assert len(test_var1_tags_4) == 0

    # Test getf_variable_attributes
    test_var1_attrs = db.getf_variable_attributes("test_device1", "test_var2")
    assert len(test_var1_attrs) == 2
    assert test_var1_attrs["attr1"] == "some_value1"
    assert test_var1_attrs["attr2"] == "some_value2"

    # Test add_variable_attribute
    db.add_variable_attribute("test_device1", "test_var2", "attr3", "some_value3")
    test_var1_attrs_2 = db.getf_variable_attributes("test_device1", "test_var2")
    assert len(test_var1_attrs_2) == 3
    assert test_var1_attrs_2["attr1"] == "some_value1"
    assert test_var1_attrs_2["attr2"] == "some_value2"
    assert test_var1_attrs_2["attr3"] == "some_value3"

    # Test remove_variable_attribute
    db.remove_variable_attribute("test_device1", "test_var2", "attr2")
    test_var1_attrs_3 = db.getf_variable_attributes("test_device1", "test_var2")
    assert len(test_var1_attrs_3) == 2
    assert test_var1_attrs_3["attr1"] == "some_value1"
    assert test_var1_attrs_3["attr3"] == "some_value3"

    # Test clear_variable_attributes
    db.clear_variable_attributes("test_device1", "test_var2")
    test_var1_attrs_4 = db.getf_variable_attributes("test_device1", "test_var2")
    assert len(test_var1_attrs_4) == 0

    # Test delete_variable
    db.delete_variable("test_device1", "test_var1")
    var_names_2 = db.getf_variable_names("test_device1")
    assert set(var_names_2) == set(["test_var2"])

    # Test delete_device
    db.delete_device("test_device1")
    device_names_2 = db.getf_device_names()
    assert set(device_names_2) == set(["test_device2"])