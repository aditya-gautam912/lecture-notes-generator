import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.ai_service import transcribe_audio, generate_study_materials

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
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

        # 4. Clean up temp file
        os.remove(file_path)

        return {
            "transcript": transcript,
            "materials": study_materials
        }

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        # Ensure cleanup even on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
