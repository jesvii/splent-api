from hmac import compare_digest

from flask import Flask, jsonify, request
from src.config import Config
from src.routes.packages import packages_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.sort_keys = False

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.before_request
    def require_bearer_token():
        token = app.config.get("SPLENT_API_TOKEN")
        if not token or not request.path.startswith("/api/"):
            return None

        auth_header = request.headers.get("Authorization", "")
        scheme, _, supplied_token = auth_header.partition(" ")
        #if scheme.lower() != "bearer" or supplied_token != token:
        if scheme.lower() != "bearer" or not compare_digest(supplied_token, token):
            return jsonify({"error": "Unauthorized"}), 401

        return None

    app.register_blueprint(packages_bp, url_prefix="/api")

    return app
