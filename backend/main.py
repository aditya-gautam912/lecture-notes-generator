import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.ai_service import transcribe_audio, generate_study_materials
from services.pdf_service import create_lecture_pdf
import database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

TEMP_DIR = "temp_audio"
PDF_DIR = "exported_pdfs"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

@app.on_event("startup")
def startup_event():
    database.init_db()

class GenerateRequest(BaseModel):
    filename: str
    transcript: str

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    file_path = None
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}")

        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")

        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcript = await transcribe_audio(file_path)
        os.remove(file_path)

        return {"transcript": transcript, "filename": file.filename}

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
        # 1. Generate notes, summary, quiz (async)
        study_materials = await generate_study_materials(req.transcript)

        # 2. Save to Database
        lecture_id = database.save_lecture(req.filename, req.transcript, study_materials)

        return {
            "id": lecture_id,
            "transcript": req.transcript,
            "materials": study_materials,
            "filename": req.filename
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
    lecture = database.get_lecture_by_id(lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@app.delete("/history/{lecture_id}")
async def delete_lecture(lecture_id: int):
    database.delete_lecture(lecture_id)
    return {"message": "Deleted successfully"}

@app.get("/export-pdf/{lecture_id}")
async def export_pdf(lecture_id: int):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
