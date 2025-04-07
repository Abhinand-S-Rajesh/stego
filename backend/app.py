from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
from stegano import lsb
import os
import uuid
import requests

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
ENCODED_FOLDER = "encoded"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def download_image_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch image from URL.")
    ext = url.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise Exception("Unsupported image format from URL.")
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

@app.route("/api/encode", methods=["POST"])
def encode():
    try:
        text = request.form["text"]
        if "file" in request.files:
            file = request.files["file"]
            if not allowed_file(file.filename):
                return jsonify({"error": "Unsupported image format"}), 400
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        elif "url" in request.form:
            url = request.form["url"]
            file_path = download_image_from_url(url)
        else:
            return jsonify({"error": "No image provided"}), 400

        # Convert to PNG for LSB
        image = Image.open(file_path).convert("RGB")
        png_path = file_path.rsplit('.', 1)[0] + ".png"
        image.save(png_path, "PNG")

        # Encode
        encoded_image = lsb.hide(png_path, text)
        encoded_filename = f"encoded_{uuid.uuid4().hex}.png"
        encoded_path = os.path.join(ENCODED_FOLDER, encoded_filename)
        encoded_image.save(encoded_path)

        return send_file(encoded_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/decode", methods=["POST"])
def decode():
    try:
        if "file" in request.files:
            file = request.files["file"]
            if not allowed_file(file.filename):
                return jsonify({"error": "Unsupported image format"}), 400
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        elif "url" in request.form:
            url = request.form["url"]
            file_path = download_image_from_url(url)
        else:
            return jsonify({"error": "No image provided"}), 400

        image = Image.open(file_path).convert("RGB")
        png_path = file_path.rsplit('.', 1)[0] + ".png"
        image.save(png_path, "PNG")

        # Decode
        hidden_text = lsb.reveal(png_path)
        if hidden_text is None:
            return jsonify({"text": "", "warning": "No hidden message found."})

        return jsonify({"text": hidden_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
