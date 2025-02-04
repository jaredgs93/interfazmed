from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

FASTAPI_UPLOAD_URL = "http://127.0.0.1:8000/upload/"
FASTAPI_QUESTIONS_URL = "http://127.0.0.1:8000/generate_questions"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/generate_questions", methods=["GET"])
def generate_questions():
    response = requests.get(FASTAPI_QUESTIONS_URL)
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({"error": "No se pudieron obtener preguntas"}), 500

@app.route("/upload", methods=["POST"])
def send_video():
    data = request.json
    video_base64 = data.get("video")
    questions = data.get("questions", "")

    if not video_base64:
        return jsonify({"error": "No se recibió un video"}), 400

    response = requests.post(FASTAPI_UPLOAD_URL, json={"video": video_base64, "questions": questions})

    if response.status_code == 200:
        return jsonify({"message": "✅ Video grabado satisfactoriamente"})
    else:
        return jsonify({"error": "❌ Error al enviar el video"}), 500

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
