# users_routes.py
from __future__ import annotations
import os
from flask import Blueprint, request, jsonify

from users_repo import (
    create_user,
    list_users,
    get_user,
    update_user,
    delete_user,
)

users_bp = Blueprint("users", __name__)

def _is_mysql() -> bool:
    return os.getenv("DB_URL", "").strip().startswith("mysql")

@users_bp.route("", methods=["POST"])
def create_user_api():
    """
    JSON:
    {
      "username": "alice",
      "email": "alice@example.com",
      "feature": {"role":"admin"}
    }
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    feature = data.get("feature")

    if not username or not email:
        return jsonify({"error": "username and email are required"}), 400

    try:
        create_user(username, email, feature, _is_mysql())
    except Exception as e:
        return jsonify({"error": f"insert failed: {e}"}), 409

    return jsonify({"message": "created"}), 201

@users_bp.route("", methods=["GET"])
def list_users_api():
    return jsonify(list_users())

@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user_api(user_id: int):
    data = get_user(user_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data)

@users_bp.route("/<int:user_id>", methods=["PATCH", "PUT"])
def update_user_api(user_id: int):
    data = request.get_json(silent=True) or {}
    fields = {}
    for k in ("username", "email", "feature"):
        if k in data:
            fields[k] = data[k]
    if not fields:
        return jsonify({"error": "no fields to update"}), 400

    try:
        update_user(user_id, fields, _is_mysql())
    except Exception as e:
        return jsonify({"error": f"update failed: {e}"}), 409
    return jsonify({"message": "updated"})

@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user_api(user_id: int):
    delete_user(user_id)
    return jsonify({"message": "deleted"})
