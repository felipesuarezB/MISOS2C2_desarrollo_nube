from api_messages.base_api_error import ApiError


class PersonAlreadyExists(ApiError):
  code = 409

  def __init__(self):
    self.message = "Persona ya existe."


class PersonCreated:
  code = 201

  def __init__(self, person_id):
    self.message = "Persona creada exitosamente."
    self.person_id = person_id


class PersonsList:
  code = 200

  def __init__(self, found_persons):
    self.persons = found_persons


class PersonFound:
  code = 200

  def __init__(self, found_person):
    self.person = found_person


class PersonNotFound(ApiError):
  code = 404

  def __init__(self):
    self.message = "Persona no encontrada."


class PersonUpdated:
  code = 200

  def __init__(self):
    self.message = "Persona actualizada exitosamente."


class PersonDeleted:
  code = 200

  def __init__(self):
    self.message = "Persona borrada exitosamente."
