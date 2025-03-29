from api_messages.base_api_error import ApiError


class TrainerAlreadyExists(ApiError):
  code = 409

  def __init__(self):
    self.message = "Entrenador ya existe."


class TrainerCreated:
  code = 201

  def __init__(self, trainer_id):
    self.message = "Entrenador creado exitosamente."
    self.trainer_id = trainer_id


class TrainersList:
  code = 200

  def __init__(self, found_trainers):
    self.trainers = found_trainers


class TrainerNotFound(ApiError):
  code = 401

  def __init__(self):
    self.message = "Entrenador no encontrado."


class TrainerFound:
  code = 200

  def __init__(self, found_trainer):
    self.trainer = found_trainer


class TrainerUpdated:
  code = 200

  def __init__(self):
    self.message = "Entrenador actualizado exitosamente."


class TrainerDeleted:
  code = 200

  def __init__(self):
    self.message = "Entrenador borrado exitosamente."
