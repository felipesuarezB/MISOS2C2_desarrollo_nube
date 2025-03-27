from api_messages.base_api_error import ApiError


class UserAlreadyExists(ApiError):
  code = 409

  def __init__(self):
    self.message = "Usuario ya existe."


class UserCreated:
  code = 201

  def __init__(self, user_id, user_role):
    self.message = "Usuario creado exitosamente."
    self.user_id = user_id
    self.user_role = user_role


class UserAuthFailed(ApiError):
  code = 401

  def __init__(self):
    self.message = "Autenticación de usuario no exitosa."


class UserAuthSucceed:
  code = 200

  def __init__(self, user_id, user_role):
    self.message = "Autenticación de usuario exitosa."
    self.user_id = user_id
    self.user_role = user_role


class UserPasswordUpdated:
  code = 200

  def __init__(self, user_id, user_role):
    self.message = "Contraseña de usuario actualizada exitosamente."
    self.user_id = user_id
    self.user_role = user_role


class UserNotFound(ApiError):
  code = 401

  def __init__(self):
    self.message = "Usuario no encontrado."


class UserFound:
  code = 200

  def __init__(self, found_user):
    self.user = found_user
