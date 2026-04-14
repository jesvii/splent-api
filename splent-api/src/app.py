from flask import Flask
from src.config import Config
from src.routes.packages import packages_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(packages_bp, url_prefix="/api")

    return app