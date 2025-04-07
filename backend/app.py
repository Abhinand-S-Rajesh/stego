from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from PIL import Image
from stegano import lsb
import os
import uuid
import requests
import traceback

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
ENCODED_FOLDER = "encoded"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}

# Max upload size: 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def download_image_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch image from URL.")

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise Exception("URL does not point to a valid image.")

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
        file_path = None

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

        # Convert to PNG
        image = Image.open(file_path).convert("RGB")
        png_path = file_path.rsplit('.', 1)[0] + ".png"
        image.save(png_path, "PNG")

        # Check message size (very rough estimate)
        max_chars = os.path.getsize(png_path) // 3
        if len(text) > max_chars:
            return jsonify({"error": "Message too long for image capacity."}), 400

        # Encode
        encoded_image = lsb.hide(png_path, text)
        encoded_filename = f"encoded_{uuid.uuid4().hex}.png"
        encoded_path = os.path.join(ENCODED_FOLDER, encoded_filename)
        encoded_image.save(encoded_path)

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
                os.remove(png_path)
            except Exception:
                pass
            return response

        return jsonify({"download_url": f"/encoded/{encoded_filename}"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/decode", methods=["POST"])
def decode():
    try:
        file_path = None

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

        hidden_text = lsb.reveal(png_path)
        if hidden_text is None:
            return jsonify({"text": "", "warning": "No hidden message found."})

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
                os.remove(png_path)
            except Exception:
                pass
            return response

        return jsonify({"text": hidden_text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/encoded/<filename>")
def serve_encoded(filename):
    try:
        return send_file(os.path.join(ENCODED_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"File not found: {str(e)}"}), 404

if __name__ == "__main__":
    app.run(debug=False)
