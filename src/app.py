from fastapi import FastAPI, Request, UploadFile, Form, HTTPException
from fastapi.templating import Jinja2Templates
import shutil
from openai import OpenAI
import os
import base64
from pathlib import Path
import datetime
from decouple import config

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

        return {"message": "Video y preguntas guardados correctamente"}

    except Exception as e:
        print(e, "Error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
