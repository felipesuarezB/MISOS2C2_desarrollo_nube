from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from database import db


class Entrenador(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  nombre = Column(String(128), nullable=False)
  apellido = Column(String(128), nullable=False)
  id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuario.id'), nullable=False)


class EntrenadorJsonSchema(Schema):
  id = fields.String(attribute='id')
  nombre = fields.String(attribute='nombre')
  apellido = fields.String(attribute='apellido')
  id_usuario = fields.String(attribute='id_usuario')
