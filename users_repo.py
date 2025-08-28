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

# Optionalは型ヒント。Noneを含む可能性があるときに使われる
def get_user(user_id: int) -> Optional[dict[str, Any]]:
    row = db_exec(
        "SELECT id, username, email, feature, created_at, updated_at FROM users WHERE id=:id",
        {"id": user_id},
    ).fetchone()
    return _row_to_dict(row) if row else None

# 「-> None」の意味として、処理結果は返さないことを想定している
def update_user(user_id: int, fields: dict[str, Any], is_mysql: bool) -> None:
    #  feature キーが fields に含まれていて、値が dict または list なら： その値を json.dumps(...) で JSON文字列に変換。
    if "feature" in fields and isinstance(fields["feature"], (dict, list)):
        fields["feature"] = json.dumps(fields["feature"], ensure_ascii=False)
    # _now_iso(is_mysql) は「今の時刻をISOフォーマット文字列で返す」関数。
    # is_mysql=True なら MySQL 互換フォーマット
    # False なら SQLite/Postgres 互換フォーマット
    fields["updated_at"] = _now_iso(is_mysql)

#　update_user関数の使用イメージ
# fields = {"username": "bob", "feature": {"role": "editor"}}
# update_user(1, fields, is_mysql=True)

# # ここで fields の中身はこうなっている：
# {
#   "username": "bob",
#   "feature": '{"role": "editor"}',
#   "updated_at": "2025-08-28 22:50:30"  # _now_isoの結果
# }
# # → この辞書を使って UPDATE users SET ... WHERE id=1 を実行する


    set_frag = ", ".join([f"{k}=:{k}" for k in fields.keys()])
    params = {**fields, "id": user_id}
    db_exec(f"UPDATE users SET {set_frag} WHERE id=:id", params)

def delete_user(user_id: int) -> None:
    db_exec("DELETE FROM users WHERE id=:id", {"id": user_id})

# データベースから取得した1行（Rowオブジェクト）を Python の辞書型に変換する処理
# SQLAlchemyの結果を「APIで返せる形（dict）」に整えるヘルパー関数
def _row_to_dict(row: Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    # SQLAlchemy 2.x Row -> dict
    data = dict(row._mapping)
    # feature をJSON復元できれば戻す
    f = data.get("feature")
    if isinstance(f, str):
        try:
            data["feature"] = json.loads(f)
        except Exception:
            pass
    return data
