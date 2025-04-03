from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from stegano import lsb
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/encode", methods=["POST"])
def encode():
    try:
        file = request.files["file"]
        text = request.form["text"]

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        encoded_image = lsb.hide(file_path, text)
        encoded_path = os.path.join(UPLOAD_FOLDER, "encoded_" + file.filename)
        encoded_image.save(encoded_path)

        return send_file(encoded_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/decode", methods=["POST"])
def decode():
    try:
        file = request.files["file"]

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        hidden_text = lsb.reveal(file_path)

        return jsonify({"text": hidden_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)