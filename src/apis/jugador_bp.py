from datetime import timedelta
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError
from flask_smorest import Blueprint
from app import db
from models.jugador import JugadorJsonSchema, JugadorSchema
from services.jugador_service import jugador_service
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

jugadores_bp = Blueprint("jugadores", __name__, url_prefix='/api', description="API de jugadores.")

@jugadores_bp.route("/auth/signup", methods=["POST"])
@jugadores_bp.arguments(JugadorSchema)
def signup(nuevo_jugador):    
    result = jugador_service.crear_jugador(nuevo_jugador)
    res_json = jsonify(result.__dict__)
    
    res = make_response(res_json, result.code)

    return res
    
@jugadores_bp.route("/auth/login", methods=["POST"])
@jugadores_bp.arguments(JugadorJsonSchema)
def login(user_crendentials):
  result = jugador_service.auth_user(user_crendentials)
  res_json = jsonify(result.__dict__)

  res = make_response(res_json, result.code)

  return res