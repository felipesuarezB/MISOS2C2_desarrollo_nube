from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from database import db


class Usuario(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  usuario = Column(String(50), nullable=False, unique=True)
  contrasena = Column(String(50), nullable=False)
  rol = Column(Integer(), nullable=False)
  fecha_creacion = Column(DateTime(), nullable=False, default=datetime.now)


class RolUsuario(Enum):
  ADMINISTRADOR_GIMNASIO = 1
  ENTRENADOR = 2
  PERSONA = 3


class UsuarioJsonSchema(Schema):
  id = fields.String()
  usuario = fields.String()
  contrasena = fields.String()
  rol = fields.Int()


class UpdatePasswordJsonSchema(Schema):
  usuario = fields.String()
  contrasena_actual = fields.String()
  contrasena_nueva = fields.String()
