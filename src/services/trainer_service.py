import uuid

from models.usuario import Usuario, RolUsuario
from models.entrenador import Entrenador, EntrenadorJsonSchema
from api_messages.api_users import UserNotFound
from api_messages.api_trainers import TrainerCreated, TrainerAlreadyExists, TrainersList, TrainerNotFound, TrainerFound
from api_messages.api_trainers import TrainerUpdated, TrainerDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import InvalidTokenPayloadParams, ForbiddenOperation
from database import db


class TrainerService:

  def __init__(self):
    pass

  def create_trainer(self, new_trainer, jwt_payload):
    if 'nombre' not in new_trainer:
      raise InvalidRequestBody()
    if 'apellido' not in new_trainer:
      raise InvalidRequestBody()
    if 'id_usuario' not in new_trainer:
      raise InvalidRequestBody()

    new_trainer_user_id = new_trainer['id_usuario']
    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    if new_trainer_user_id != token_user_id:
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    trainer_user_id_uuid = None
    try:
      trainer_user_id_uuid = uuid.UUID(new_trainer_user_id)
    except Exception as ex:
      raise InvalidRequestBody() from ex

    found_user = None
    try:
      found_user = db.session.query(Usuario).filter(Usuario.id == trainer_user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None:
      raise UserNotFound()

    if found_user.rol not in [RolUsuario.ENTRENADOR.value]:
      raise InvalidRequestBody()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id_usuario == trainer_user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is not None:
      raise TrainerAlreadyExists()

    new_trainer = Entrenador(nombre=new_trainer['nombre'],
                             apellido=new_trainer['apellido'],
                             id_usuario=trainer_user_id_uuid)

    try:
      db.session.add(new_trainer)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return TrainerCreated(new_trainer.id)

  def get_my_trainer(self, jwt_payload):
    token_user_id = jwt_payload['sub']
    token_user_id_uuid = None
    try:
      token_user_id_uuid = uuid.UUID(token_user_id)
    except Exception as ex:
      raise InvalidTokenPayloadParams() from ex

    token_user_role = jwt_payload['user_role']
    if token_user_role not in [RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id_usuario == token_user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is None:
      raise TrainerNotFound()

    found_trainer_json = EntrenadorJsonSchema().dump(found_trainer)

    return TrainerFound(found_trainer_json)

  def list_trainers(self, jwt_payload):
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
      raise ForbiddenOperation()

    found_trainers = []
    try:
      found_trainers = db.session.query(Entrenador).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_trainers_json = [EntrenadorJsonSchema().dump(trainer) for trainer in found_trainers]

    return TrainersList(found_trainers_json)

  def get_trainer(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is None:
      raise TrainerNotFound()

    if token_user_id != str(found_trainer.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    found_trainer_json = EntrenadorJsonSchema().dump(found_trainer)

    return TrainerFound(found_trainer_json)

  def update_trainer(self, id, updated_trainer, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is None:
      raise TrainerNotFound()

    if token_user_id != str(found_trainer.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    try:
      if 'nombre' in updated_trainer:
        found_trainer.nombre = updated_trainer['nombre']
      if 'apellido' in updated_trainer:
        found_trainer.apellido = updated_trainer['apellido']

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return TrainerUpdated()

  def delete_trainer(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
      raise ForbiddenOperation()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is None:
      raise TrainerNotFound()

    if token_user_id != str(found_trainer.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    try:
      db.session.delete(found_trainer)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return TrainerDeleted()


trainer_service = TrainerService()
