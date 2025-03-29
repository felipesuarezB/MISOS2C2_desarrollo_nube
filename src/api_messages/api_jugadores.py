from api_messages.base_api_error import ApiError


class JugadorCreado:
  code = 201

  def __init__(self, user_id):
    self.message = "Usuario creado exitosamente."
    self.user_id = user_id
    