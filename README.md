# 🎓 Lecture Voice-to-Notes Generator

An AI-powered application that converts lecture audio recordings into structured study materials, including summaries, detailed notes, and interactive quizzes.

## 🚀 Features

- **Audio Transcription**: Uses Groq's `whisper-large-v3` for near-instant, high-accuracy transcription.
- **Smart Summarization**: Summarizes long lectures into concise, readable points using `llama-3.3-70b-versatile`.
- **Study Notes**: Automatically generates bulleted study notes from the transcript.
- **Interactive Quizzes**: Creates a 5-question multiple-choice quiz to test your understanding of the lecture.
- **Student-Centric UI**: A clean, minimalist interface built with React and TypeScript.

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Vite, Vanilla CSS.
- **Backend**: FastAPI (Python), Uvicorn.
- **AI Models**: 
  - Transcription: [Groq Whisper Large V3](https://groq.com/)
  - Text Processing: [Groq Llama 3.3 70B Versatile](https://groq.com/)

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js & npm**
- **Groq API Key**: Get one for free at [console.groq.com](https://console.groq.com/).

## ⚙️ Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
6. Start the backend server:
   ```bash
   python main.py
   ```

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 📖 Usage

1. Open your browser to `http://localhost:5173`.
2. Upload a lecture audio file (MP3, WAV, or M4A).
3. Wait for the AI to process the audio.
4. View your generated transcript, summary, study notes, and quiz!

## 🛡️ Security

This project uses a `.env` file to store sensitive API keys. **Never commit your `.env` file to version control.** The `.gitignore` included in this repo is already configured to exclude it.

## 📄 License

MIT License
