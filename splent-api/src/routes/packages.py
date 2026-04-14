from flask import Blueprint, jsonify
from src.services.package_service import get_packages, get_package_by_name

packages_bp = Blueprint("packages", __name__)


@packages_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@packages_bp.get("/packages")
def packages():
    return jsonify(get_packages()), 200


@packages_bp.get("/packages/<name>")
def package_by_name(name):
    package = get_package_by_name(name)

    if package is None:
        return jsonify({"error": "Package not found"}), 404

    return jsonify(package), 200