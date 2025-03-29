from api_messages.base_api_error import ApiError


class RoutineCreated:
  code = 201

  def __init__(self, routine_id):
    self.message = "Rutina creada exitosamente."
    self.routine_id = routine_id


class RoutinesList:
  code = 200

  def __init__(self, found_routines):
    self.routines = found_routines


class RoutineFound:
  code = 200

  def __init__(self, found_routine):
    self.routine = found_routine


class RoutineNotFound(ApiError):
  code = 404

  def __init__(self):
    self.message = "Rutina no encontrada."


class RoutineUpdated:
  code = 200

  def __init__(self):
    self.message = "Rutina actualizada exitosamente."


class RoutineAssociatedWithProgram(ApiError):
  code = 409

  def __init__(self):
    self.message = "Rutina asociada a programa."


class RoutineDeleted:
  code = 200

  def __init__(self):
    self.message = "Rutina borrada exitosamente."
