import { useState } from 'react';
import AudioUploader from './components/AudioUploader';
import NotesView from './components/NotesView';
import './App.css';

function App() {
  const [processing, setProcessing] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleStart = () => {
    setProcessing(true);
    setData(null);
    setError(null);
  };

  const handleComplete = (result: any) => {
    setProcessing(false);
    setData(result);
  };

  const handleError = (err: string) => {
    setProcessing(false);
    setError(err);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎓 Lecture Voice-to-Notes</h1>
        <p>Turn your lectures into study guides in seconds.</p>
      </header>

      <main className="app-main">
        {!data && !processing && (
          <AudioUploader 
            onProcessingStart={handleStart} 
            onProcessingComplete={handleComplete} 
            onError={handleError} 
          />
        )}

        {processing && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Transcribing and generating notes... This may take a minute.</p>
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

      {data && (
        <footer className="app-footer">
          <button onClick={() => setData(null)}>Process Another Lecture</button>
        </footer>
      )}
    </div>
  );
}

export default App;
