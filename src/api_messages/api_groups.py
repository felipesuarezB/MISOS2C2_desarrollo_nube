from api_messages.base_api_error import ApiError


class PersonAlreadyInGroup(ApiError):
  code = 409

  def __init__(self):
    self.message = "Persona ya se encuentra dentro del grupo del entrenador."


class PersonAddedToTrainerGroup:
  code = 200

  def __init__(self):
    self.message = "Persona agregada al grupo del entrenador."


class GroupPersonsList:
  code = 200

  def __init__(self, found_persons):
    self.persons = found_persons


class PersonRemovedFromTrainerGroup:
  code = 200

  def __init__(self):
    self.message = "Persona removida del grupo del entrenador."


class ChangeLogsList:
  code = 200

  def __init__(self, found_change_logs):
    self.change_logs = found_change_logs
