from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()


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
