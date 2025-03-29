from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError
from flask_smorest import Blueprint
from app import db
from models.jugador import JugadorSchema
from services.jugador_service import jugador_service

jugadores_bp = Blueprint("jugadores", __name__, url_prefix='/api', description="API de jugadores.")

@jugadores_bp.route("/auth/signup", methods=["POST"])
@jugadores_bp.arguments(JugadorSchema)
def signup(nuevo_jugador):    
    result = jugador_service.crear_jugador(nuevo_jugador)
    res_json = jsonify(result.__dict__)
    
    res = make_response(res_json, result.code)

    return res

@jugadores_bp.route("", methods=["GET"])
def lista_jugadores():
  result = jugador_service.lista_jugadores()
  res_json = jsonify(result.jugadores)
  return res_json, result.code
    