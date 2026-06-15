import os
import re
import shutil
import json
import time
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from services.ai_service import transcribe_audio, generate_study_materials
from services.pdf_service import create_lecture_pdf
import database

app = FastAPI()

ALLOWED_ORIGINS = [
    "https://lecture-notes-generator-jkqv.onrender.com",
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

@ app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if not API_SECRET_KEY:
        return await call_next(request)
    if request.url.path in ("/health", "/"):
        return await call_next(request)
    origin = request.headers.get("origin", "")
    if origin in ALLOWED_ORIGINS or not origin:
        return await call_next(request)
    auth = request.headers.get("Authorization", "")
    expected = f"Bearer {API_SECRET_KEY}"
    if auth != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

TEMP_DIR = "temp_audio"
PDF_DIR = "exported_pdfs"
MAX_FILE_SIZE = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
RATE_LIMIT = 10
RATE_WINDOW = 60
RATE_CLEANUP_INTERVAL = 300
MAX_TRANSCRIPT_LEN = 100000

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

rate_store: dict[str, list[float]] = defaultdict(list)

def rate_limit(ip: str):
    now = time.time()
    window_start = now - RATE_WINDOW
    rate_store[ip] = [t for t in rate_store[ip] if t > window_start]
    if len(rate_store[ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    rate_store[ip].append(now)

    if int(now) % RATE_CLEANUP_INTERVAL == 0:
        cutoff = now - RATE_WINDOW * 2
        stale = [k for k, v in rate_store.items() if v and max(v) < cutoff]
        for k in stale:
            del rate_store[k]

def sanitize_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r'[^\w\-_. ]', '', name)
    return name or "upload"

@app.on_event("startup")
def startup_event():
    database.init_db()

class GenerateRequest(BaseModel):
    filename: str = Field(max_length=255)
    transcript: str = Field(max_length=MAX_TRANSCRIPT_LEN)

@app.post("/transcribe")
async def transcribe_endpoint(request: Request, file: UploadFile = File(...)):
    rate_limit(request.client.host if request.client else "unknown")
    file_path = None
    try:
        safe_name = sanitize_filename(file.filename)
        ext = os.path.splitext(safe_name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}")

        if file.size is not None and file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")

        file_path = os.path.join(TEMP_DIR, safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")

        transcript = await transcribe_audio(file_path)
        os.remove(file_path)

        return {"transcript": transcript, "filename": safe_name}

    except HTTPException:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_endpoint(req: GenerateRequest):
    try:
        safe_name = sanitize_filename(req.filename)
        study_materials = await generate_study_materials(req.transcript)

        lecture_id = database.save_lecture(safe_name, req.transcript, study_materials)

        return {
            "id": lecture_id,
            "transcript": req.transcript,
            "materials": study_materials,
            "filename": safe_name
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    return database.get_all_lectures()

@app.get("/history/{lecture_id}")
async def get_lecture(lecture_id: int):
    if lecture_id < 1:
        raise HTTPException(status_code=400, detail="Invalid lecture ID")
    lecture = database.get_lecture_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@app.delete("/history/{lecture_id}")
async def delete_lecture(lecture_id: int):
    if lecture_id < 1:
        raise HTTPException(status_code=400, detail="Invalid lecture ID")
    database.delete_lecture(lecture_id)
    return {"message": "Deleted successfully"}

@app.get("/export-pdf/{lecture_id}")
async def export_pdf(lecture_id: int):
    if lecture_id < 1:
        raise HTTPException(status_code=400, detail="Invalid lecture ID")
    lecture = database.get_lecture_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    pdf_filename = f"lecture_{lecture_id}.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    
    create_lecture_pdf(lecture, pdf_path)
    
    return FileResponse(
        path=pdf_path, 
        filename=f"{lecture['filename']}_Study_Guide.pdf",
        media_type='application/pdf'
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"), media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
