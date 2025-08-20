
# 簡単なAPIを作って curl を試す方法

## 1. まずはローカルに簡単なAPIを立てる

from flask import Flask, request, jsonify

app = Flask(__name__)

# GET で呼び出すAPI
@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from API!"})

# POST で呼び出すAPI
@app.route("/upload", methods=["POST"])
def upload():
    loginuser = request.form.get("loginuser")
    feature = request.form.get("feature")
    file = request.files.get("data")

    return jsonify({
        "loginuser": loginuser,
        "feature": feature,
        "filename": file.filename if file else None
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

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
