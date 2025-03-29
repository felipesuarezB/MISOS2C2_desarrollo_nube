import uuid
from datetime import datetime

from models.usuario import RolUsuario
from models.grupo_personas import GrupoPersonas, GrupoPersonasJsonSchema
from models.grupo_personas import RegistroCambioGrupo, RegistroCambioGrupoJsonSchema
from models.persona import Persona
from models.entrenador import Entrenador
from api_messages.api_groups import PersonAlreadyInGroup, PersonAddedToTrainerGroup, GroupPersonsList
from api_messages.api_groups import PersonRemovedFromTrainerGroup, ChangeLogsList
from api_messages.api_persons import PersonNotFound
from api_messages.api_trainers import TrainerNotFound
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation
from database import db


class GroupService:

  def __init__(self):
    pass

  def add_person_to_trainer_group(self, trainer_id, person_id, jwt_payload):
    path_trainer_id_uuid = None
    path_person_id_uuid = None
    try:
      path_trainer_id_uuid = uuid.UUID(trainer_id)
      path_person_id_uuid = uuid.UUID(person_id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id == path_trainer_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is None:
      raise TrainerNotFound()

    if token_user_id != str(found_trainer.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    found_person = None
    try:
      found_person = db.session.query(Persona).filter(Persona.id == path_person_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person is None:
      raise PersonNotFound()

    found_person = None
    try:
      filter_expr1 = GrupoPersonas.id_entrenador == path_trainer_id_uuid
      filter_expr2 = GrupoPersonas.id_persona == path_person_id_uuid
      found_person_in_group = db.session.query(GrupoPersonas).filter(filter_expr1, filter_expr2).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person_in_group is not None:
      raise PersonAlreadyInGroup()

    new_person_in_group = GrupoPersonas(id_entrenador=path_trainer_id_uuid, id_persona=path_person_id_uuid)

    try:
      db.session.add(new_person_in_group)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return PersonAddedToTrainerGroup()

  def list_persons_by_trainer_group(self, id, jwt_payload):
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

    found_persons = []
    try:
      query_expr = [Persona.id, Persona.dni, Persona.nombre, Persona.apellido, GrupoPersonas.id_entrenador]
      on_clause = GrupoPersonas.id_persona == Persona.id
      filter_expr = GrupoPersonas.id_entrenador == path_id_uuid
      found_persons = db.session.query(*query_expr).join(Persona, on_clause).filter(filter_expr).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_persons_json = [GrupoPersonasJsonSchema().dump(person) for person in found_persons]

    return GroupPersonsList(found_persons_json)

  def remove_person_from_trainer_group(self, trainer_id, person_id, change_log, jwt_payload):
    if 'fecha_cambio' not in change_log:
      raise InvalidRequestBody()
    if 'razon_cambio' not in change_log:
      raise InvalidRequestBody()

    change_datetime = None
    try:
      change_datetime = datetime.strptime(change_log['fecha_cambio'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError as ex:
      raise InvalidRequestBody() from ex

    path_trainer_id_uuid = None
    path_person_id_uuid = None
    try:
      path_trainer_id_uuid = uuid.UUID(trainer_id)
      path_person_id_uuid = uuid.UUID(person_id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_trainer = None
    try:
      found_trainer = db.session.query(Entrenador).filter(Entrenador.id == path_trainer_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_trainer is None:
      raise TrainerNotFound()

    if token_user_id != str(found_trainer.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value]:
        raise ForbiddenOperation()

    found_person_in_group = None
    try:
      filter_expr1 = GrupoPersonas.id_entrenador == path_trainer_id_uuid
      filter_expr2 = GrupoPersonas.id_persona == path_person_id_uuid
      found_person_in_group = db.session.query(GrupoPersonas).filter(filter_expr1, filter_expr2).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person_in_group is None:
      raise PersonNotFound()

    new_change_log = RegistroCambioGrupo(id_entrenador=path_trainer_id_uuid,
                                         id_persona=path_person_id_uuid,
                                         fecha_cambio=change_datetime,
                                         razon_cambio=change_log['razon_cambio'])

    try:
      db.session.delete(found_person_in_group)
      db.session.add(new_change_log)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return PersonRemovedFromTrainerGroup()

  def get_group_change_logs_of_person(self, id, jwt_payload):
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

    found_change_logs = []
    try:
      filter_expr = RegistroCambioGrupo.id_persona == path_id_uuid
      found_change_logs = db.session.query(RegistroCambioGrupo).filter(filter_expr).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_change_logs_json = [RegistroCambioGrupoJsonSchema().dump(change_log) for change_log in found_change_logs]

    return ChangeLogsList(found_change_logs_json)


group_service = GroupService()
