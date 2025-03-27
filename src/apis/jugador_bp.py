from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError
from app import db
from models.jugador import JugadorSchema
from services.jugador_service import jugador_service

jugadores_bp = Blueprint("jugadores", __name__, url_prefix='/api', description="API de usuarios.")

@jugadores_bp.route("/auth/signup", methods=["POST"])
@jugadores_bp.arguments(JugadorSchema)
def signup(nuevo_jugador):    
    result = jugador_service.crear_jugador(nuevo_jugador)
    res_json = jsonify(result.__dict__)

    return res_json, result.code

    