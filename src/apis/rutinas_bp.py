from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime, timedelta

from api_messages.api_routines import RoutinesList, RoutineFound
from services.routine_service import routine_service
from models.rutina import RutinaJsonSchema

rutinas_bp = Blueprint('rutinas', __name__, url_prefix='/rutinas', description="API de Rutinas.")


@rutinas_bp.route("", methods=["POST"])
@rutinas_bp.arguments(RutinaJsonSchema)
@jwt_required()
def create_routine(new_routine):
  jwt_payload = get_jwt()
  result = routine_service.create_routine(new_routine, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@rutinas_bp.route("", methods=["GET"])
@rutinas_bp.response(RoutinesList.code, RutinaJsonSchema)
@jwt_required()
def list_routines():
  jwt_payload = get_jwt()
  result = routine_service.list_routines(jwt_payload)
  res_json = jsonify(result.routines)

  return res_json, result.code


@rutinas_bp.route("/<string:id>")
class RutinasResource(MethodView):

  @rutinas_bp.response(RoutineFound.code, RutinaJsonSchema)
  @jwt_required()
  def get(self, id):
    jwt_payload = get_jwt()
    result = routine_service.get_routine(id, jwt_payload)
    res_json = jsonify(result.routine)

    return res_json, result.code

  @rutinas_bp.arguments(RutinaJsonSchema)
  @jwt_required()
  def put(self, *args, **kwargs):
    id = kwargs['id']
    updated_routine = args[0]
    jwt_payload = get_jwt()
    result = routine_service.update_routine(id, updated_routine, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code

  @jwt_required()
  def delete(self, id):
    jwt_payload = get_jwt()
    result = routine_service.delete_routine(id, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code
