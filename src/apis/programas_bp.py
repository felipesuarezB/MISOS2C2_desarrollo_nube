from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime, timedelta

from api_messages.api_programs import ProgramsList, ProgramFound
from services.program_service import program_service
from models.programa import ProgramaJsonSchema

programas_bp = Blueprint('programas', __name__, url_prefix='/programas', description="API de Programas.")


@programas_bp.route("", methods=["POST"])
@programas_bp.arguments(ProgramaJsonSchema)
@jwt_required()
def create_program(new_program):
  jwt_payload = get_jwt()
  result = program_service.create_program(new_program, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@programas_bp.route("", methods=["GET"])
@programas_bp.response(ProgramsList.code, ProgramaJsonSchema)
@jwt_required()
def list_programs():
  jwt_payload = get_jwt()
  result = program_service.list_programs(jwt_payload)
  res_json = jsonify(result.programs)

  return res_json, result.code


@programas_bp.route("/<string:id>")
class RutinasResource(MethodView):

  @programas_bp.response(ProgramFound.code, ProgramaJsonSchema)
  @jwt_required()
  def get(self, id):
    jwt_payload = get_jwt()
    result = program_service.get_program(id, jwt_payload)
    res_json = jsonify(result.program)

    return res_json, result.code

  @programas_bp.arguments(ProgramaJsonSchema)
  @jwt_required()
  def put(self, *args, **kwargs):
    id = kwargs['id']
    updated_program = args[0]
    jwt_payload = get_jwt()
    result = program_service.update_program(id, updated_program, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code

  @jwt_required()
  def delete(self, id):
    jwt_payload = get_jwt()
    result = program_service.delete_program(id, jwt_payload)
    res_json = jsonify(result.__dict__)

    return res_json, result.code
