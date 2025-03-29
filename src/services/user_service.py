import hashlib
import uuid

from models.usuario import Usuario, UsuarioJsonSchema, RolUsuario
from api_messages.api_users import UserCreated, UserAlreadyExists, UserAuthFailed, UserAuthSucceed
from api_messages.api_users import UserPasswordUpdated, UserNotFound, UserFound
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams, ForbiddenOperation
from database import db


class UserService:

  def __init__(self):
    pass

  def create_user(self, new_user):
    if 'usuario' not in new_user:
      raise InvalidRequestBody()
    if 'contrasena' not in new_user:
      raise InvalidRequestBody()
    if 'rol' not in new_user:
      raise InvalidRequestBody()

    username = new_user['usuario']
    password = new_user['password1']
    user_role = new_user['rol']

    found_user = None
    try:
      found_user = db.session.query(Usuario).filter(Usuario.usuario == username).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is not None:
      raise UserAlreadyExists()

    encrypted_password = ""
    user_role_index = 0
    try:
      encrypted_password = hashlib.md5(password.encode('utf-8')).hexdigest()
      user_role_index = RolUsuario(user_role).value
    except Exception as ex:
      raise InvalidRequestBody() from ex

    new_user = Usuario(usuario=username, contrasena=encrypted_password, rol=user_role_index)

    try:
      db.session.add(new_user)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return UserCreated(new_user.id, new_user.rol)

  def auth_user(self, user_credentials):
    if 'usuario' not in user_credentials:
      raise InvalidRequestBody()
    if 'contrasena' not in user_credentials:
      raise InvalidRequestBody()

    username = user_credentials['usuario']
    password = user_credentials['contrasena']

    encrypted_password = ""
    try:
      encrypted_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    except Exception as ex:
      raise InvalidRequestBody() from ex

    found_user = None
    try:
      filter1 = Usuario.usuario == username
      filter2 = Usuario.contrasena == encrypted_password
      found_user = db.session.query(Usuario).filter(filter1, filter2).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None:
      raise UserAuthFailed()

    return UserAuthSucceed(found_user.id, found_user.rol)

  def get_my_user(self, jwt_payload):
    token_user_id = jwt_payload['sub']
    user_id_uuid = None
    try:
      user_id_uuid = uuid.UUID(token_user_id)
    except Exception as ex:
      raise InvalidRequestBody() from ex

    found_user = None
    try:
      found_user = db.session.query(Usuario).filter(Usuario.id == user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None:
      raise UserNotFound()

    found_user_json = UsuarioJsonSchema(only=("usuario", "rol")).dump(found_user)

    return UserFound(found_user_json)

  def update_password(self, new_password, jwt_payload):
    if 'usuario' not in new_password:
      raise InvalidRequestBody()
    if 'contrasena_actual' not in new_password:
      raise InvalidRequestBody()
    if 'contrasena_nueva' not in new_password:
      raise InvalidRequestBody()

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    username = new_password['usuario']
    current_password = new_password['contrasena_actual']

    encrypted_password = ""
    try:
      encrypted_password = hashlib.md5(current_password.encode('utf-8')).hexdigest()
    except Exception as ex:
      raise InvalidRequestBody() from ex

    found_user = None
    try:
      filter1 = Usuario.usuario == username
      filter2 = Usuario.contrasena == encrypted_password
      found_user = db.session.query(Usuario).filter(filter1, filter2).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None:
      raise UserNotFound()

    if found_user.rol == RolUsuario.PERSONA.value:
      if token_user_id != id:
        if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                                   RolUsuario.ENTRENADOR.value]:
          raise ForbiddenOperation()
    elif found_user.rol == RolUsuario.ENTRENADOR.value:
      if token_user_id != id:
        if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
          raise ForbiddenOperation()
    elif found_user.rol == RolUsuario.ADMINISTRADOR_GIMNASIO.value:
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    updated_password = new_password['contrasena_nueva']

    encrypted_new_password = ""
    try:
      encrypted_new_password = hashlib.md5(updated_password.encode('utf-8')).hexdigest()
    except Exception as ex:
      raise InvalidRequestBody() from ex

    try:
      found_user.contrasena = encrypted_new_password

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return UserPasswordUpdated(found_user.id, found_user.rol)

  def get_user(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    found_user = None
    try:
      found_user = db.session.query(Usuario).filter(Usuario.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None:
      raise UserNotFound()

    if found_user.rol == RolUsuario.PERSONA.value:
      if token_user_id != id:
        if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                                   RolUsuario.ENTRENADOR.value]:
          raise ForbiddenOperation()
    elif found_user.rol == RolUsuario.ENTRENADOR.value:
      if token_user_id != id:
        if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
          raise ForbiddenOperation()
    elif found_user.rol == RolUsuario.ADMINISTRADOR_GIMNASIO.value:
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    found_user_json = UsuarioJsonSchema(only=("usuario", "rol")).dump(found_user)

    return UserFound(found_user_json)


user_service = UserService()
