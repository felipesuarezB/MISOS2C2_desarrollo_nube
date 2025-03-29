from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from database import db


class Persona(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  dni = Column(String(128), nullable=False)
  nombre = Column(String(128), nullable=False)
  apellido = Column(String(128), nullable=False)
  fecha_nacimiento = Column(DateTime, nullable=False)
  fecha_ingreso = Column(DateTime, nullable=False)
  talla = Column(Integer)
  peso = Column(Integer)
  medida_brazo = Column(Integer)
  medida_pecho = Column(Integer)
  medida_cintura = Column(Integer)
  medida_pierna = Column(Integer)
  id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuario.id'), nullable=False)


class PersonaJsonSchema(Schema):
  id = fields.String(attribute='id')
  dni = fields.String(attribute='dni')
  nombre = fields.String(attribute='nombre')
  apellido = fields.String(attribute='apellido')
  fecha_nacimiento = fields.String(attribute='fecha_nacimiento')
  fecha_ingreso = fields.String(attribute='fecha_ingreso')
  talla = fields.Int(attribute='talla')
  peso = fields.Int(attribute='peso')
  medida_brazo = fields.Int(attribute='medida_brazo')
  medida_pecho = fields.Int(attribute='medida_pecho')
  medida_cintura = fields.Int(attribute='medida_cintura')
  medida_pierna = fields.Int(attribute='medida_pierna')
  id_usuario = fields.String(attribute='id_usuario')
