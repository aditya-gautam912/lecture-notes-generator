import { useState, useEffect, useCallback } from 'react';
import AudioUploader from './components/AudioUploader';
import NotesView from './components/NotesView';
import ConfirmModal from './components/ConfirmModal';
import SkeletonLoader from './components/SkeletonLoader';
import EmptyState from './components/EmptyState';
import { useToast } from './hooks/useToast';
import type { StudyData, HistoryItem } from './types';
import './App.css';

function App() {
  const [processingState, setProcessingState] = useState<'idle' | 'loading' | 'transcribing' | 'generating'>('idle');
  const [data, setData] = useState<StudyData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [uploadKey, setUploadKey] = useState(0);
  const { addToast } = useToast();

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch('/history');
      const result = await response.json();
      setHistory(result);
    } catch {
      addToast('Failed to load history', 'error');
    }
  }, [addToast]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const loadLecture = async (id: number) => {
    setProcessingState('loading');
    setError(null);
    try {
      const response = await fetch(`/history/${id}`);
      const result = await response.json();
      setData(result);
      setProcessingState('idle');
    } catch {
      setError("Failed to load lecture from history");
      setProcessingState('idle');
    }
  };

  const confirmDelete = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    setDeleteTarget(id);
  };

  const handleDeleteConfirm = async () => {
    if (deleteTarget === null) return;
    try {
      await fetch(`/history/${deleteTarget}`, { method: 'DELETE' });
      addToast('Lecture deleted', 'success');
      fetchHistory();
      if (data?.id === deleteTarget) setData(null);
    } catch {
      addToast('Failed to delete lecture', 'error');
    } finally {
      setDeleteTarget(null);
    }
  };

  const handleStart = () => {
    setProcessingState('transcribing');
    setData(null);
    setError(null);
  };

  const handleGenerateStart = () => {
    setProcessingState('generating');
  };

  const handleComplete = (result: StudyData) => {
    setProcessingState('idle');
    setData(result);
    addToast('Study materials generated successfully!', 'success');
    fetchHistory();
  };

  const handleError = (err: string) => {
    setProcessingState('idle');
    setError(err);
    addToast(err, 'error');
  };

  return (
    <div className="app-wrapper">
      <button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen((prev) => !prev)}
        aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {sidebarOpen ? '✕' : '☰'}
      </button>

      {sidebarOpen && <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar-header">
          <h2>📚 Lecture History</h2>
          {data && (
            <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => {
              setData(null);
              setProcessingState('idle');
              setError(null);
              setSidebarOpen(false);
              setUploadKey(k => k + 1);
              window.scrollTo(0, 0);
            }}>
              + New Lecture
            </button>
          )}
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <EmptyState
              icon="📖"
              title="No lectures yet"
              description="Upload your first lecture to get started."
            />
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                className={`history-item ${data?.id === item.id ? 'active' : ''}`}
                onClick={() => { loadLecture(item.id); setSidebarOpen(false); }}
              >
                <div>
                  <div className="filename">{item.filename}</div>
                  <div className="date">{new Date(item.date).toLocaleDateString()}</div>
                </div>
                <button className="delete-btn" onClick={(e) => confirmDelete(e, item.id)}>🗑️</button>
              </div>
            ))
          )}
        </div>
      </aside>

      <main className="app-container">
        <header className="app-header">
          <h1>🎓 Lecture Voice-to-Notes</h1>
          <p>Turn your lectures into study guides in seconds.</p>
        </header>

        {!data && processingState !== 'loading' && !error && (
          <AudioUploader
            key={uploadKey}
            onProcessingStart={handleStart}
            onGenerateStart={handleGenerateStart}
            onProcessingComplete={handleComplete}
            onError={handleError}
          />
        )}

        {processingState === 'loading' && (
          <div className="loading-state">
            <SkeletonLoader lines={6} />
          </div>
        )}

        {error && processingState === 'idle' && !data && (
          <div className="empty-state">
            <span className="empty-state-icon">❌</span>
            <h3>Something went wrong</h3>
            <p>{error}</p>
            <button className="btn btn-primary" onClick={() => setError(null)} style={{ marginTop: '1rem' }}>
              Try Again
            </button>
          </div>
        )}

        {data && <NotesView data={data} />}
      </main>

      <ConfirmModal
        open={deleteTarget !== null}
        title="Delete Lecture"
        message="Are you sure you want to delete this lecture? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

export default App;
