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

