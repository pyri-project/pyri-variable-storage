from sqlalchemy import Table, Column, Integer, Numeric, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from enum import IntEnum
from datetime import datetime

from sqlalchemy.sql.schema import UniqueConstraint

Base = declarative_base()

class VariablePersistence(IntEnum):
    TEMPORARY = 0
    NORMAL = 1
    PERSISTENT = 2
    CONST = 3

class VariableProtectionLevel(IntEnum):
    PRIVATE = 0
    READ_ONLY = 1
    READ_WRITE = 2

class Variable(Base):
    __tablename__ = "pyri_variables"
    __table_args__ = (UniqueConstraint('name','device',name='_unique_var'),)
    id = Column(Integer(), primary_key = True)
    name = Column(String(512), index = True)
    device = Column(String(128))
    datatype = Column(String(128))
    value = Column(LargeBinary())
    reset_value = Column(LargeBinary(), default = None)
    persistence = Column(Integer(), default = VariablePersistence.TEMPORARY)
    default_protection = Column(Integer(), default = VariableProtectionLevel.READ_WRITE)
    created_on = Column(LargeBinary()) # com.robotraconteur.datetime.TimeSpec2
    updated_on = Column(LargeBinary()) # com.robotraconteur.datetime.TimeSpec2

class VariableTag(Base):
    __tablename__ = "pyri_variables_tags"
    __table_args__ = (UniqueConstraint('variable_id','tag',name='_unique_tag'),)
    tag_id = Column(Integer(), primary_key = True)
    variable_id = Column(Integer(), ForeignKey('pyri_variables.id'))
    variable = relationship("Variable", backref=backref('tags', order_by = tag_id, cascade="all, delete-orphan"))
    tag = Column(String(128))

class VariableUserPermission(Base):
    __tablename__ = "pyri_variables_user_permissions"
    __table_args__ = (UniqueConstraint('variable_id','username',name='_unique_permission'),)
    permission_id = Column(Integer(), primary_key = True)
    variable_id = Column(Integer(), ForeignKey('pyri_variables.id'))
    variable = relationship("Variable", backref=backref('user_permissions', order_by = permission_id, cascade="all, delete-orphan"))
    username = Column(String(128))
    permission = Column(Integer())

class VariableGroupPermission(Base):
    __tablename__ = "pyri_variables_group_permissions"
    __table_args__ = (UniqueConstraint('variable_id','groupname',name='_unique_permission'),)
    permission_id = Column(Integer(), primary_key = True)
    variable_id = Column(Integer(), ForeignKey('pyri_variables.id'))
    variable = relationship("Variable", backref=backref('group_permissions', order_by = permission_id, cascade="all, delete-orphan"))
    groupname = Column(String(128))
    permission = Column(Integer())

class VariableAttribute(Base):
    __tablename__ = "pyri_variables_attributes"
    __table_args__ = (UniqueConstraint('variable_id','name',name='_unique_attribute'),)
    attribute_id = Column(Integer(), primary_key = True)
    variable_id = Column(Integer(), ForeignKey('pyri_variables.id'))
    variable = relationship("Variable", backref=backref('attributes', order_by = attribute_id, cascade="all, delete-orphan"))
    name = Column(String(128))
    value = Column(String(1024))