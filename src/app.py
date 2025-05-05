import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import logging

from src.database import db, get_database_url
from src.apis.health_bp import health_bp
from src.apis.jugador_bp import jugadores_bp
from src.apis.video_bp import videos_bp
from src.api_messages.base_api_error import ApiError
from src.api_messages.api_errors import TokenNotFound, TokenInvalidOrExpired
from src.tasks.celery_worker import celery

from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.url import make_url
import psycopg2

def create_database_if_not_exists(db_uri):
    url = make_url(db_uri)
    db_name = url.database

    # Conectarse a la base 'postgres' para gestionar otras bases
    url = url.set(database="postgres")

    try:
        conn = psycopg2.connect(
            dbname=url.database,
            user=url.username,
            password=url.password,
            host=url.host,
            port=url.port,
        )
        conn.set_session(autocommit=True)
        cur = conn.cursor()

        # Verificar si ya existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()

        if not exists:
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✔ Base de datos '{db_name}' creada exitosamente.")
        else:
            print(f"ℹ La base de datos '{db_name}' ya existe.")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")


def create_app():
    app = Flask(__name__)

    # Configuración de OpenAPI y Swagger
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
        db_uri = get_database_url()
        create_database_if_not_exists(db_uri)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    # Inicialización de SQLAlchemy
    db.init_app(app)
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            db.create_all()

    # CORS
    CORS(app,
         resources={r"/*": {"origins": "*"}},
         expose_headers=["Authorization"],
         supports_credentials=True)

    # JWT
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
    return jsonify(err.__dict__), err.code

@jwt.unauthorized_loader
def unauthorized_callback(reason):
    app.logger.error(f"unauthorized_loader: {reason}")
    err = TokenNotFound()
    return jsonify(err.__dict__), err.code

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    app.logger.error(f"invalid_token_loader: {reason}")
    err = TokenInvalidOrExpired()
    return jsonify(err.__dict__), err.code

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    err = TokenInvalidOrExpired()
    return jsonify(err.__dict__), err.code
