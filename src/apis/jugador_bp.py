from datetime import timedelta
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError
from flask_smorest import Blueprint
from src.models.jugador import JugadorJsonSchema, JugadorSchema
from src.services.jugador_service import jugador_service
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from src.api_messages.api_jugadores import UserAlreadyExists

jugadores_bp = Blueprint("jugadores", __name__, url_prefix='/api', description="API de jugadores.")

# def generate_new_token(user_id):
#   token = create_access_token(user_id,expires_delta=timedelta(seconds=3600))
#   return token

@jugadores_bp.route("/auth/signup", methods=["POST"])
@jugadores_bp.arguments(JugadorSchema)
def signup(nuevo_jugador):    
    try:
        result = jugador_service.crear_jugador(nuevo_jugador)
        res_json = jsonify(result.__dict__)
        res = make_response(res_json, result.code)
        return res
    except UserAlreadyExists as e:
        res_json = jsonify({"message": e.message})
        res = make_response(res_json, e.code)
        return res

@jugadores_bp.route("", methods=["GET"])
@jwt_required()
def lista_jugadores():
    result = jugador_service.lista_jugadores()
    res_json = jsonify(result.jugadores)
    return res_json, result.code
    
    
@jugadores_bp.route("/auth/login", methods=["POST"])
@jugadores_bp.arguments(JugadorJsonSchema)
def login(user_credentials):
  result = jugador_service.auth_user(user_credentials)
#   token = generate_new_token(result.user_id)
  res_json = jsonify(result.__dict__)

  res = make_response(res_json, result.code)
#   res.headers['Authorization'] = f'Bearer {token}'

  return res

