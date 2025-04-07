import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
import logging
from src.database import db, get_database_url
from src.apis.health_bp import health_bp
from src.apis.jugador_bp import jugadores_bp
from src.apis.video_bp import videos_bp
from src.api_messages.base_api_error import ApiError
from src.api_messages.api_errors import TokenNotFound, TokenInvalidOrExpired
from src.tasks.celery_worker import celery


def create_app():
    app = Flask(__name__)

    # Configuración de endpoints OpenAPI y Swagger
    app.config['API_TITLE'] = 'API Backend App ANB Rising Stars Showcase'
    app.config['API_VERSION'] = '1.0.0'
    app.config['OPENAPI_VERSION'] = "3.0.2"
    app.config['OPENAPI_JSON_PATH'] = "api-spec.json"
    app.config['OPENAPI_URL_PREFIX'] = "/"
    app.config['OPENAPI_SWAGGER_UI_PATH'] = "/swagger-ui"
    app.config['OPENAPI_SWAGGER_UI_URL'] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Registro de blueprints
    api = Api(app)
    api.register_blueprint(health_bp)
    api.register_blueprint(jugadores_bp)
    api.register_blueprint(videos_bp)

    # Configuración de base de datos
    if os.getenv('ENVIRONMENT') in ['test']:
        database_uri = ''
        if os.getenv('DB_HOST') in ['memory']:
            database_uri = 'sqlite:///:memory:'
        elif os.getenv('DB_HOST') in ['sqlite']:
            database_uri = 'sqlite:///' + os.getenv('DB_NAME', 'test.db')
        else:
            database_uri = get_database_url()
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()

    # Inicialización de SQLAlchemy
    db.init_app(app)
    with app.app_context():
        db.create_all()


    cors = CORS(app,
                resources={r"/*": {"origins": "*"}},
                expose_headers=["Authorization"],
                supports_credentials=True)

  
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager()
    jwt.init_app(app)

    return app, jwt

app, jwt = create_app()

def init_celery(celery, app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

init_celery(celery, app)



@app.errorhandler(ApiError)
def handle_exception(err):
    app.logger.error(f"{type(err)} - {err}")
    if err.__cause__ is not None:
        app.logger.error(err.__cause__)

    err_json = jsonify(err.__dict__)
    return err_json, err.code


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    app.logger.error(f"unauthorized_loader: {reason}")
    err = TokenNotFound()
    err_json = jsonify(err.__dict__)
    return err_json, err.code


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    app.logger.error(f"invalid_token_loader: {reason}")
    err = TokenInvalidOrExpired()
    err_json = jsonify(err.__dict__)
    return err_json, err.code


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    err = TokenInvalidOrExpired()
    err_json = jsonify(err.__dict__)
    return err_json, err.code


