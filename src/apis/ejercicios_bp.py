from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime, timedelta

from services.exercise_service import exercise_service
from models.ejercicio import EjercicioJsonSchema

ejercicios_bp = Blueprint('ejercicios', __name__, url_prefix='/ejercicios', description="API de Ejercicios.")


@ejercicios_bp.route("", methods=["POST"])
@ejercicios_bp.arguments(EjercicioJsonSchema)
@jwt_required()
def create_exercise(new_exercise):
  jwt_payload = get_jwt()
  result = exercise_service.create_exercise(new_exercise, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@ejercicios_bp.route("", methods=["GET"])
@jwt_required()
def list_exercises():
  jwt_payload = get_jwt()
  result = exercise_service.list_exercises(jwt_payload)
  res_json = jsonify(result.exercises)

  return res_json, result.code


@ejercicios_bp.route("/<string:id>")
class EjerciciosResource(MethodView):

  @jwt_required()
  def get(self, id):
    jwt_payload = get_jwt()
    result = exercise_service.get_exercise(id, jwt_payload)
    res_json = jsonify(result.exercise)

    return res_json, result.code

  @ejercicios_bp.arguments(EjercicioJsonSchema)
  @jwt_required()
  def put(self, *args, **kwargs):
    id = kwargs['id']
    updated_exercise = args[0]
    jwt_payload = get_jwt()
    result = exercise_service.update_exercise(id, updated_exercise, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code

  @jwt_required()
  def delete(self, id):
    jwt_payload = get_jwt()
    result = exercise_service.delete_exercise(id, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code
