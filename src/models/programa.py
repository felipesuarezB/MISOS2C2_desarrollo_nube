from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from models.rutina import RutinaJsonSchema

from database import db


class Programa(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  nombre = Column(String(128), nullable=False)
  descripcion = Column(String(512))
  dias_programa = Column(Integer(), default=0)


class ProgramaRutinas(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  id_programa = Column(UUID(as_uuid=True), ForeignKey('programa.id'), nullable=False)
  id_rutina = Column(UUID(as_uuid=True), ForeignKey('rutina.id'), nullable=False)


class ProgramaJsonSchema(Schema):
  id = fields.String(attribute='id')
  nombre = fields.String(attribute='nombre')
  descripcion = fields.String(attribute='descripcion')
  dias_programa = fields.Integer(attribute='dias_programa')
  lista_rutinas_por_dia = fields.List(fields.Nested(RutinaJsonSchema()), attribute='lista_rutinas_por_dia')
