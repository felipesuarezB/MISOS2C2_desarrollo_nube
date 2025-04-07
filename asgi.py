from asgiref.wsgi import WsgiToAsgi
from src.app import create_app

flask_app, _ = create_app()
asgi_app = WsgiToAsgi(flask_app) 