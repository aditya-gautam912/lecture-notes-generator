import React from 'react';

interface NotesViewProps {
  data: {
    id?: number;
    transcript: string;
    filename?: string;
    materials: {
      summary: string;
      notes: string[];
      quiz: {
        question: string;
        options: string[];
        answer: string;
      }[];
    };
  };
}

const NotesView: React.FC<NotesViewProps> = ({ data }) => {
  const { summary, notes, quiz } = data.materials;

  const handleDownloadPDF = () => {
    if (data.id) {
      window.open(`http://localhost:8000/export-pdf/${data.id}`, '_blank');
    }
  };

  return (
    <div className="notes-view">
      <div className="notes-header">
        <h2>{data.filename || 'Lecture Results'}</h2>
        {data.id && (
          <button className="download-btn" onClick={handleDownloadPDF}>
            📥 Download Study Guide (PDF)
          </button>
        )}
      </div>

      <section className="summary-section">
        <h3>Summary</h3>
        <p>{summary}</p>
      </section>

      <section className="notes-section">
        <h3>Study Notes</h3>
        <ul>
          {notes.map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      </section>

      <section className="quiz-section">
        <h3>Self-Assessment Quiz</h3>
        {quiz.map((item, index) => (
          <div key={index} className="quiz-item">
            <p><strong>Q{index + 1}: {item.question}</strong></p>
            <ul>
              {item.options.map((option, optIndex) => (
                <li key={optIndex}>{option}</li>
              ))}
            </ul>
            <details>
              <summary>Show Answer</summary>
              <p>Correct Answer: {item.answer}</p>
            </details>
          </div>
        ))}
      </section>

      <section className="transcript-section">
        <h3>Full Transcript</h3>
        <div className="transcript-box">
          {data.transcript}
        </div>
      </section>
    </div>
  );
};

export default NotesView;
