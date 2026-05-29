import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_path: str):
    """Transcribes audio using Groq's Whisper-large-v3 model."""
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3",
            response_format="text",
        )
    return transcription

def generate_study_materials(transcript: str):
    """Generates structured notes, a summary, and a quiz from the transcript."""
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

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful academic assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    return completion.choices[0].message.content
