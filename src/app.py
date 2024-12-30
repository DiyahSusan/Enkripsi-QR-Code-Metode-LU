import os
from flask import Flask, render_template, request, jsonify
from encrypt_program import (
    generate_qr_code, 
    load_encrypted_data_from_image, 
    lu_decrypt, 
    lu_encrypt, 
    save_encrypted_data, 
    save_qr_image
)
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")

CORS(app)

UPLOAD_FOLDER = "upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file part in the request."}), 400
        
        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({"success": False, "error": "No selected file."}), 400
        
        # Save the file to the upload folder
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        return jsonify({"success": True, "file_path": file_path})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/generate", methods=["POST"])
def generate_qr():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"success": False, "error": "Message is required."}), 400

        # generate QR Code
        qr_matrix = generate_qr_code(message)

        save_qr_image(qr_matrix, "static/generated_qr.png")

        # encrypt QR Code
        encrypted_data = lu_encrypt(qr_matrix)

        save_encrypted_data(encrypted_data, "static/encrypted_qr.png")
        encrypted_image = np.array(Image.open("static/encrypted_qr.png"))

        # convert menjadi Base64
        buffer = BytesIO()
        Image.fromarray((qr_matrix * 255).astype(np.uint8)).save(buffer, format="PNG")
        original_base64 = base64.b64encode(buffer.getvalue()).decode()

        buffer = BytesIO()
        Image.fromarray(encrypted_image).save(buffer, format="PNG")
        encrypted_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "qr_code": original_base64,
            "enc_qr": encrypted_base64
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/decrypt", methods=["POST"])
def decrypt_qr():
    try:
        files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if f.endswith(".png")]
        if not files:
            return jsonify({"success": False, "error": "No uploaded files found."})

        # ambil file paling baru
        latest_file = max(
            [os.path.join(app.config["UPLOAD_FOLDER"], f) for f in files],
            key=os.path.getctime
        )
        print(f"Decrypting file: {latest_file}")

        # load gambar yang telah di enkripsi
        loaded_encrypted_data = load_encrypted_data_from_image(latest_file)

        # decrypt
        print("\nDecrypting...")
        decrypted_matrix = lu_decrypt(loaded_encrypted_data)
        save_qr_image(decrypted_matrix, "static/decrypted_qr.png")

        # convert menjadi Base64
        decrypted_image = np.array(Image.open("static/decrypted_qr.png"))
        buffer = BytesIO()
        Image.fromarray(decrypted_image).save(buffer, format="PNG")
        decrypted_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "dec_qr": decrypted_base64
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
