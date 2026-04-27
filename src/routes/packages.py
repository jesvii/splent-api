from flask import Blueprint, jsonify, request
from src.services.package_service import get_packages, get_package_by_name, publish_package, update_package, delete_package

packages_bp = Blueprint("packages", __name__)


@packages_bp.get("/packages")
def packages():
    return jsonify(get_packages()), 200


@packages_bp.get("/packages/<name>")
def package_by_name(name):
    package = get_package_by_name(name)

    if package is None:
        return jsonify({"error": "Package not found"}), 404

    return jsonify(package), 200

@packages_bp.post("/packages")
def create_package():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    try:
        package = publish_package(data)
        return jsonify(package), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify(
            {
                "error": "Error publishing package",
                "details": str(e),
            }
        ), 500   
    
@packages_bp.put("/packages/<name>")
def edit_package(name):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    try:
        package = update_package(name, data)
        return jsonify(package), 200
    except FileNotFoundError:
        return jsonify({"error": "Package not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify(
            {
                "error": "Error updating package",
                "details": str(e),
            }
        ), 500   
    
@packages_bp.delete("/packages/<name>")
def delete_package_by_name(name):
    try:
        delete_package(name)
        return jsonify({"message": "Package deleted successfully"}), 200
    except FileNotFoundError:
        return jsonify({"error": "Package not found"}), 404
    except Exception as e:
        return jsonify(
            {
                "error": "Error deleting package",
                "details": str(e),
            }
        ), 500