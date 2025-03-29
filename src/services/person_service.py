import uuid
from datetime import datetime

from models.usuario import Usuario, RolUsuario
from models.persona import Persona, PersonaJsonSchema
from api_messages.api_users import UserNotFound
from api_messages.api_persons import PersonAlreadyExists, PersonCreated, PersonsList, PersonNotFound, PersonFound
from api_messages.api_persons import PersonUpdated, PersonDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation, InvalidTokenPayloadParams
from database import db


class PersonService:

  def __init__(self):
    pass

  def create_person(self, new_person, jwt_payload):
    if 'dni' not in new_person:
      raise InvalidRequestBody()
    if 'nombre' not in new_person:
      raise InvalidRequestBody()
    if 'apellido' not in new_person:
      raise InvalidRequestBody()
    if 'fecha_nacimiento' not in new_person:
      raise InvalidRequestBody()
    if 'fecha_ingreso' not in new_person:
      raise InvalidRequestBody()
    if 'id_usuario' not in new_person:
      raise InvalidRequestBody()

    birth_datetime = None
    entry_datetime = None
    try:
      birth_datetime = datetime.strptime(new_person['fecha_nacimiento'], '%Y-%m-%dT%H:%M:%S.%fZ')
      entry_datetime = datetime.strptime(new_person['fecha_ingreso'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError as ex:
      raise InvalidRequestBody() from ex

    new_person_user_id = new_person['id_usuario']

    person_user_id_uuid = None
    try:
      person_user_id_uuid = uuid.UUID(new_person_user_id)
    except Exception as ex:
      raise InvalidRequestBody() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    if new_person_user_id != token_user_id:
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                                 RolUsuario.ENTRENADOR.value]:
        raise ForbiddenOperation()

    found_user = None
    try:
      found_user = db.session.query(Usuario).filter(Usuario.id == person_user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_user is None:
      raise UserNotFound()

    if found_user.rol not in [RolUsuario.PERSONA.value]:
      raise InvalidRequestBody()

    found_person = None
    try:
      found_person = db.session.query(Persona).filter(Persona.id_usuario == person_user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person is not None:
      raise PersonAlreadyExists()

    new_person = Persona(dni=new_person['dni'],
                         nombre=new_person['nombre'],
                         apellido=new_person['apellido'],
                         fecha_nacimiento=birth_datetime,
                         fecha_ingreso=entry_datetime,
                         talla=new_person['talla'],
                         peso=new_person['peso'],
                         medida_brazo=new_person['medida_brazo'],
                         medida_pecho=new_person['medida_pecho'],
                         medida_cintura=new_person['medida_cintura'],
                         medida_pierna=new_person['medida_pierna'],
                         id_usuario=person_user_id_uuid)

    try:
      db.session.add(new_person)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return PersonCreated(new_person.id)

  def get_my_person(self, jwt_payload):
    token_user_id = jwt_payload['sub']
    token_user_id_uuid = None
    try:
      token_user_id_uuid = uuid.UUID(token_user_id)
    except Exception as ex:
      raise InvalidTokenPayloadParams() from ex

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.PERSONA.value]:
      raise ForbiddenOperation()

    found_person = None
    try:
      found_person = db.session.query(Persona).filter(Persona.id_usuario == token_user_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person is None:
      raise PersonNotFound()

    found_person_json = PersonaJsonSchema().dump(found_person)

    return PersonFound(found_person_json)

  def list_persons(self, jwt_payload):
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_persons = []
    try:
      found_persons = db.session.query(Persona).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_persons_json = [PersonaJsonSchema().dump(person) for person in found_persons]

    return PersonsList(found_persons_json)

  def get_person(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    found_person = None
    try:
      found_person = db.session.query(Persona).filter(Persona.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person is None:
      raise PersonNotFound()

    if token_user_id != str(found_person.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                                 RolUsuario.ENTRENADOR.value]:
        raise ForbiddenOperation()

    found_person_json = PersonaJsonSchema().dump(found_person)

    return PersonFound(found_person_json)

  def update_person(self, id, updated_person, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    birth_datetime = None
    if 'fecha_nacimiento' in updated_person:
      try:
        birth_datetime = datetime.strptime(updated_person['fecha_nacimiento'], '%Y-%m-%dT%H:%M:%S.%fZ')
      except ValueError as ex:
        raise InvalidRequestBody() from ex

    entry_datetime = None
    if 'fecha_ingreso' in updated_person:
      try:
        entry_datetime = datetime.strptime(updated_person['fecha_ingreso'], '%Y-%m-%dT%H:%M:%S.%fZ')
      except ValueError as ex:
        raise InvalidRequestBody() from ex

    token_user_id = jwt_payload['sub']
    token_user_role = jwt_payload['user_role']

    found_person = None
    try:
      found_person = db.session.query(Persona).filter(Persona.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person is None:
      raise PersonNotFound()

    if token_user_id != str(found_person.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                                 RolUsuario.ENTRENADOR.value]:
        raise ForbiddenOperation()

    try:
      if 'dni' in updated_person:
        found_person.dni = updated_person['dni']
      if 'nombre' in updated_person:
        found_person.nombre = updated_person['nombre']
      if 'apellido' in updated_person:
        found_person.apellido = updated_person['apellido']
      if 'fecha_nacimiento' in updated_person:
        found_person.fecha_nacimiento = birth_datetime
      if 'fecha_ingreso' in updated_person:
        found_person.fecha_ingreso = entry_datetime
      if 'talla' in updated_person:
        found_person.talla = updated_person['talla']
      if 'peso' in updated_person:
        found_person.peso = updated_person['peso']
      if 'medida_brazo' in updated_person:
        found_person.medida_brazo = updated_person['medida_brazo']
      if 'medida_pecho' in updated_person:
        found_person.medida_pecho = updated_person['medida_pecho']
      if 'medida_cintura' in updated_person:
        found_person.medida_cintura = updated_person['medida_cintura']
      if 'medida_pierna' in updated_person:
        found_person.medida_pierna = updated_person['medida_pierna']

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return PersonUpdated()

  def delete_person(self, id, jwt_payload):
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

    found_person = None
    try:
      found_person = db.session.query(Persona).filter(Persona.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_person is None:
      raise PersonNotFound()

    if token_user_id != str(found_person.id_usuario):
      if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                                 RolUsuario.ENTRENADOR.value]:
        raise ForbiddenOperation()

    try:
      db.session.delete(found_person)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return PersonDeleted()


person_service = PersonService()
