from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()


<<<<<<< HEAD
def get_postgresql_url():
  """
  Connection string example: postgresql://username:password@host:port/dbname
  """
  db_user = os.getenv('DB_USER')
  db_password = os.getenv('DB_PASSWORD')
  db_host = os.getenv('DB_HOST')
  db_port = os.getenv('DB_PORT')
  db_name = os.getenv('DB_NAME')
  return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
=======
def get_database_url():
    """
    Retorna la URL de conexión a la base de datos según la configuración del entorno.
    Si DB_HOST es 'sqlite', usa SQLite, de lo contrario usa PostgreSQL.
    """
    db_host = os.getenv('DB_HOST')
    
    # Si estamos usando SQLite
    if db_host == 'sqlite':
        db_name = os.getenv('DB_NAME', 'dev.db')
        return f"sqlite:///{db_name}"
    
    # Si estamos usando PostgreSQL
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Mantener la función anterior para compatibilidad
def get_postgresql_url():
    return get_database_url()
>>>>>>> 47fc610810f8b86b252ef92c15c0c2d192f71e1e
