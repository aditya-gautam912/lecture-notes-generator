import React, { useState } from 'react';
import { API_BASE_URL } from '../config';
import type { StudyData } from '../types';

interface NotesViewProps {
  data: StudyData;
}

const NotesView: React.FC<NotesViewProps> = ({ data }) => {
  const { summary, notes, quiz } = data.materials;
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const handleSelect = (qIndex: number, option: string) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [qIndex]: option }));
  };

  const handleSubmit = () => {
    setSubmitted(true);
  };

  const handleReset = () => {
    setAnswers({});
    setSubmitted(false);
  };

  const correctCount = quiz.filter((q, i) => answers[i] === q.answer).length;
  const allAnswered = quiz.every((_, i) => answers[i] !== undefined);

  const handleDownloadPDF = () => {
    if (data.id) {
      window.open(`${API_BASE_URL}/export-pdf/${data.id}`, '_blank');
    }
  };

  return (
    <div className="notes-view">
      <div className="notes-header">
        <h2>{data.filename || 'Lecture Results'}</h2>
        {data.id && (
          <button className="btn btn-success" onClick={handleDownloadPDF}>
            📥 Download Study Guide (PDF)
          </button>
        )}
      </div>

      <section className="summary-section card">
        <h3 className="section-title">Summary</h3>
        <p>{summary}</p>
      </section>

      <section className="notes-section card">
        <h3 className="section-title">Study Notes</h3>
        <ul>
          {notes.map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      </section>

      <section className="quiz-section card">
        <h3 className="section-title">Self-Assessment Quiz</h3>

        {quiz.map((item, index) => {
          const selected = answers[index];
          const isCorrect = submitted && selected === item.answer;
          const isWrong = submitted && selected && selected !== item.answer;

          return (
            <div
              key={index}
              className={`quiz-item ${submitted ? (selected === item.answer ? 'quiz-item--correct' : 'quiz-item--wrong') : ''}`}
            >
              <p className="quiz-question">Q{index + 1}: {item.question}</p>
              <div className="quiz-options">
                {item.options.map((opt) => {
                  let cls = 'quiz-option';
                  if (submitted && opt === item.answer) cls += ' quiz-option--correct';
                  if (submitted && opt === selected && opt !== item.answer) cls += ' quiz-option--wrong';
                  if (selected === opt && !submitted) cls += ' quiz-option--selected';

                  return (
                    <button
                      key={opt}
                      className={cls}
                      onClick={() => handleSelect(index, opt)}
                      disabled={submitted}
                    >
                      <span className="quiz-option-radio">
                        {selected === opt ? '●' : '○'}
                      </span>
                      {opt}
                    </button>
                  );
                })}
              </div>
              {submitted && (
                <p className={`quiz-feedback ${isCorrect ? 'quiz-feedback--correct' : 'quiz-feedback--wrong'}`}>
                  {isCorrect ? '✓ Correct!' : isWrong ? `✗ Incorrect. Answer: ${item.answer}` : `Answer: ${item.answer}`}
                </p>
              )}
            </div>
          );
        })}

        <div className="quiz-footer">
          {!submitted ? (
            <button className="btn btn-primary" disabled={!allAnswered} onClick={handleSubmit}>
              Submit Answers
            </button>
          ) : (
            <>
              <p className="quiz-score">
                Score: {correctCount}/{quiz.length}
              </p>
              <button className="btn btn-ghost" onClick={handleReset}>
                Retry Quiz
              </button>
            </>
          )}
        </div>
      </section>

      <section className="transcript-section card">
        <h3 className="section-title">Full Transcript</h3>
        <div className="transcript-box">
          {data.transcript}
        </div>
      </section>
    </div>
  );
};

export default NotesView;
