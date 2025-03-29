from flask import request, current_app, make_response
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from datetime import datetime, timedelta

from services.user_service import user_service
from models.usuario import UsuarioJsonSchema, UpdatePasswordJsonSchema

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios', description="API de usuarios.")


def generate_new_token(user_id, user_role):
  token = create_access_token(user_id,
                              expires_delta=timedelta(days=7),
                              additional_claims={
                                  'user_role': user_role
                              })
  return token


@usuarios_bp.route("/signup", methods=["POST"])
@usuarios_bp.arguments(UsuarioJsonSchema)
def signup(new_user):
  result = user_service.create_user(new_user)
  token = generate_new_token(result.user_id, result.user_role)
  res_json = jsonify(result.__dict__)

  res = make_response(res_json, result.code)
  res.headers['Authorization'] = f'Bearer {token}'

  return res


@usuarios_bp.route("/login", methods=["POST"])
@usuarios_bp.arguments(UsuarioJsonSchema)
def login(user_crendentials):
  result = user_service.auth_user(user_crendentials)
  token = generate_new_token(result.user_id, result.user_role)
  res_json = jsonify(result.__dict__)

  res = make_response(res_json, result.code)
  res.headers['Authorization'] = f'Bearer {token}'

  return res


@usuarios_bp.route("/me", methods=["GET"])
@jwt_required()
def user_me():
  jwt_payload = get_jwt()
  result = user_service.get_my_user(jwt_payload)
  res_json = jsonify(result.user)

  return res_json, result.code


@usuarios_bp.route("/password", methods=["PUT"])
@usuarios_bp.arguments(UpdatePasswordJsonSchema)
@jwt_required()
def update_password(new_password):
  jwt_payload = get_jwt()
  result = user_service.update_password(new_password, jwt_payload)
  res_json = jsonify(result.__dict__)

  return res_json, result.code


@usuarios_bp.route("/<string:id>")
class UsuarioResource(MethodView):

  @jwt_required()
  def get(self, id):
    jwt_payload = get_jwt()
    result = user_service.get_user(id, jwt_payload)
    res_json = jsonify(result.user)

    return res_json, result.code
