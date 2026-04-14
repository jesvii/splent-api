from flask import Blueprint, jsonify
from src.services.package_service import get_packages

packages_bp = Blueprint("packages", __name__)


@packages_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@packages_bp.get("/packages")
def packages():
    return jsonify(get_packages()), 200