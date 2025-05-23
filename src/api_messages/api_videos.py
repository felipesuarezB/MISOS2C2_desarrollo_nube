from src.api_messages.base_api_error import ApiError

class VideoFailed(ApiError):
  code = 400

  def __init__(self):
    self.message = "Error en el archivo (tipo o tamaño inválido)."

class VideoUploaded:
  code = 201

  def __init__(self, video_id):
    self.message = "Video subido exitosamente, tarea creada."
    self.video_id = video_id
    
class VideoListed:
  code = 200

  def __init__(self, jugadoresList):
    self.message = "Lista de videos obtenida."
    self.videjugadoresListo_id = jugadoresList
    
class AuthFailed(ApiError):
  code = 401

  def __init__(self):
    self.message = "Falta de autenticación."
    
class VideoDeleted:
  code = 200

  def __init__(self, id_video):
    self.message = "Video borrado exitosamente."
    self.id_video = id_video

class VideoVoted:
  code = 200

  def __init__(self):
    self.message = "Voto exitoso."

class VideoRanking:
  code = 200

  def __init__(self, ranking):
    self.message = "Lista de rankings obtenida."
    self.ranking = ranking

class ForbiddenOperation:
  code = 404
  def __init__(self):
    self.message = "El usuario ya voto"

class UsserIssue:
  code = 404
  def __init__(self):
    self.message = "Usuario no existe"

class VideoIssue:
  code = 404
  def __init__(self):
    self.message = "Video no existe"