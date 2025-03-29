from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from database import db


class GrupoPersonas(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  id_entrenador = Column(UUID(as_uuid=True), ForeignKey('entrenador.id'), nullable=False)
  id_persona = Column(UUID(as_uuid=True), ForeignKey('persona.id'), nullable=False)


class GrupoPersonasJsonSchema(Schema):
  id = fields.String(attribute='id')
  dni = fields.String(attribute='dni')
  nombre = fields.String(attribute='nombre')
  apellido = fields.String(attribute='apellido')
  id_entrenador = fields.String(attribute='id_entrenador')


class RegistroCambioGrupo(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  id_entrenador = Column(UUID(as_uuid=True), ForeignKey('entrenador.id'), nullable=False)
  id_persona = Column(UUID(as_uuid=True), ForeignKey('persona.id'), nullable=False)
  fecha_cambio = Column(DateTime, nullable=False)
  razon_cambio = Column(String(200), nullable=False)


class RegistroCambioGrupoJsonSchema(Schema):
  fecha_cambio = fields.String(attribute='fecha_cambio')
  razon_cambio = fields.String(attribute='razon_cambio')
