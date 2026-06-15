# 🎓 Lecture Voice-to-Notes Generator

> **Live Demo**: [https://lecture-notes-generator-jkqv.onrender.com/](https://lecture-notes-generator-jkqv.onrender.com/)

An AI-powered application that converts lecture audio and video recordings into structured study materials, including summaries, detailed notes, and interactive quizzes.

## 🚀 Features

- **Audio & Video Support**: Upload MP3, WAV, M4A, AAC, OGG, MP4, AVI, MOV, MKV, WEBM, FLV — max 100MB.
- **Video-to-Audio Extraction**: Automatically extracts audio track from video files for transcription.
- **Audio Chunking**: Files >15MB are split into chunks for reliable processing.
- **Transcription**: Uses Groq's `whisper-large-v3` for high-accuracy speech-to-text.
- **Smart Summarization**: Condenses lectures into concise summaries using `llama-3.3-70b-versatile`.
- **Structured Notes**: Auto-generated bullet-point study notes from the transcript.
- **Interactive Quiz**: Multiple-choice quiz with ✓/✗ icons, "(Correct)" labels, instant scoring, and retry.
- **Quiz Answer Normalization**: AI-generated answers are auto-matched to options (handles letter prefixes, partial matches).
- **Drag & Drop Upload**: Drag files onto the upload area or click to browse.
- **Honest Progress Bar**: Real XHR upload percentage + indeterminate animation during AI generation (no fake progress).
- **Toast Notifications**: Non-intrusive success/error messages.
- **Skeleton Loaders**: Pulsing placeholders while content loads.
- **Responsive Sidebar**: Collapsible hamburger menu on mobile, slide-in/out with backdrop.
- **Light Theme Only**: Clean, minimal light-colored interface.
- **PDF Export**: Download a printable study guide with summary, notes, and quiz.
- **Lecture History**: Browse, load, and delete past lectures from the sidebar.
- **Rate Limiting**: 10 requests/min/IP on `/transcribe`.
- **Optional API Auth**: Lock the API with an `API_SECRET_KEY` environment variable.

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Vite, Vanilla CSS (custom design system with CSS custom properties).
- **Backend**: FastAPI (Python), Uvicorn, SQLAlchemy, SQLite.
- **AI Models**: 
  - Transcription: [Groq Whisper Large V3](https://groq.com/)
  - Text Processing: [Groq Llama 3.3 70B Versatile](https://groq.com/)
- **Audio Processing**: pydub + ffmpeg (chunking, video extraction).
- **Testing**: Vitest (17 frontend tests), pytest + FastAPI TestClient (29 backend tests).

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js & npm**
- **Groq API Key**: Get one for free at [console.groq.com](https://console.groq.com/).
- **ffmpeg** (optional, for audio chunking and video extraction).

## ⚙️ Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
API_SECRET_KEY=your_secret_key_here    # optional, locks API endpoints
```

Start the server:

```bash
python main.py
```

### 2. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

The Vite dev server proxies API requests to the backend (see `vite.config.ts`).

## 📖 Usage

1. Open your browser to `http://localhost:5173`.
2. Drag an audio/video file onto the upload area or click to browse.
3. Watch the progress bar during upload (real %) and AI generation (indeterminate).
4. View your transcript, summary, study notes, and interactive quiz.
5. Click quiz answers, submit to see ✓/✗ feedback and score, retry if desired.
6. Browse past lectures in the sidebar and download PDF study guides.

## 🧪 Running Tests

### Backend (29 tests)

```bash
cd backend
venv\Scripts\activate   # or source venv/bin/activate
python -m pytest tests/ -v
```

### Frontend (17 tests)

```bash
cd frontend
npm test
```

## 🛡️ Security

- API keys are stored in `.env` (excluded from git via `.gitignore`).
- Optional `API_SECRET_KEY` enables Bearer token auth for cross-origin API requests.
- CORS restricted to the deployed Render URL + localhost.
- Rate limiting: 10 requests/min/IP on `/transcribe`.
- File validation: extension whitelist, MIME type check, 100MB size limit (pre + post write).
- Input sanitization: filename cleaned, transcript capped at 100K chars.

## 📄 License

MIT License
