
# 簡単なAPIを作って curl を試す方法

## 1. まずはローカルに簡単なAPIを立てる

# app.py
from __future__ import annotations
import os
import pathlib
from flask import Flask, jsonify, request
from werkzeug.datastructures import FileStorage
import datetime

from db import init_db
from users_routes import users_bp

app = Flask(__name__)

# アップロード先
UPLOAD_DIR = pathlib.Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from API!"})

@app.route("/upload", methods=["POST"])
def upload():
    loginuser = request.form.get("loginuser")
    feature = request.form.get("feature")
    #「file :」の「：」は型アノテーション。
    # 代入に加えて「この変数は FileStorage 型か None 型のどちらかになりますよ」という 型ヒント をつけている。
    # FileStorage は　アップロードファイルを表すクラス。ただし、このクラスはFlaskの機能。
    file: FileStorage | None = request.files.get("data")

    saved_name = None
    if file and file.filename:
        # 同名衝突回避のため簡易タイムスタンプ付与
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        # f文字列 (f-string)を使っている
        # 変数を文字列として扱いたいときも使う
        # 今回でいうと、"20250828223015987654_test.png"みたいな文字列になる
        saved_name = f"{ts}_{file.filename}"
        file.save(UPLOAD_DIR / saved_name)

    # 201はステータスコードを表している
    # 201 はレスポンスヘッダのステータス行に出るだけ
    # なのでJsonの中身には入らない
    return jsonify({
        "loginuser": loginuser,
        "feature": feature,
        "filename": saved_name
    }), 201

# /users ルート群を登録
app.register_blueprint(users_bp, url_prefix="/users")

if __name__ == "__main__":
    # アプリ起動時にテーブルを作成（存在しなければ）
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)

# 以下は実際に実行したcurlコマンドの例と出力

# curl -X POST http://127.0.0.1:5000/upload \
#   -F "loginuser=testuser" \
#   -F "feature={\"key\":\"id\", \"value\":\"big\"}" \
#   -F "data=@test.txt"

# 出力
# {
#   "feature": "{\"key\":\"id\", \"value\":\"big\"}",
#   "filename": "test.txt",
#   "loginuser": "testuser"
# }


# curl -sS -X POST \
#   -F 'loginuser=testuser' \
#   --form-string 'feature=[{"key":"id","value":"big"}]' \
#   -F 'data=@test.txt' \
#   -i \
#   -w '\n--> %{http_code} | %{content_type}\n' \
#   http://127.0.0.1:5000/upload 

# HTTP/1.1 200 OK
# Server: Werkzeug/3.1.3 Python/3.12.10
# Date: Wed, 20 Aug 2025 14:55:20 GMT
# Content-Type: application/json
# Content-Length: 109
# Connection: close

# 出力
# {
#   "feature": "[{\"key\":\"id\",\"value\":\"big\"}]",
#   "filename": "test.txt",
#   "loginuser": "testuser"
# }
