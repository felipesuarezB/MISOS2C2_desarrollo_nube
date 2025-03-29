from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import uuid
from datetime import datetime
from enum import Enum

from database import db


class Rutina(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  nombre = Column(String(128), nullable=False)
  descripcion = Column(String(512))
  total_minutos = Column(Integer(), default=0)


class RutinaEjercicios(db.Model):
  id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
  id_rutina = Column(UUID(as_uuid=True), ForeignKey('rutina.id'), nullable=False)
  id_ejercicio = Column(UUID(as_uuid=True), ForeignKey('ejercicio.id'), nullable=False)
  repeticiones = Column(Integer(), nullable=False, default=1)


class RutinaEjercicioJsonSchema(Schema):
  id = fields.String(attribute='id')
  id_ejercicio = fields.String(attribute='id_ejercicio')
  nombre = fields.String(attribute='nombre')
  calorias_por_repeticion = fields.Integer(attribute='calorias_por_repeticion')
  repeticiones = fields.Integer(attribute='repeticiones')


class RutinaJsonSchema(Schema):
  id = fields.String(attribute='id')
  nombre = fields.String(attribute='nombre')
  descripcion = fields.String(attribute='descripcion')
  total_minutos = fields.Integer(attribute='total_minutos')
  lista_ejercicios = fields.List(fields.Nested(RutinaEjercicioJsonSchema()), attribute='lista_ejercicios')
