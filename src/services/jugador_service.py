from flask import jsonify
from api_messages.api_errors import InternalServerError
from api_messages.api_users import UserAlreadyExists
from models.jugador import JugadorSchema, Jugador
from database import db


class JugadorService:

  def __init__(self):
    pass

  def crear_jugador(self, nuevo_jugador):

    username = nuevo_jugador["username"]
    found_user = None
    try:
      found_user = db.session.query(Jugador).filter(Jugador.usuario == username).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is not None:
      raise UserAlreadyExists()

    nuevo_jugador = Jugador(
        nombre=nuevo_jugador["nombre"],
        apellido=nuevo_jugador["apellido"],
        email=nuevo_jugador["email"],
        password=nuevo_jugador["password1"],
        paassword2=nuevo_jugador["password2"],
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

    return jsonify({"message": "Usuario creado exitosamente"}), 201


jugador_service = JugadorService()
