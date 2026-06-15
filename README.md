# 🎓 Lecture Voice-to-Notes Generator

> **Live Demo**: [https://lecture-notes-generator-jkqv.onrender.com/](https://lecture-notes-generator-jkqv.onrender.com/)

An AI-powered application that converts lecture audio recordings into structured study materials, including summaries, detailed notes, and interactive quizzes.

## 🚀 Features

- **Audio Transcription**: Uses Groq's `whisper-large-v3` for near-instant, high-accuracy transcription.
- **Smart Summarization**: Summarizes long lectures into concise, readable points using `llama-3.3-70b-versatile`.
- **Study Notes**: Automatically generates bulleted study notes from the transcript.
- **Interactive Quiz**: Clickable multiple-choice quiz with instant feedback and scoring.
- **Drag & Drop Upload**: Drag audio files directly onto the upload area.
- **Real-Time Progress**: Upload percentage via XHR, simulated progress for AI processing stages.
- **Toast Notifications**: Non-intrusive success/error messages in the corner.
- **Skeleton Loaders**: Pulsing placeholders while content loads.
- **Responsive Sidebar**: Collapsible hamburger menu on mobile.
- **Light Theme Only**: Clean, minimal light-colored interface.
- **PDF Export**: Download a printable study guide.
- **Lecture History**: Browse, load, and delete past lectures from the sidebar.

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Vite, Vanilla CSS (custom design system with CSS custom properties).
- **Backend**: FastAPI (Python), Uvicorn, SQLAlchemy, SQLite.
- **AI Models**: 
  - Transcription: [Groq Whisper Large V3](https://groq.com/)
  - Text Processing: [Groq Llama 3.3 70B Versatile](https://groq.com/)
- **Testing**: Vitest (frontend), pytest + FastAPI TestClient (backend).

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

The Vite dev server proxies API requests to the backend (see `vite.config.ts`).

## 📖 Usage

1. Open your browser to `http://localhost:5173`.
2. Drag an audio file onto the upload area or click to browse (MP3, WAV, M4A, AAC, OGG — max 100MB).
3. Watch the real-time progress bar during upload and AI processing.
4. View your generated transcript, summary, study notes, and interactive quiz.
5. Click quiz answers to select, submit to see your score, and retry if desired.
6. Browse past lectures in the sidebar and download PDF study guides.

## 🧪 Running Tests

### Backend
```bash
cd backend
venv\Scripts\activate   # or source venv/bin/activate
python -m pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm test
```

## 🛡️ Security

This project uses a `.env` file to store sensitive API keys. **Never commit your `.env` file to version control.** The `.gitignore` included in this repo is already configured to exclude it.

## 📄 License

MIT License
