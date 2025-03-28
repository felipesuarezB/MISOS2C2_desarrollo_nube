import os
from flask import Flask, jsonify
from flask_smorest import Api

from apis.jugador_bp import jugadores_bp

from database import db, get_postgresql_url

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env.test
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env.test')
load_dotenv(dotenv_path)

def create_app():
  app = Flask(__name__)
  
  api = Api(app)
  api.register_blueprint(jugadores_bp)
  
  # Configuración de base de datos con SQLAlchemy (flask-sqlalchemy).
  if os.getenv('ENVIRONMENT') in ['test']:
    database_uri = ''
    if os.getenv('DB_HOST') in ['memory']:
      database_uri = 'sqlite:///:memory:'
    elif os.getenv('DB_HOST') in ['sqlite']:
      database_uri = 'sqlite:///test.db'
    else:
      database_uri = get_postgresql_url()
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  else:
    app.config['SQLALCHEMY_DATABASE_URI'] = get_postgresql_url()
    
  if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"), port=int(os.getenv("FLASK_RUN_PORT", 8000)), debug=True)
    
  # Inicialización flask-sqlalchemy extension y creación de esquemas de base de datos.
  db.init_app(app)
  with app.app_context():
    db.create_all()
    
  app = create_app()
    