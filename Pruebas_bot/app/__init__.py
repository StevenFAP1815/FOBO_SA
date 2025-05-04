from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint


def create_app():
    app = Flask(__name__)

    load_configurations(app) # Para cargar las configuraciones desde el archivo .env
    configure_logging()# Para depuración de errores
    
    app.register_blueprint(webhook_blueprint)# Esto es para registrar el blueprint en la aplicación y poder recibir las solicitudes en el webhook

    return app