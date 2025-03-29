from api_messages.base_api_error import ApiError


class ProgramCreated:
  code = 201

  def __init__(self, program_id):
    self.message = "Programa creado exitosamente."
    self.program_id = program_id


class ProgramsList:
  code = 200

  def __init__(self, found_programs):
    self.programs = found_programs


class ProgramFound:
  code = 200

  def __init__(self, found_program):
    self.program = found_program


class ProgramNotFound(ApiError):
  code = 404

  def __init__(self):
    self.message = "Programa no encontrado."


class ProgramUpdated:
  code = 200

  def __init__(self):
    self.message = "Programa actualizado exitosamente."


class ProgramDeleted:
  code = 200

  def __init__(self):
    self.message = "Programa borrado exitosamente."
