import uuid

from models.usuario import RolUsuario
from models.rutina import Rutina, RutinaEjercicios, RutinaJsonSchema, RutinaEjercicioJsonSchema
from models.programa import ProgramaRutinas
from models.ejercicio import Ejercicio
from api_messages.api_routines import RoutineCreated, RoutinesList, RoutineFound, RoutineNotFound
from api_messages.api_routines import RoutineUpdated, RoutineAssociatedWithProgram, RoutineDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation
from database import db


class RoutineService:

  def __init__(self):
    pass

  def create_routine(self, new_routine, jwt_payload):
    if 'nombre' not in new_routine:
      raise InvalidRequestBody()
    if 'descripcion' not in new_routine:
      raise InvalidRequestBody()
    if 'total_minutos' not in new_routine:
      raise InvalidRequestBody()
    if 'lista_ejercicios' not in new_routine:
      raise InvalidRequestBody()

    routine_exercises_ids_uuids = self._parse_routine_exercises_ids_uuids(new_routine)

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    routine = Rutina(id=uuid.uuid4(),
                     nombre=new_routine['nombre'],
                     descripcion=new_routine['descripcion'],
                     total_minutos=new_routine['total_minutos'])

    routine_exercises = []
    for index, routine_exercise_id_uuid in enumerate(routine_exercises_ids_uuids):
      routine_exercise_id_uuid = RutinaEjercicios(id_rutina=routine.id,
                                                  id_ejercicio=routine_exercise_id_uuid,
                                                  repeticiones=new_routine['lista_ejercicios'][index]['repeticiones'])
      routine_exercises.append(routine_exercise_id_uuid)

    try:
      db.session.add(routine)
      for routine_exercise in routine_exercises:
        db.session.add(routine_exercise)

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return RoutineCreated(routine.id)

  def list_routines(self, jwt_payload):
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_routines = []
    try:
      found_routines = db.session.query(Rutina).all()
    except Exception as ex:
      raise InternalServerError() from ex

    found_routine_exercises = []
    for routine in found_routines:
      routine_exercises = self._find_routine_exercises_details(routine.id)
      found_routine_exercises.append(routine_exercises)

    found_routines_json = []
    for index, routine in enumerate(found_routines):
      routine_json = self._parse_routine_json(routine, index, found_routine_exercises)
      found_routines_json.append(routine_json)

    return RoutinesList(found_routines_json)

  def get_routine(self, id, jwt_payload):
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

    found_routine = self._find_routine_by_id(path_id_uuid)

    if found_routine is None:
      raise RoutineNotFound()

    found_routine_exercises = self._find_routine_exercises_details(found_routine.id)

    found_routine_json = self._parse_routine_json(found_routine, 0, [found_routine_exercises])

    return RoutineFound(found_routine_json)

  def update_routine(self, id, updated_routine, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    if 'lista_ejercicios' not in updated_routine:
      raise InvalidRequestBody()

    routine_exercises_ids_uuids = self._parse_routine_exercises_ids_uuids(updated_routine)

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_routine = self._find_routine_by_id(path_id_uuid)

    if found_routine is None:
      raise RoutineNotFound()

    found_routine_exercises = self._find_routine_exercises(found_routine.id)

    updated_routine_exercises = []
    for index, routine_exercise_json in enumerate(updated_routine['lista_ejercicios']):
      routine_exercise = RutinaEjercicios(id_rutina=found_routine.id,
                                          id_ejercicio=routine_exercises_ids_uuids[index],
                                          repeticiones=routine_exercise_json['repeticiones'])
      updated_routine_exercises.append(routine_exercise)

    try:
      if 'nombre' in updated_routine:
        found_routine.nombre = updated_routine['nombre']
      if 'descripcion' in updated_routine:
        found_routine.descripcion = updated_routine['descripcion']
      if 'total_minutos' in updated_routine:
        found_routine.total_minutos = updated_routine['total_minutos']

      for routine_exercise in found_routine_exercises:
        db.session.delete(routine_exercise)

      for routine_exercise in updated_routine_exercises:
        db.session.add(routine_exercise)

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return RoutineUpdated()

  def delete_routine(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_routine = self._find_routine_by_id(path_id_uuid)

    if found_routine is None:
      raise RoutineNotFound()

    exists_program_assoc = self._exists_program_routines_assoc(found_routine.id)

    if exists_program_assoc:
      raise RoutineAssociatedWithProgram()

    try:
      del_filter_expr = RutinaEjercicios.id_rutina == found_routine.id
      db.session.query(RutinaEjercicios).filter(del_filter_expr).delete()

      db.session.delete(found_routine)

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return RoutineDeleted()

  def _parse_routine_exercises_ids_uuids(self, routine_json):
    routine_exercises_ids_uuids = []
    for routine_exercise_json in routine_json['lista_ejercicios']:
      try:
        exercise_id_uuid = uuid.UUID(routine_exercise_json['id_ejercicio'])
      except Exception as ex:
        raise InvalidRequestBody() from ex

      routine_exercises_ids_uuids.append(exercise_id_uuid)

    return routine_exercises_ids_uuids

  def _find_routine_by_id(self, routine_id_uuid):
    found_routine = None
    try:
      filter_expr = Rutina.id == routine_id_uuid
      found_routine = db.session.query(Rutina).filter(filter_expr).first()
    except Exception as ex:
      raise InternalServerError() from ex

    return found_routine

  def _find_routine_exercises(self, routine_id_uuid):
    found_routine_exercises = []
    try:
      filter_expr = RutinaEjercicios.id_rutina == routine_id_uuid
      found_routine_exercises = db.session.query(RutinaEjercicios).filter(filter_expr).all()
    except Exception as ex:
      raise InternalServerError() from ex

    return found_routine_exercises

  def _find_routine_exercises_details(self, routine_id_uuid):
    found_routine_exercises = []
    try:
      query_expr = [Ejercicio.nombre, Ejercicio.calorias_por_repeticion, RutinaEjercicios.id_ejercicio, RutinaEjercicios.repeticiones]
      on_clause = RutinaEjercicios.id_ejercicio == Ejercicio.id
      filter_expr = RutinaEjercicios.id_rutina == routine_id_uuid
      found_routine_exercises = db.session.query(*query_expr).join(Ejercicio, on_clause).filter(filter_expr).all()
    except Exception as ex:
      raise InternalServerError() from ex

    return found_routine_exercises

  def _parse_routine_json(self, routine, index, routine_exercises):
    routine_json = RutinaJsonSchema().dump(routine)
    routine_exercises_json = [RutinaEjercicioJsonSchema().dump(routine_exercises) for routine_exercises in routine_exercises[index]]
    routine_json['lista_ejercicios'] = routine_exercises_json

    return routine_json

  def _exists_program_routines_assoc(self, routine_id_uuid):
    exists_assoc = False

    found_program_routine = None
    try:
      filter_expr = ProgramaRutinas.id_rutina == routine_id_uuid
      found_program_routine = db.session.query(ProgramaRutinas).filter(filter_expr).first()
    except Exception as ex:
      raise InternalServerError() from ex

    exists_assoc = found_program_routine != None

    return exists_assoc


routine_service = RoutineService()
