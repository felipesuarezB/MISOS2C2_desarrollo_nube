from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema

import uuid

from database import db

class Jugador(db.Model):
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password1 = Column(String(200), nullable=False)
    password2 = Column(String(200), nullable=False)
    ciudad = Column(String(50), nullable=False)
    pais = Column(String(50), nullable=False)
    username = Column(String(50), unique=False, nullable=False)
    
class JugadorSchema(Schema):
    id = fields.String(attribute='id')
    nombre = fields.String(attribute='nombre')
    apellido = fields.String(attribute='apellido')
    email = fields.String(attribute='email')
    password1 = fields.String(attribute='password1')
    password2 = fields.String(attribute='password2')
    ciudad = fields.String(attribute='ciudad')
    pais = fields.String(attribute='pais')
    username = fields.String(attribute='username')
    
class JugadorJsonSchema(Schema):
    username = fields.String(attribute='username', unique=True)
    password1 = fields.String(attribute='password1')
    password2 = fields.String(attribute='password2')

