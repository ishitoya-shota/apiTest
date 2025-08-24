# db.py
from __future__ import annotations
import os
from typing import Any, Iterable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Result

# 接続先を環境変数で切替
# 例) MySQL: DB_URL=mysql+pymysql://appuser:password@localhost:3306/sampleapi
DB_URL = os.getenv("DB_URL", "").strip()
if not DB_URL:
    # デフォルトSQLite
    DB_URL = "sqlite:///app.sqlite3"

# エンジン作成（pool_pre_ping: MySQLでの切断検知用、future=True: 2.0 API）
engine: Engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

def db_exec(sql: str, params: dict[str, Any] | Iterable[Any] | None = None) -> Result:
    """
    書き込み系も読み取り系も begin トランザクション内で実行。
    """
    with engine.begin() as conn:
        return conn.execute(text(sql), params or {})

def init_db() -> None:
    """
    users テーブル作成（存在しなければ）
    - SQLite / MySQL どちらでも動く共通DDL
    - MySQL では ENGINE/CHARSET を追加
    """
    # DB方言差を最小にするため CREATE TABLE を二通りに分ける
    is_mysql = DB_URL.startswith("mysql")
    if is_mysql:
        ddl = """
        CREATE TABLE IF NOT EXISTS users (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          username VARCHAR(255) NOT NULL UNIQUE,
          email    VARCHAR(255) NOT NULL UNIQUE,
          feature  TEXT NULL,
          created_at DATETIME(6) NOT NULL,
          updated_at DATETIME(6) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    else:
        # SQLite 版
        ddl = """
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE,
          email    TEXT NOT NULL UNIQUE,
          feature  TEXT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        """
    db_exec(ddl)
