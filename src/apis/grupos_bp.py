from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime, timedelta

from services.group_service import group_service
from models.grupo_personas import RegistroCambioGrupoJsonSchema

grupos_bp = Blueprint('grupos', __name__, url_prefix='/grupos', description="API de grupos.")


@grupos_bp.route("<string:trainer_id>/miembros/<string:person_id>", methods=["POST"])
@jwt_required()
def add_person_to_trainer_group(trainer_id, person_id):
  jwt_payload = get_jwt()
  result = group_service.add_person_to_trainer_group(trainer_id, person_id, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@grupos_bp.route("<string:id>/miembros", methods=["GET"])
@jwt_required()
def list_persons_by_trainer_group(id):
  jwt_payload = get_jwt()
  result = group_service.list_persons_by_trainer_group(id, jwt_payload)
  res_json = jsonify(result.persons)

  return res_json, result.code


@grupos_bp.route("<string:trainer_id>/miembros/<string:person_id>", methods=["DELETE"])
@grupos_bp.arguments(RegistroCambioGrupoJsonSchema)
@jwt_required()
def remove_person_from_trainer_group(*args, **kwargs):
  trainer_id = kwargs['trainer_id']
  person_id = kwargs['person_id']
  change_log = args[0]
  jwt_payload = get_jwt()
  result = group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@grupos_bp.route("cambios/<string:id>", methods=["GET"])
@jwt_required()
def get_group_change_logs_of_person(id):
  jwt_payload = get_jwt()
  result = group_service.get_group_change_logs_of_person(id, jwt_payload)
  res_json = jsonify(result.change_logs)

  return res_json, result.code
