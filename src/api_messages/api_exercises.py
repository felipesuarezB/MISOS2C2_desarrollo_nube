from api_messages.base_api_error import ApiError


class ExerciseCreated:
  code = 201

  def __init__(self, exercise_id):
    self.message = "Ejercicio creado exitosamente."
    self.exercise_id = exercise_id


class ExercisesList:
  code = 200

  def __init__(self, found_exercises):
    self.exercises = found_exercises


class ExerciseFound:
  code = 200

  def __init__(self, found_exercise):
    self.exercise = found_exercise


class ExerciseNotFound(ApiError):
  code = 404

  def __init__(self):
    self.message = "Ejercicio no encontrado."


class ExerciseUpdated:
  code = 200

  def __init__(self):
    self.message = "Ejercicio actualizado exitosamente."


class ExerciseAssociatedWithRoutine(ApiError):
  code = 409

  def __init__(self):
    self.message = "Ejercicio asociado a rutina."


class ExerciseDeleted:
  code = 200

  def __init__(self):
    self.message = "Ejercicio borrado exitosamente."
