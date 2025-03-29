import uuid

from models.usuario import RolUsuario
from models.ejercicio import Ejercicio, EjercicioJsonSchema
from models.rutina import RutinaEjercicios
from api_messages.api_exercises import ExerciseCreated, ExercisesList, ExerciseFound, ExerciseNotFound
from api_messages.api_exercises import ExerciseUpdated, ExerciseAssociatedWithRoutine, ExerciseDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation
from database import db


class ExerciseService:

  def __init__(self):
    pass

  def create_exercise(self, new_exercise, jwt_payload):
    if 'nombre' not in new_exercise:
      raise InvalidRequestBody()
    if 'descripcion' not in new_exercise:
      raise InvalidRequestBody()
    if 'link_video' not in new_exercise:
      raise InvalidRequestBody()
    if 'calorias_por_repeticion' not in new_exercise:
      raise InvalidRequestBody()

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    new_exercise = Ejercicio(nombre=new_exercise['nombre'],
                             descripcion=new_exercise['descripcion'],
                             link_video=new_exercise['link_video'],
                             calorias_por_repeticion=new_exercise['calorias_por_repeticion'])

    try:
      db.session.add(new_exercise)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return ExerciseCreated(new_exercise.id)

  def list_exercises(self, jwt_payload):
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_exercises = []
    try:
      found_exercises = db.session.query(Ejercicio).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_exercises_json = [EjercicioJsonSchema().dump(exercise) for exercise in found_exercises]

    return ExercisesList(found_exercises_json)

  def get_exercise(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value,
                               RolUsuario.PERSONA.value]:
      raise ForbiddenOperation()

    found_exercise = None
    try:
      found_exercise = db.session.query(Ejercicio).filter(Ejercicio.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_exercise is None:
      raise ExerciseNotFound()

    found_exercise_json = EjercicioJsonSchema().dump(found_exercise)

    return ExerciseFound(found_exercise_json)

  def update_exercise(self, id, updated_exercise, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_exercise = None
    try:
      found_exercise = db.session.query(Ejercicio).filter(Ejercicio.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_exercise is None:
      raise ExerciseNotFound()

    try:
      if 'nombre' in updated_exercise:
        found_exercise.nombre = updated_exercise['nombre']
      if 'descripcion' in updated_exercise:
        found_exercise.descripcion = updated_exercise['descripcion']
      if 'link_video' in updated_exercise:
        found_exercise.link_video = updated_exercise['link_video']
      if 'calorias_por_repeticion' in updated_exercise:
        found_exercise.calorias_por_repeticion = updated_exercise['calorias_por_repeticion']

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return ExerciseUpdated()

  def delete_exercise(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_exercise = None
    try:
      found_exercise = db.session.query(Ejercicio).filter(Ejercicio.id == path_id_uuid).first()
    except Exception as ex:
      raise InternalServerError() from ex

    if found_exercise is None:
      raise ExerciseNotFound()

    exists_routine_assoc = self._exists_routine_exercises_assoc(found_exercise.id)

    if exists_routine_assoc:
      raise ExerciseAssociatedWithRoutine()

    try:
      db.session.delete(found_exercise)
      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return ExerciseDeleted()

  def _exists_routine_exercises_assoc(self, exercise_id_uuid):
    exists_assoc = False

    found_routine_exercise = None
    try:
      filter_expr = RutinaEjercicios.id_ejercicio == exercise_id_uuid
      found_routine_exercise = db.session.query(RutinaEjercicios).filter(filter_expr).first()
    except Exception as ex:
      raise InternalServerError() from ex

    exists_assoc = found_routine_exercise != None

    return exists_assoc


exercise_service = ExerciseService()
