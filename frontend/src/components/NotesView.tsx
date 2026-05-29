import React from 'react';

interface NotesViewProps {
  data: {
    transcript: string;
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

  return (
    <div className="notes-view">
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
        <h3>Quiz</h3>
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
