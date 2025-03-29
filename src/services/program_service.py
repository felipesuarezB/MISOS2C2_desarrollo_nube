import uuid

from models.usuario import RolUsuario
from models.programa import Programa, ProgramaRutinas, ProgramaJsonSchema
from models.rutina import Rutina, RutinaEjercicios, RutinaJsonSchema
from models.ejercicio import Ejercicio, EjercicioJsonSchema
from api_messages.api_programs import ProgramCreated, ProgramsList, ProgramFound, ProgramNotFound
from api_messages.api_programs import ProgramUpdated, ProgramDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation
from database import db


class ProgramService:

  def __init__(self):
    pass

  def create_program(self, new_program, jwt_payload):
    if 'nombre' not in new_program:
      raise InvalidRequestBody()
    if 'descripcion' not in new_program:
      raise InvalidRequestBody()
    if 'dias_programa' not in new_program:
      raise InvalidRequestBody()
    if 'lista_rutinas_por_dia' not in new_program:
      raise InvalidRequestBody()

    if new_program['dias_programa'] != len(new_program['lista_rutinas_por_dia']):
      raise InvalidRequestBody()

    program_routines_ids_uuids = self._parse_program_routines_ids_uuids(new_program)

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    program = Programa(id=uuid.uuid4(),
                       nombre=new_program['nombre'],
                       descripcion=new_program['descripcion'],
                       dias_programa=new_program['dias_programa'])

    program_routines = []
    for routine_id_uuid in program_routines_ids_uuids:
      new_program_routine = ProgramaRutinas(id_programa=program.id, id_rutina=routine_id_uuid)
      program_routines.append(new_program_routine)

    try:
      db.session.add(program)
      for program_routine in program_routines:
        db.session.add(program_routine)

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return ProgramCreated(program.id)

  def list_programs(self, jwt_payload):
    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_programs = []
    try:
      found_programs = db.session.query(Programa).all()
    except Exception as ex:
      raise InternalServerError() from ex

    all_routines = []
    all_exercises = []
    for program in found_programs:
      program_routines = self._find_program_routines_details(program.id)
      all_routines.append(program_routines)

      routines_exercises = self._find_routines_exercises_details(program_routines)
      all_exercises.append(routines_exercises)

    programs_json = []
    for index, program in enumerate(found_programs):
      program_json = self._parse_program_json(program, index, all_routines, all_exercises)
      programs_json.append(program_json)

    return ProgramsList(programs_json)

  def get_program(self, id, jwt_payload):
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

    found_program = self._find_program_by_id(path_id_uuid)

    if found_program is None:
      raise ProgramNotFound()

    all_routines = self._find_program_routines_details(found_program.id)
    all_exercises = self._find_routines_exercises_details(all_routines)

    found_program_json = self._parse_program_json(found_program, 0, [all_routines], [all_exercises])

    return ProgramFound(found_program_json)

  def update_program(self, id, updated_program, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    if 'dias_programa' not in updated_program:
      raise InvalidRequestBody()
    if 'lista_rutinas_por_dia' not in updated_program:
      raise InvalidRequestBody()

    if updated_program['dias_programa'] != len(updated_program['lista_rutinas_por_dia']):
      raise InvalidRequestBody()

    program_routines_ids_uuids = self._parse_program_routines_ids_uuids(updated_program)

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_program = self._find_program_by_id(path_id_uuid)

    if found_program is None:
      raise ProgramNotFound()

    found_program_routines = self._find_program_routines(found_program.id)

    updated_program_routines = []
    for index, _ in enumerate(updated_program['lista_rutinas_por_dia']):
      program_routine = ProgramaRutinas(id_programa=found_program.id,
                                        id_rutina=program_routines_ids_uuids[index])
      updated_program_routines.append(program_routine)

    try:
      if 'nombre' in updated_program:
        found_program.nombre = updated_program['nombre']
      if 'descripcion' in updated_program:
        found_program.descripcion = updated_program['descripcion']
      if 'dias_programa' in updated_program:
        found_program.dias_programa = updated_program['dias_programa']

      for program_routines in found_program_routines:
        db.session.delete(program_routines)

      for program_routines in updated_program_routines:
        db.session.add(program_routines)

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return ProgramUpdated()

  def delete_program(self, id, jwt_payload):
    path_id_uuid = None
    try:
      path_id_uuid = uuid.UUID(id)
    except Exception as ex:
      raise InvalidUrlPathParams() from ex

    token_user_role = jwt_payload['user_role']

    if token_user_role not in [RolUsuario.ADMINISTRADOR_GIMNASIO.value,
                               RolUsuario.ENTRENADOR.value]:
      raise ForbiddenOperation()

    found_program = self._find_program_by_id(path_id_uuid)

    if found_program is None:
      raise ProgramNotFound()

    try:
      del_filter_expr = ProgramaRutinas.id_programa == found_program.id
      db.session.query(ProgramaRutinas).filter(del_filter_expr).delete()

      db.session.delete(found_program)

      db.session.commit()
    except Exception as ex:
      db.session.rollback()
      raise InternalServerError() from ex

    return ProgramDeleted()

  def _parse_program_routines_ids_uuids(self, program_json):
    program_routines_ids_uuids = []
    for program_routine_json in program_json['lista_rutinas_por_dia']:
      try:
        routine_id_uuid = uuid.UUID(program_routine_json['id'])
      except Exception as ex:
        raise InvalidRequestBody() from ex

      program_routines_ids_uuids.append(routine_id_uuid)

    return program_routines_ids_uuids

  def _find_program_by_id(self, program_id_uuid):
    found_program = None
    try:
      filter_expr = Programa.id == program_id_uuid
      found_program = db.session.query(Programa).filter(filter_expr).first()
    except Exception as ex:
      raise InternalServerError() from ex

    return found_program

  def _find_program_routines_details(self, program_id_uuid):
    found_program_routines = []
    try:
      query_expr = [Rutina.id, Rutina.nombre, Rutina.total_minutos, ProgramaRutinas.id_rutina]
      on_clause = ProgramaRutinas.id_rutina == Rutina.id
      filter_expr = ProgramaRutinas.id_programa == program_id_uuid
      found_program_routines = db.session.query(*query_expr).join(Rutina, on_clause).filter(filter_expr).all()
    except Exception as ex:
      raise InternalServerError() from ex

    return found_program_routines

  def _find_routines_exercises_details(self, program_routines):
    found_routines_exercises = []
    for routine in program_routines:
      try:
        query_expr = [Ejercicio.id, Ejercicio.nombre, Ejercicio.calorias_por_repeticion, RutinaEjercicios.id_ejercicio]
        on_clause = RutinaEjercicios.id_ejercicio == Ejercicio.id
        filter_expr = RutinaEjercicios.id_rutina == routine.id
        found_routine_exercises = db.session.query(*query_expr).join(Ejercicio, on_clause).filter(filter_expr).all()
      except Exception as ex:
        raise InternalServerError() from ex

      found_routines_exercises.append(found_routine_exercises)

    return found_routines_exercises

  def _find_program_routines(self, program_id_uuid):
    found_program_routines = []
    try:
      filter_expr = ProgramaRutinas.id_programa == program_id_uuid
      found_program_routines = db.session.query(ProgramaRutinas).filter(filter_expr).all()
    except Exception as ex:
      raise InternalServerError() from ex

    return found_program_routines

  def _parse_program_json(self, program, program_idx, programs_routines, routines_exercises):
    program_json = ProgramaJsonSchema().dump(program)
    program_routines_json = [RutinaJsonSchema().dump(program_routines) for program_routines in programs_routines[program_idx]]
    program_json['lista_rutinas_por_dia'] = program_routines_json

    for routine_idx, routine_json in enumerate(program_routines_json):
      routine_exercises_json = [EjercicioJsonSchema().dump(exercise) for exercise in routines_exercises[program_idx][routine_idx]]
      routine_json['lista_ejercicios'] = routine_exercises_json

    return program_json


program_service = ProgramService()
