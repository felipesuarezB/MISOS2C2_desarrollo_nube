from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime, timedelta

from services.trainer_service import trainer_service
from models.entrenador import EntrenadorJsonSchema

entrenadores_bp = Blueprint('entrenadores', __name__, url_prefix='/entrenadores', description="API de entrenadores.")


@entrenadores_bp.route("", methods=["POST"])
@entrenadores_bp.arguments(EntrenadorJsonSchema)
@jwt_required()
def create_trainer(new_trainer):
  jwt_payload = get_jwt()
  result = trainer_service.create_trainer(new_trainer, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@entrenadores_bp.route("/me", methods=["GET"])
@jwt_required()
def trainer_me():
  jwt_payload = get_jwt()
  result = trainer_service.get_my_trainer(jwt_payload)
  res_json = jsonify(result.trainer)

  return res_json, result.code


@entrenadores_bp.route("", methods=["GET"])
@jwt_required()
def list_trainers():
  jwt_payload = get_jwt()
  result = trainer_service.list_trainers(jwt_payload)
  res_json = jsonify(result.trainers)

  return res_json, result.code


@entrenadores_bp.route("/<string:id>")
class EntrenadoresResource(MethodView):

  @jwt_required()
  def get(self, id):
    jwt_payload = get_jwt()
    result = trainer_service.get_trainer(id, jwt_payload)
    res_json = jsonify(result.trainer)

    return res_json, result.code

  @entrenadores_bp.arguments(EntrenadorJsonSchema)
  @jwt_required()
  def put(self, *args, **kwargs):
    id = kwargs['id']
    updated_trainer = args[0]
    jwt_payload = get_jwt()
    result = trainer_service.update_trainer(id, updated_trainer, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code

  @jwt_required()
  def delete(self, id):
    jwt_payload = get_jwt()
    result = trainer_service.delete_trainer(id, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code
