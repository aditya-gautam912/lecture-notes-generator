import { render, screen } from '@testing-library/react';
import NotesView from '../components/NotesView';
import type { StudyData } from '../types';

const mockData: StudyData = {
  id: 1,
  filename: 'test-lecture.mp3',
  transcript: 'Full transcript text.',
  materials: {
    summary: 'This is a test summary.',
    notes: ['Note 1', 'Note 2', 'Note 3'],
    quiz: [
      {
        question: 'What is 2+2?',
        options: ['3', '4', '5', '6'],
        answer: '4',
      },
    ],
  },
};

describe('NotesView', () => {
  it('renders filename', () => {
    render(<NotesView data={mockData} />);
    expect(screen.getByText('test-lecture.mp3')).toBeInTheDocument();
  });

  it('renders summary', () => {
    render(<NotesView data={mockData} />);
    expect(screen.getByText('This is a test summary.')).toBeInTheDocument();
  });

  it('renders study notes', () => {
    render(<NotesView data={mockData} />);
    expect(screen.getByText('Note 1')).toBeInTheDocument();
    expect(screen.getByText('Note 2')).toBeInTheDocument();
    expect(screen.getByText('Note 3')).toBeInTheDocument();
  });

  it('renders quiz question and options', () => {
    render(<NotesView data={mockData} />);
    expect(screen.getByText('Q1: What is 2+2?')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('renders download button when id is present', () => {
    render(<NotesView data={mockData} />);
    expect(screen.getByText('📥 Download Study Guide (PDF)')).toBeInTheDocument();
  });

  it('does not render download button when id is missing', () => {
    render(<NotesView data={{ ...mockData, id: undefined }} />);
    expect(screen.queryByText('📥 Download Study Guide (PDF)')).not.toBeInTheDocument();
  });

  it('renders transcript', () => {
    render(<NotesView data={mockData} />);
    expect(screen.getByText('Full transcript text.')).toBeInTheDocument();
  });
});
