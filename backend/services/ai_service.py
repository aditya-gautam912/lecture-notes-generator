import os
import json
import tempfile
import math
from groq import AsyncGroq
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

CHUNK_SIZE_MB = 15
MAX_FILE_SIZE_MB = 100
VIDEO_EXTENSIONS = {'.avi', '.mov', '.mkv', '.webm', '.flv'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}

class QuizItem(BaseModel):
    question: str
    options: List[str]
    answer: str

class StudyMaterials(BaseModel):
    summary: str
    notes: List[str]
    quiz: List[QuizItem]

def _split_audio(file_path: str) -> List[str]:
    try:
        from pydub import AudioSegment
    except ImportError:
        return [file_path]

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb <= CHUNK_SIZE_MB:
        return [file_path]

    audio = AudioSegment.from_file(file_path)
    chunk_ms = int((CHUNK_SIZE_MB / size_mb) * len(audio))
    chunks = []
    for i in range(math.ceil(len(audio) / chunk_ms)):
        start = i * chunk_ms
        end = min((i + 1) * chunk_ms, len(audio))
        segment = audio[start:end]
        fd, path = tempfile.mkstemp(suffix='.mp3')
        os.close(fd)
        segment.export(path, format='mp3')
        chunks.append(path)
    return chunks

def _ensure_audio(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in AUDIO_EXTENSIONS:
        return file_path
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        fd, path = tempfile.mkstemp(suffix='.mp3')
        os.close(fd)
        audio.export(path, format='mp3')
        return path
    except ImportError:
        return file_path

async def transcribe_audio(file_path: str):
    """Transcribes audio using Groq's Whisper-large-v3, extracting audio from video and splitting large files."""
    audio_path = _ensure_audio(file_path)
    chunks = _split_audio(audio_path)
    transcripts = []

    for chunk_path in chunks:
        filename = os.path.basename(chunk_path)
        with open(chunk_path, "rb") as f:
            text = await client.audio.transcriptions.create(
                file=(filename, f.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        transcripts.append(text)
        if chunk_path != audio_path:
            os.remove(chunk_path)

    if audio_path != file_path:
        os.remove(audio_path)

    return " ".join(transcripts)

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
                "options": ["Full text of correct answer", "Full text of wrong option 1", "Full text of wrong option 2", "Full text of wrong option 3"],
                "answer": "Full text of correct answer"
            }}
        ]
    }}

    IMPORTANT: The "answer" must be the EXACT full text of one of the "options" — do not use letters like "A" or "B" as the answer. The answer must match the option text verbatim.

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
        result = materials.model_dump()
        result["quiz"] = _normalize_quiz(result.get("quiz", []))
        return result
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation error: {e}")
        raise ValueError("Failed to generate valid study materials from the AI response.")


def _normalize_quiz(quiz: list[dict]) -> list[dict]:
    for item in quiz:
        options = item.get("options", [])
        answer = item.get("answer", "")
        if answer in options:
            continue
        for opt in options:
            if opt.startswith(answer) or answer.startswith(opt):
                item["answer"] = opt
                break
            prefix = opt.split(".")[0].split(")")[0].strip()
            if prefix and len(prefix) == 1 and answer == prefix:
                item["answer"] = opt
                break
    return quiz
