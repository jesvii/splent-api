from flask import Blueprint, jsonify

packages_bp = Blueprint("packages", __name__)

@packages_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200