from pyri.plugins.factory import PyriPluginFactory
from pyri.plugins.types import PyriPluginInfo


class PyriVariablesPluginFactory(PyriPluginFactory):
    
    def get_info(self):
        return PyriPluginInfo("pyri.variables")

def get_factory():
    return PyriVariablesPluginFactory()