import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

class QuizItem(BaseModel):
    question: str
    options: List[str]
    answer: str

class StudyMaterials(BaseModel):
    summary: str
    notes: List[str]
    quiz: List[QuizItem]

async def transcribe_audio(file_path: str):
    """Transcribes audio using Groq's Whisper-large-v3 model asynchronously."""
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as file:
        transcription = await client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3",
            response_format="text",
        )
    return transcription

async def generate_study_materials(transcript: str):
    """Generates structured notes, a summary, and a quiz from the transcript using Pydantic validation."""
    prompt = f"""
    You are an expert academic assistant. Based on the following lecture transcript, please provide:
    1. A concise summary of the key points.
    2. Structured study notes with bullet points.
    3. A 5-question multiple-choice quiz to test understanding.

    Format the output as JSON with the following structure:
    {{
        "summary": "...",
        "notes": ["...", "..."],
        "quiz": [
            {{
                "question": "...",
                "options": ["A", "B", "C", "D"],
                "answer": "..."
            }}
        ]
    }}

    Transcript:
    {transcript}
    """

    completion = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful academic assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    content = completion.choices[0].message.content
    try:
        parsed_json = json.loads(content)
        materials = StudyMaterials(**parsed_json)
        return materials.model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation error: {e}")
        raise ValueError("Failed to generate valid study materials from the AI response.")
