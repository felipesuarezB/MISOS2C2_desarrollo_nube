from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime, timedelta

from services.person_service import person_service
from models.persona import PersonaJsonSchema

personas_bp = Blueprint('personas', __name__, url_prefix='/personas', description="API de personas.")


@personas_bp.route("", methods=["POST"])
@personas_bp.arguments(PersonaJsonSchema)
@jwt_required()
def create_person(new_person):
  jwt_payload = get_jwt()
  result = person_service.create_person(new_person, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@personas_bp.route("/me", methods=["GET"])
@jwt_required()
def person_me():
  jwt_payload = get_jwt()
  result = person_service.get_my_person(jwt_payload)
  res_json = jsonify(result.person)

  return res_json, result.code


@personas_bp.route("", methods=["GET"])
@jwt_required()
def list_persons():
  jwt_payload = get_jwt()
  result = person_service.list_persons(jwt_payload)
  res_json = jsonify(result.persons)

  return res_json, result.code


@personas_bp.route("/<string:id>")
class PersonasResource(MethodView):

  @jwt_required()
  def get(self, id):
    jwt_payload = get_jwt()
    result = person_service.get_person(id, jwt_payload)
    res_json = jsonify(result.person)

    return res_json, result.code

  @personas_bp.arguments(PersonaJsonSchema)
  @jwt_required()
  def put(self, *args, **kwargs):
    id = kwargs['id']
    updated_person = args[0]
    jwt_payload = get_jwt()
    result = person_service.update_person(id, updated_person, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code

  @jwt_required()
  def delete(self, id):
    jwt_payload = get_jwt()
    result = person_service.delete_person(id, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code
