from api_messages.base_api_error import ApiError


class InvalidRequestBody(ApiError):
  code = 400

  def __init__(self):
    self.message = "Alguno de los campos requeridos no está presente en la solicitud o no tiene el formato esperado."


class InvalidQueryStringParams(ApiError):
  code = 400

  def __init__(self):
    self.message = "Alguno de los campos en el URL query string no tiene el formato esperado."


class InvalidUrlPathParams(ApiError):
  code = 400

  def __init__(self):
    self.message = "Alguno de los campos en el URL path no tiene el formato esperado."


class InvalidTokenPayloadParams(ApiError):
  code = 400

  def __init__(self):
    self.message = "Alguno de los campos en el payload del token JWT no tiene el formato esperado."


class TokenInvalidOrExpired(ApiError):
  code = 401

  def __init__(self):
    self.message = "Token inválido o expirado."


class TokenNotFound(ApiError):
  code = 403

  def __init__(self):
    self.message = "No hay token en la solicitud."


class ForbiddenOperation(ApiError):
  code = 403

  def __init__(self):
    self.message = "No está permitida la operación para el rol del usuario."


class InternalServerError(ApiError):
  code = 500

  def __init__(self):
    self.message = "Error interno del servicio."
