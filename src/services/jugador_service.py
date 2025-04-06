from datetime import timedelta
import hashlib
from flask import jsonify
from api_messages.api_jugadores import JugadorCreado, JugadoresList
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams, ForbiddenOperation
from api_messages.api_jugadores import UserAlreadyExists, UserAuthFailed, UserAuthSucceed
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models.jugador import JugadorSchema, Jugador
from database import db

def generate_new_token(user_id):
    token = create_access_token(user_id,expires_delta=timedelta(seconds=3600))
    return token

class JugadorService:

  def __init__(self):
    pass
    
  def crear_jugador(self, nuevo_jugador):

    email = nuevo_jugador["email"]
    password1 = nuevo_jugador['password1']
    password2 = nuevo_jugador['password2']
    encrypted_password1 = ""
    encrypted_password2 = ""    
    try:
      found_user = db.session.query(Jugador).filter(Jugador.email == email).first()
      encrypted_password1 = hashlib.md5(password1.encode('utf-8')).hexdigest()
      encrypted_password2 = hashlib.md5(password2.encode('utf-8')).hexdigest()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is not None:
      raise UserAlreadyExists()

    nuevo_jugador = Jugador(
        nombre=nuevo_jugador["nombre"],
        apellido=nuevo_jugador["apellido"],
        email=nuevo_jugador["email"],
        password1=encrypted_password1,
        password2=encrypted_password2,
        ciudad=nuevo_jugador["ciudad"],
        pais=nuevo_jugador["pais"],
        username=nuevo_jugador["username"]
    )

    try:
      db.session.add(nuevo_jugador)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return JugadorCreado(nuevo_jugador.id)

  def lista_jugadores(self):
    found_jugadores = []
    try:
      found_jugadores = db.session.query(Jugador).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_jugadores_json = [JugadorSchema().dump(jugador) for jugador in found_jugadores]

    return JugadoresList(found_jugadores_json)

  def auth_user(self, user_credentials):
    if 'username' not in user_credentials:
      raise InvalidRequestBody()
    if 'password1' not in user_credentials:
      raise InvalidRequestBody()

    username = user_credentials['username']
    password = user_credentials['password1']

    encrypted_password = ""
    try:
      encrypted_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    except Exception as ex:
      raise InvalidRequestBody() from ex

    try:
      filter = Jugador.username == username
      found_user = db.session.query(Jugador).filter(filter).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None or (found_user.password1 != encrypted_password and found_user.password2 != encrypted_password):
        raise UserAuthFailed()
    
    token = generate_new_token(found_user.id)

    return UserAuthSucceed(found_user.id, token)
  
jugador_service = JugadorService()