import os
import json
import tempfile
import math
from groq import AsyncGroq
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List

load_dotenv()

# Transcription client (audio) - Groq only (OpenRouter has no audio API)
TRANSCRIBE_BASE_URL = os.getenv("TRANSCRIBE_BASE_URL", "https://api.groq.com/openai/v1")
TRANSCRIBE_API_KEY = os.getenv("TRANSCRIBE_API_KEY", os.getenv("GROQ_API_KEY"))
transcribe_client = AsyncGroq(api_key=TRANSCRIBE_API_KEY, base_url=TRANSCRIBE_BASE_URL)

# Generation client (chat) - OpenAI-compatible provider (Groq, OpenRouter, etc.)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("GROQ_API_KEY"))
client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

LLM_MODELS = [m for m in os.getenv("GROQ_LLM_MODEL", "minimax/minimax-m3:free,google/gemma-4-26b-a4b-it:free,z-ai/glm-5.2:free,minimax/minimax-m2.7:free").split(",") if m]

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
            text = await transcribe_client.audio.transcriptions.create(
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

    last_error = None
    for model in LLM_MODELS:
        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = completion.choices[0].message.content
            parsed_json = _extract_json(content)
            materials = StudyMaterials(**parsed_json)
            result = materials.model_dump()
            result["quiz"] = _normalize_quiz(result.get("quiz", []))
            return result
        except Exception as e:
            last_error = e
            print(f"Model {model} failed: {e}")
    raise ValueError(f"All LLM models failed. Last error: {last_error}")


def _extract_json(content: str) -> dict:
    if content is None:
        raise ValueError("Empty AI response")
    text = content.strip()
    # Strip ```json ... ``` or ``` ... ``` code fences
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
        text = text.strip()
    # Fallback: extract the first balanced {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def _normalize_quiz(quiz: list[dict]) -> list[dict]:
    result = []
    for item in quiz:
        item_copy = dict(item)
        options = item_copy.get("options", [])
        answer = item_copy.get("answer", "")
        if answer in options:
            result.append(item_copy)
            continue
        for opt in options:
            if opt.startswith(answer) or answer.startswith(opt):
                item_copy["answer"] = opt
                break
            prefix = opt.split(".")[0].split(")")[0].strip()
            if prefix and len(prefix) == 1 and answer == prefix:
                item_copy["answer"] = opt
                break
        result.append(item_copy)
    return result
