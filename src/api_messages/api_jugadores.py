from api_messages.base_api_error import ApiError

class UserAlreadyExists(ApiError):
  code = 409

  def __init__(self):
    self.message = "Usuario ya existe."

class JugadorCreado:
  code = 201

  def __init__(self, user_id):
    self.message = "Usuario creado exitosamente."
    self.user_id = user_id
    
class UserAuthFailed(ApiError):
  code = 401

  def __init__(self):
    self.message = "Autenticación de usuario no exitosa."


class UserAuthSucceed:
  code = 200

  def __init__(self, user_id, token):
    self.message = "Autenticación de usuario exitosa."
    self.user_id = user_id,
    self.token_type = "Bearer",
    self.expires_in = 3600,
    self.token = token