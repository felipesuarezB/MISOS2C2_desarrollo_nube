import hashlib
from flask import jsonify
from api_messages.api_errors import InternalServerError
from api_messages.api_users import UserAlreadyExists
from api_messages.api_jugadores import JugadorCreado, JugadoresList
from models.jugador import JugadorSchema, Jugador
from database import db


class JugadorService:

  def __init__(self):
    pass

  def crear_jugador(self, nuevo_jugador):

    email = nuevo_jugador["email"]
    password = nuevo_jugador['password1']
    
    found_user = None
    encrypted_password = ""
    
    try:
      found_user = db.session.query(Jugador).filter(Jugador.email == email).first()
      encrypted_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is not None:
      raise UserAlreadyExists()

    nuevo_jugador = Jugador(
        nombre=nuevo_jugador["nombre"],
        apellido=nuevo_jugador["apellido"],
        email=nuevo_jugador["email"],
        password1=encrypted_password,
        ciudad=nuevo_jugador["ciudad"],
        pais=nuevo_jugador["pais"],
        username=nuevo_jugador["username"]
    )

    db.session.add(nuevo_jugador)
    db.session.commit()
    # try:
    #   db.session.add(nuevo_jugador)
    #   db.session.commit()
    # except Exception as ex:
    #   db.session.rollback()
    #   raise InternalServerError() from ex

    return JugadorCreado(nuevo_jugador.id)

  def lista_jugadores(self):
    found_jugadores = []
    try:
      found_jugadores = db.session.query(Jugador).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_jugadores_json = [JugadorSchema().dump(jugador) for jugador in found_jugadores]

    return JugadoresList(found_jugadores_json)



jugador_service = JugadorService()