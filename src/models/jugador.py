from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validates, ValidationError
from database import db

db = SQLAlchemy()

class Jugador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    pais = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    
class JugadorSchema(Schema):
    nombre = fields.Str(required=True)
    apellido = fields.Str(required=True)
    email = fields.Email(required=True)
    password1 = fields.Str(required=True)
    password2 = fields.Str(required=True)
    ciudad = fields.Str(required=True)
    pais = fields.Str(required=True)
    username = fields.Str(required=True)

    @validates("email")
    def validate_email(self, value):
        if Jugador.query.filter_by(email=value).first():
            raise ValidationError("El email ya está registrado.")

    @validates("password2")
    def validate_password(self, value, **kwargs):
        if kwargs.get("password1") and kwargs["password1"] != value:
            raise ValidationError("Las contraseñas no coinciden.")