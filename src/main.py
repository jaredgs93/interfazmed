from fastapi import FastAPI, HTTPException
import base64
from pathlib import Path
import datetime
from openai import OpenAI
from decouple import config
import uvicorn

app = FastAPI()

BASE_DIR = Path("./uploaded_files")
BASE_DIR.mkdir(exist_ok=True)

client = OpenAI(api_key = config('OPENAI_API_KEY'))

@app.get("/")
async def root():
    return {"message": "OK"}

@app.post("/upload/")
async def upload_video(data: dict):
    try:
        video_base64 = data.get("video")
        questions = data.get("questions", "")

        if not video_base64:
            raise HTTPException(status_code=400, detail="No se recibió un video en Base64.")

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_dir = BASE_DIR / f"upload_{timestamp}"
        upload_dir.mkdir(exist_ok=True)

        video_filename = f"video_{timestamp}.mp4"
        video_path = upload_dir / video_filename
        with open(video_path, "wb") as f:
            f.write(base64.b64decode(video_base64))

        questions_path = upload_dir / "questions.txt"
        with open(questions_path, "w") as f:
            f.write(questions)

        return {"message": "Video y preguntas guardados correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/generate_questions")
async def generate_questions():
    completion = client.chat.completions.create(
            messages = [{'role': 'system', 'content' : """Actúa como un profesor de medicina. Haz tres preguntas a los estudiantes de la clase sobre el episodio Infection, Part I (S5E4) de la serie Chicago Fire.
                                                          Las preguntas deben ir enfocadas en qué harían los estudiantes en diversas situaciones médicas y cómo resolverían los problemas que se presentan en el episodio.
                                                          La finalidad es evaluar diversas habilidades del estudiante, tales como toma de decisiones, negociación, liderazgo, creatividad."""},
                        ],
        
            model = 'gpt-3.5-turbo'
        )
    
        
    chat_response = completion.choices[0].message.content
    print(chat_response)
    return {"questions": chat_response}