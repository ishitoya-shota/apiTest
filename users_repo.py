# users_repo.py
from __future__ import annotations
import json
import datetime as dt
from typing import Any, Optional

from sqlalchemy.engine import Row

from db import db_exec

def _now_iso(mysql: bool) -> str:
    now = dt.datetime.utcnow()
    if mysql:
        # MySQL DATETIME(6) には "YYYY-MM-DD HH:MM:SS.ffffff" 形式が相性良い
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")
    # SQLite は TEXT(ISO8601)で保存
    return now.isoformat(timespec="microseconds") + "Z"

def create_user(username: str, email: str, feature: Any | None, is_mysql: bool) -> None:
    now = _now_iso(is_mysql)
    feature_txt = json.dumps(feature, ensure_ascii=False) if isinstance(feature, (dict, list)) else (feature or None)

    if is_mysql:
        db_exec(
            "INSERT INTO users (username,email,feature,created_at,updated_at) "
            "VALUES (:username,:email,:feature,:created_at,:updated_at)",
            {"username": username, "email": email, "feature": feature_txt, "created_at": now, "updated_at": now},
        )
    else:
        db_exec(
            "INSERT INTO users (username,email,feature,created_at,updated_at) "
            "VALUES (:username,:email,:feature,:created_at,:updated_at)",
            {"username": username, "email": email, "feature": feature_txt, "created_at": now, "updated_at": now},
        )

def list_users() -> list[dict[str, Any]]:
    rows = db_exec("SELECT id, username, email, feature, created_at, updated_at FROM users ORDER BY id DESC").fetchall()
    return [_row_to_dict(r) for r in rows]

def get_user(user_id: int) -> Optional[dict[str, Any]]:
    row = db_exec(
        "SELECT id, username, email, feature, created_at, updated_at FROM users WHERE id=:id",
        {"id": user_id},
    ).fetchone()
    return _row_to_dict(row) if row else None

def update_user(user_id: int, fields: dict[str, Any], is_mysql: bool) -> None:
    if "feature" in fields and isinstance(fields["feature"], (dict, list)):
        fields["feature"] = json.dumps(fields["feature"], ensure_ascii=False)
    fields["updated_at"] = _now_iso(is_mysql)

    set_frag = ", ".join([f"{k}=:{k}" for k in fields.keys()])
    params = {**fields, "id": user_id}
    db_exec(f"UPDATE users SET {set_frag} WHERE id=:id", params)

def delete_user(user_id: int) -> None:
    db_exec("DELETE FROM users WHERE id=:id", {"id": user_id})

def _row_to_dict(row: Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    data = dict(row._mapping)  # SQLAlchemy 2.x Row -> dict
    # feature をJSON復元できれば戻す
    f = data.get("feature")
    if isinstance(f, str):
        try:
            data["feature"] = json.loads(f)
        except Exception:
            pass
    return data
