from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from database import db


class Ejercicio(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  nombre = Column(String(128), nullable=False)
  descripcion = Column(String(512))
  link_video = Column(String(512))
  calorias_por_repeticion = Column(Integer())


class EjercicioJsonSchema(Schema):
  id = fields.String(attribute='id')
  nombre = fields.String(attribute='nombre')
  descripcion = fields.String(attribute='descripcion')
  link_video = fields.String(attribute='link_video')
  calorias_por_repeticion = fields.Int(attribute='calorias_por_repeticion')
