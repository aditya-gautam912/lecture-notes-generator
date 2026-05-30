import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from services.ai_service import transcribe_audio, generate_study_materials
from services.pdf_service import create_lecture_pdf
import database

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_audio"
PDF_DIR = "exported_pdfs"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    file_path = None
    try:
        # 1. Save uploaded file temporarily
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Transcribe
        transcript = transcribe_audio(file_path)

        # 3. Generate notes, summary, quiz
        study_materials_json = generate_study_materials(transcript)
        study_materials = json.loads(study_materials_json)

        # 4. Save to Database
        lecture_id = database.save_lecture(file.filename, transcript, study_materials)

        # 5. Clean up temp file
        os.remove(file_path)

        return {
            "id": lecture_id,
            "transcript": transcript,
            "materials": study_materials,
            "filename": file.filename
        }

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
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
