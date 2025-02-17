from fastapi import FastAPI, Request, UploadFile, Form, HTTPException
from fastapi.templating import Jinja2Templates
import shutil
from openai import OpenAI
import os
import base64
from pathlib import Path
import datetime
from decouple import config
import requests
import uvicorn
import json
import subprocess

# Configurar token y chat_id de Telegram
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
CHAT_ID = config('CHAT_ID')

print("TOKEN:", TELEGRAM_BOT_TOKEN)
print("CHAT ID:", CHAT_ID)


def send_telegram_notification(student_data):
    student_name = student_data["name"]
    student_career = student_data["career"]
    student_semester = student_data["semester"]
    message = f"🎥 {student_name} de la carrera de {student_career} (semestre {student_semester}) ha subido un nuevo video!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

import subprocess

def convert_to_mp4(input_path, output_path):
    """Convierte un video .webm a .mp4 usando ffmpeg."""
    try:
        command = [
            "ffmpeg",
            "-i", input_path,           # Archivo de entrada
            "-c:v", "libx264",         # Códec de video
            "-c:a", "aac",             # Códec de audio
            "-strict", "experimental",  # Modo experimental para AAC
            "-movflags", "+faststart",  # Optimiza el archivo para streaming
            output_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"✅ Video convertido a .mp4: {output_path}")
            return True
        else:
            print(f"❌ Error al convertir video: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️ Error ejecutando ffmpeg: {e}")
        return False


# Configurar API de OpenAI
client = OpenAI(api_key=config('OPENAI_API_KEY'))

app = FastAPI()

# Configurar las rutas de templates
templates = Jinja2Templates(directory="templates")

# Directorio para guardar videos
BASE_DIR = Path("uploaded_files")
BASE_DIR.mkdir(exist_ok=True)

# Ruta para la interfaz web principal
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para el aviso de privacidad
@app.get("/privacy")
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

# Ruta para la pantalla de éxito
@app.get("/success")
async def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

# Cargamos el .txt con la transcipción del video (con utf-8)
with open("transcription.txt", "r", encoding="utf-8") as f:
    transcription = f.read()

@app.get("/generate_questions")
async def generate_questions():
    completion = client.chat.completions.create(
            messages=[{'role': 'system', 'content': """Actúa como un profesor de medicina. Haz tres preguntas (en español) dirigidas a un estudiante de medicina sobre el resumen del episodio Derailed (S01E01) de la serie Chicago Med.
                                                          Las preguntas deben ir enfocadas en qué harían los estudiantes en diversas situaciones médicas y cómo resolverían los problemas que se presentan en el episodio.
                                                          La finalidad es evaluar diversas habilidades del estudiante, tales como toma de decisiones, negociación, liderazgo, creatividad.
                                                        Para apoyarte, aquí tienes la transcripción en inglés del resumen del episodio:""" + transcription}],
            model='gpt-3.5-turbo'
        )
    
    chat_response = completion.choices[0].message.content
    print(chat_response)
    return {"questions": chat_response}

# API para recibir videos y preguntas
@app.post("/upload")
async def upload_video(file: UploadFile = Form(...), questions: str = Form(...), student_name: str = Form(...), student_age: str = Form(...), student_gender : str = Form(...), student_career: str = Form(...), student_semester: str = Form(...)):
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_student_name = "_".join(student_name.split()).lower()  # Reemplaza espacios por guiones bajos
        upload_dir = BASE_DIR / f"upload_{safe_student_name}_{timestamp}"
        upload_dir.mkdir(exist_ok=True)

        # Guardar video en .webm
        webm_path = upload_dir / "video.webm"
        with open(webm_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        """# Convertir a .mp4
        mp4_path = upload_dir / f"{safe_student_name}_{timestamp}.mp4"
        if convert_to_mp4(str(webm_path), str(mp4_path)):
            print(f"✅ Video convertido y guardado en {mp4_path}")
            webm_path.unlink()  # Eliminar archivo .webm original
        else:
            raise HTTPException(status_code=500, detail="Error al convertir el video a .mp4")"""


        questions_path = upload_dir / "questions.txt"
        with open(questions_path, "w") as qf:
            qf.write(questions)
        
        # Crear un diccionario con los datos del estudiante
        student_data = {
            "name": student_name,
            "age": student_age,
            "gender": student_gender,
            "career": student_career,
            "semester": student_semester,
        }

        # Guardar los datos del estudiante en un archivo JSON
        student_data_path = upload_dir / "student_data.json"
        with open(student_data_path, "w") as sf:
            json.dump(student_data, sf, ensure_ascii= False)
        
        # Enviar notificación a Telegram
        try:
            send_telegram_notification(student_data)
        except Exception as e:
            print("Error al enviar notificación a Telegram", e)

        return {"message": "Video y preguntas guardados correctamente"}

    except Exception as e:
        print(e, "Error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
