from flask import jsonify, make_response
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from flask_smorest import Blueprint
from models.video import VideoJsonSchema
from services.video_service import video_service


videos_bp = Blueprint("videos", __name__, url_prefix='/api', description="API de videos.")

@videos_bp.route('/videos/upload', methods=['POST'])
@videos_bp.arguments(VideoJsonSchema)
@jwt_required()
def upload_video(uploadVideo):
    
    result = video_service.save_video(uploadVideo)
    res_json = jsonify(result.__dict__)
    res = make_response(res_json, result.code)

    return res

@videos_bp.route('/videos', methods=['GET'])
@jwt_required()
def upload_video():
    jwt_payload = get_jwt()
    result = video_service.list_videos(jwt_payload)
    res_json = jsonify(result.__dict__)
    res = make_response(res_json, result.code)

    return res

@videos_bp.route('/public/videos', methods=['GET'])
@jwt_required()
def public_video():
    jwt_payload = get_jwt()
    result = video_service.list_public_videos(jwt_payload)
    res_json = jsonify(result.__dict__)
    res = make_response(res_json, result.code)

    return res

@videos_bp.route('/public/videos/<string:id>/vote', methods=['POST'])
@jwt_required()
def vote_video(id):
    # 🔹 Extraer el username desde el JWT
    username = get_jwt_identity()
    print(f"👤 Username extraído del JWT: {username} (tipo: {type(username)})")

    # 🔹 Llamar al servicio de votos
    result = video_service.vote_video(id, username)

    # 🔹 Crear la respuesta JSON
    res_json = jsonify(result.__dict__)
    return make_response(res_json, result.code)

@videos_bp.route('/public/rankings', methods=['GET'])
@jwt_required()
def ranking_videos():
    jwt_payload = get_jwt()
    result = video_service.list_ranking_videos(jwt_payload)
    res_json = jsonify(result.__dict__)
    res = make_response(res_json, result.code)

    return res

@videos_bp.route('/videos/<string:id>')
class VideosResources(MethodView):
    
    @jwt_required()
    def get(self, id):
        result = video_service.get_video(id)
        res_json = jsonify(result.videjugadoresListo_id)
        res = make_response(res_json, result.code)

        return res
    
    @jwt_required()
    def delete(self, id):
        result = video_service.delete_video(id)
        res_json = jsonify(result.__dict__)

        return res_json, result.code
    
    
    
