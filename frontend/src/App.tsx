import { useState, useEffect } from 'react';
import AudioUploader from './components/AudioUploader';
import NotesView from './components/NotesView';
import './App.css';

interface HistoryItem {
  id: number;
  filename: string;
  date: string;
}

function App() {
  const [processing, setProcessing] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/history');
      const result = await response.json();
      setHistory(result);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const loadLecture = async (id: number) => {
    setProcessing(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/history/${id}`);
      const result = await response.json();
      setData(result);
      setProcessing(false);
    } catch (err) {
      setError("Failed to load lecture from history");
      setProcessing(false);
    }
  };

  const deleteLecture = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this lecture?")) return;
    try {
      await fetch(`http://localhost:8000/history/${id}`, { method: 'DELETE' });
      fetchHistory();
      if (data?.id === id) setData(null);
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  const handleStart = () => {
    setProcessing(true);
    setData(null);
    setError(null);
  };

  const handleComplete = (result: any) => {
    setProcessing(false);
    setData(result);
    fetchHistory(); // Refresh history list
  };

  const handleError = (err: string) => {
    setProcessing(false);
    setError(err);
  };

  return (
    <div className="app-wrapper">
      <aside className="sidebar">
        <h2>📚 Lecture History</h2>
        <button className="new-lecture-btn" onClick={() => setData(null)}>
          + New Lecture
        </button>
        <div className="history-list">
          {history.map((item) => (
            <div 
              key={item.id} 
              className={`history-item ${data?.id === item.id ? 'active' : ''}`}
              onClick={() => loadLecture(item.id)}
            >
              <div>
                <div className="filename">{item.filename}</div>
                <div className="date">{new Date(item.date).toLocaleDateString()}</div>
              </div>
              <button className="delete-btn" onClick={(e) => deleteLecture(e, item.id)}>
                🗑️
              </button>
            </div>
          ))}
        </div>
      </aside>

      <main className="app-container">
        <header className="app-header">
          <h1>🎓 Lecture Voice-to-Notes</h1>
          <p>Turn your lectures into study guides in seconds.</p>
        </header>

        {!data && !processing && (
          <AudioUploader 
            onProcessingStart={handleStart} 
            onProcessingComplete={handleComplete} 
            onError={handleError} 
          />
        )}

        {processing && (
          <div className="loading-state">
            <div className="waveform">
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
            </div>
            <p>AI is analyzing your lecture... generating notes and quiz.</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
            <button onClick={() => setError(null)}>Try Again</button>
          </div>
        )}

        {data && <NotesView data={data} />}
      </main>
    </div>
  );
}

export default App;
