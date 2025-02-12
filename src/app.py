from fastapi import FastAPI, Request, UploadFile, Form, HTTPException
from fastapi.templating import Jinja2Templates
import shutil
from openai import OpenAI
import os
import base64
from pathlib import Path
import datetime
from decouple import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def enviar_correo(destinatario, asunto, cuerpo):
    remitente = config("EMAIL_USER")
    password = config("EMAIL_PASSWORD")  # Use an application password if you use Gmail.

    # Configure the message
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto

    # Add the message body
    mensaje.attach(MIMEText(cuerpo, "plain"))
    # Send the mail
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.sendmail(remitente, destinatario, mensaje.as_string())
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
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

@app.get("/generate_questions")
async def generate_questions():
    completion = client.chat.completions.create(
            messages=[{'role': 'system', 'content': """Actúa como un profesor de medicina. Haz tres preguntas a los estudiantes de la clase sobre el episodio Infection, Part I (S5E4) de la serie Chicago Fire.
                                                          Las preguntas deben ir enfocadas en qué harían los estudiantes en diversas situaciones médicas y cómo resolverían los problemas que se presentan en el episodio.
                                                          La finalidad es evaluar diversas habilidades del estudiante, tales como toma de decisiones, negociación, liderazgo, creatividad."""}],
            model='gpt-3.5-turbo'
        )
    
    chat_response = completion.choices[0].message.content
    print(chat_response)
    return {"questions": chat_response}

# API para recibir videos y preguntas
@app.post("/upload")
async def upload_video(file: UploadFile = Form(...), questions: str = Form(...), student_name: str = Form(...)):
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_student_name = "_".join(student_name.split()).lower()  # Reemplaza espacios por guiones bajos
        upload_dir = BASE_DIR / f"upload_{safe_student_name}_{timestamp}"
        upload_dir.mkdir(exist_ok=True)

        video_filename = f"{safe_student_name}_{timestamp}.mp4"
        video_path = upload_dir / video_filename
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        questions_path = upload_dir / "questions.txt"
        with open(questions_path, "w") as qf:
            qf.write(questions)
        
        enviar_correo(
                "jaredgs93@gmail.com",
                "Nuevo video enviado al servidor",
                f"Se ha recibido un nuevo video en el servidor de {student_name} ({timestamp})",
                
            )

        return {"message": "Video y preguntas guardados correctamente"}

    except Exception as e:
        print(e, "Error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
