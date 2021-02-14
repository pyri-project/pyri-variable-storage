from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, Query
from sqlalchemy.orm import exc as orm_exc
from sqlalchemy import exc
from . import models
from typing import List, Any, Dict
import RobotRaconteur as RR
from RobotRaconteurCompanion.Util import DateTimeUtil as rr_datetime_util
import threading

from RobotRaconteur.RobotRaconteurPython import MessageElementToBytes, MessageElementFromBytes
from RobotRaconteur.RobotRaconteurPythonUtil import PackMessageElement, UnpackMessageElement


def _rr_varvalue_to_bytes(val, node):
    m = PackMessageElement(val, "varvalue", node=node)
    return MessageElementToBytes(m)

def _rr_varvalue_from_bytes(b, node):
    m = MessageElementFromBytes(b)
    return UnpackMessageElement(m, "varvalue", node=node)

class VariableStorageDB(object):
    def __init__(self, connect_string : str = 'sqlite:///:memory:', device_info = None, node : RR.RobotRaconteurNode = None):
        self._lock = threading.Lock()
        if node is None:
            self._node = RR.RobotRaconteurNode.s
        else:
            self._node = node
        self.device_info = device_info
        self._rr_user_permission = self._node.GetStructureType('tech.pyri.variable_storage.VariableUserPermission')
        self._rr_group_permission = self._node.GetStructureType('tech.pyri.variable_storage.VariableGroupPermission')
        self._variable_not_found = self._node.GetExceptionType('tech.pyri.variable_storage.VariableNotFound')
        self._variable_info = self._node.GetStructureType('tech.pyri.variable_storage.VariableInfo')

        self._datetime_util = rr_datetime_util.DateTimeUtil(self._node)
        
        self._engine = create_engine(connect_string)
        self._Session = sessionmaker(bind=self._engine)
        self._session : Session = self._Session()
        models.Base.metadata.create_all(self._engine)

    #TODO: Don't read all columns when not needed
    def getf_device_names(self) -> List[str]:
        with self._lock:
            query = self._session.query(models.Variable.device.distinct().label("device_name"))
            device_names = [row.device_name for row in query.all()]
            return device_names

    def getf_variable_names(self, device: str) -> List[str]:
        with self._lock:
            query = self._session.query(models.Variable.name.distinct().label("variable_name")).filter(models.Variable.device == device)
            variable_names = [row.variable_name for row in query.all()]
            return variable_names

    def getf_variable_info(self, device: str, name: str) -> "tech.pyri.variable_storage.VariableInfo":

        res = self._variable_info()
        with self._lock:
            var = self._query_variable(device, name)

            res.name = var.name
            res.device = var.device
            res.datatype = var.datatype
            res.persistence = var.persistence
            res.default_protection = var.default_protection
            res.created_on = var.created_on
            res.updated_on = var.updated_on
            res.tags = [t.tag for t in var.tags]
            res.attributes = {(a.name, a.value) for a in var.attributes}
            # TODO: permissions

        return res


    def add_variable(self, device: str, name: str, datatype: str, value: Any, tags: List[str]) -> None:

        assert name is not None and len(name) > 0
        assert device is not None and len(device) > 0
        
        ts_now = self._datetime_util.TimeSpec2Now() 

        with self._lock:
            try:
                var = models.Variable()
                var.name = name
                var.device = device
                var.datatype = datatype
                var.value = _rr_varvalue_to_bytes(value, self._node)
                if tags is not None:
                    for tag in tags:
                        model_tag = models.VariableTag()
                        model_tag.tag = tag
                        var.tags.append(model_tag)
                var.updated_on = ts_now   
                var.created_on = ts_now
                self._session.add(var)
                self._session.commit()
            except exc.IntegrityError as e:
                self._session.rollback()
                error_info = e.orig.args
                if len(error_info) > 0:
                    if error_info[0] == 'UNIQUE constraint failed: pyri_variables.name, pyri_variables.device':
                        raise RR.InvalidOperationException(f'Variable {name} already exists')
                raise
            except:
                self._session.rollback()
                raise

    def add_variable2(self, device: str, name: str, datatype: str, value: Any, tags: List[str], attributes: Dict[str,str], \
        persistence: int, reset_value: Any, default_protection: int, permissions: List[Any], doc: str, overwrite: bool) -> None:
        
        assert name is not None and len(name) > 0
        assert device is not None and len(device) > 0
        assert persistence >=0 and persistence <=3
        assert default_protection >= 0 and default_protection <= 2

        ts_now = self._datetime_util.TimeSpec2Now() 

        with self._lock:
            try:

                if overwrite:
                    self._session.query(models.Variable).filter(models.Variable.name==name, models.Variable.device==device).delete()

                var = models.Variable()
                var.name = name
                var.device = device
                var.datatype = datatype
                var.value = _rr_varvalue_to_bytes(value, self._node)
                if tags is not None:
                    for tag in tags:
                        model_tag = models.VariableTag()
                        model_tag.tag = tag
                        var.tags.append(model_tag)
                if attributes is not None:
                    for attribute in attributes.items():
                        model_attr = models.VariableAttribute()
                        model_attr.name, model_attr.value = attribute
                        var.attributes.append(model_attr)
                var.persistence = persistence
                var.reset_value = _rr_varvalue_to_bytes(reset_value,self._node)
                var.default_protection = default_protection
                if permissions is not None:
                    for p in permissions:
                        if p.datatype == "tech.pyri.variable_storage.VariableUserPermission":
                            model_user_permission = models.VariableUserPermission()
                            model_user_permission.username = p.data.username
                            model_user_permission.permission = p.data.permission
                            var.user_permissions.append(model_user_permission)
                        elif p.datatype == "tech.pyri.variable_storage.VariableGroupPermission":
                            model_group_permission = models.VariableGroupPermission()
                            model_group_permission.groupname = p.data.groupname
                            model_group_permission.permission = p.data.permission
                            var.group_permissions.append(model_group_permission)
                        else:
                            raise RR.InvalidArgumentException("permissions must be a list of VariableUserPermission or VariableGroupPermission")
                var.doc = doc
                var.created_on = ts_now
                var.updated_on = ts_now
                self._session.add(var)
                self._session.commit()
            except exc.IntegrityError as e:
                self._session.rollback()
                error_info = e.orig.args
                if len(error_info) > 0:
                    if error_info[0] == 'UNIQUE constraint failed: pyri_variables.name, pyri_variables.device':
                        raise RR.InvalidOperationException(f'Variable {name} already exists')
                raise
            except:
                self._session.rollback()
                raise


    def _query_variable(self, device: str, name: str) -> models.Variable:
        # CALL LOCKED!
        try:
            return self._session.query(models.Variable).filter(models.Variable.device == device, models.Variable.name == name).one()
        except orm_exc.NoResultFound:
            raise self._variable_not_found(f"Variable {device},{name} not found")

    def getf_variable_value(self, device: str, name: str) -> Any:
        
        with self._lock:            
            var = self._query_variable(device,name)
            return _rr_varvalue_from_bytes(var.value,self._node)

    def setf_variable_value(self, device: str, name: str, value: Any) -> None:        

        ts_now = self._datetime_util.TimeSpec2Now() 
        var = self._query_variable(device,name)
        try:
            var.value = _rr_varvalue_to_bytes(value, self._node)
            var.updated_on = ts_now
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def getf_variable_reset_value(self, device: str, name: str) -> Any:
        
        with self._lock:            
            var = self._query_variable(device,name)
            return _rr_varvalue_from_bytes(var.reset_value,self._node)

    def setf_variable_reset_value(self, device: str, name: str, value: Any) -> None:        
        with self._lock:
            ts_now = self._datetime_util.TimeSpec2Now() 
            var = self._query_variable(device,name)
            try:
                var.reset_value = _rr_varvalue_to_bytes(value,self._node)
                var.updated_on = ts_now
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def delete_variable(self, device: str, name: str) -> None:
        with self._lock:
            var = self._query_variable(device,name)
            try:
                self._session.delete(var)
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def delete_device(self, device: str) -> None:
        with self._lock:
            try:
                self._session.query(models.Variable).filter(models.Variable.device == device).delete()
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def filter_variables(self, device: str, name_regex: str, tags: List[str]) -> List[str]:
        with self._lock:
            query : Query = self._session.query(models.Variable.name.distinct().label("name")).outerjoin(models.VariableTag).filter(models.Variable.device == device)
            assert device is not None and len(device) > 0

            if name_regex is not None and len(name_regex) > 0:
                query = query.filter(models.Variable.name.regexp_match(name_regex))

            if tags is not None and len(tags) > 0:
                query = query.filter(models.VariableTag.tag.in_(tags))

            query_res = query.all()

            res = []
            for r in query_res:
                res.append(r.name)  

            return res

    def getf_variable_tags(self, device: str, name: str):
        with self._lock:
            query = self._session.query(models.VariableTag.tag.distinct().label("tag")).outerjoin(models.Variable).filter(models.Variable.device == device,models.Variable.name == name)
            all_tags = query.all()
            res = []
            for tag in all_tags:
                res.append(tag.tag)
            return res

    def add_variable_tags(self, device: str, name: str, tags: List[str]):

        assert len(tags) > 0
        with self._lock:
            
            #TODO: make this more efficient?
            var = self._query_variable(device,name)

            try:
                for tag in tags:
                    tag_found = False
                    for var_tag in var.tags:
                        if var_tag.tag == tag:
                            tag_found = True
                            break

                    if not tag_found:
                        new_var_tag = models.VariableTag()
                        new_var_tag.tag = tag
                        var.tags.append(new_var_tag)                
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def list_all_tags(self):
        with self._lock:
            query = self._session.query(models.VariableTag.tag.distinct().label("tag"))
            all_tags = query.all()
            res = []
            for tag in all_tags:
                res.append(tag.tag)
            return res

    def remove_variable_tags(self, device: str, name: str, tags: List[str]):
        
        assert len(tags) > 0
        with self._lock:
            try:
                var_id = self._session.query(models.Variable.id).filter(models.Variable.device == device, models.Variable.name == name).scalar()
                
                query : Query = self._session.query(models.VariableTag).filter(models.VariableTag.tag.in_(tags)).filter(models.VariableTag.variable_id == var_id)
                query.delete()
                                
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def clear_variable_tags(self, device: str, name: str):
        
        with self._lock:
            try:
                var_id = self._session.query(models.Variable.id).filter(models.Variable.device == device, models.Variable.name == name).scalar()
                
                query : Query = self._session.query(models.VariableTag).filter(models.VariableTag.variable_id == var_id)
                query.delete()
                                
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def getf_variable_attributes(self, device: str, name: str):
        with self._lock:
            var = self._query_variable(device, name)            
            res = dict()
            for attribute in var.attributes:
                res[attribute.name] = attribute.value
            return res

    def add_variable_attribute(self, device: str, name: str, attribute_name: str, attribute_value: str):

        assert len(attribute_name) > 0
        with self._lock:
            
            #TODO: make this more efficient?
            var = self._query_variable(device,name)

            try:
                model_attr = models.VariableAttribute()
                model_attr.name = attribute_name
                model_attr.value = attribute_value
                var.attributes.append(model_attr)            
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def remove_variable_attribute(self, device: str, name: str, attribute_name: str):
        
        assert len(attribute_name) > 0
        with self._lock:
            try:
                var_id = self._session.query(models.Variable.id).filter(models.Variable.device == device, models.Variable.name == name).scalar()
                
                query : Query = self._session.query(models.VariableAttribute).filter(models.VariableAttribute.name == attribute_name).filter(models.VariableAttribute.variable_id == var_id)
                query.delete()
                                
                self._session.commit()
            except:
                self._session.rollback()
                raise

    def clear_variable_attributes(self, device: str, name: str):
                
        with self._lock:
            try:
                var_id = self._session.query(models.Variable.id).filter(models.Variable.device == device, models.Variable.name == name).scalar()
                
                query : Query = self._session.query(models.VariableAttribute).filter(models.VariableAttribute.variable_id == var_id)
                query.delete()
                                
                self._session.commit()
            except:
                self._session.rollback()
                raise


    def getf_variable_permissions(self, device: str, name: str):
        raise RR.NotImplementedException("Permissions not implemented")

    def add_variable_permissions(self, device: str, name: str, permission):
        raise RR.NotImplementedException("Permissions not implemented")

    def remove_variable_permissions(self, device: str, name: str, permission):
        raise RR.NotImplementedException("Permissions not implemented")

    def clear_variable_permissions(self, device: str, name: str):
        raise RR.NotImplementedException("Permissions not implemented")

    def getf_variable_doc(self, device, name):
        with self._lock:            
            var = self._query_variable(device,name)
            return var.doc

    def setf_variable_doc(self, device, name, doc):
        var = self._query_variable(device,name)
        try:
            var.doc = doc            
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def close(self):
        with self._lock:
            if self._session is not None:
                self._session.close()