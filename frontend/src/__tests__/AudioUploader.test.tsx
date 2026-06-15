import { render, screen, fireEvent } from '@testing-library/react';
import AudioUploader from '../components/AudioUploader';

const createFile = (name: string, type: string, size = 1024): File =>
  new File([new ArrayBuffer(size)], name, { type });

describe('AudioUploader', () => {
  const defaultProps = {
    onProcessingStart: vi.fn(),
    onGenerateStart: vi.fn(),
    onProcessingComplete: vi.fn(),
    onError: vi.fn(),
  };

  it('renders upload form', () => {
    render(<AudioUploader {...defaultProps} />);
    expect(screen.getByText('Upload Lecture Audio')).toBeInTheDocument();
    expect(screen.getByText('Generate Study Notes')).toBeInTheDocument();
  });

  it('disables button when no file selected', () => {
    render(<AudioUploader {...defaultProps} />);
    expect(screen.getByText('Generate Study Notes')).toBeDisabled();
  });

  it('accepts valid audio file', () => {
    render(<AudioUploader {...defaultProps} />);
    const file = createFile('test.mp3', 'audio/mpeg');
    const input = screen.getByLabelText('Upload') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText('Generate Study Notes')).not.toBeDisabled();
  });

  it('rejects invalid file type', () => {
    render(<AudioUploader {...defaultProps} />);
    const file = createFile('test.txt', 'text/plain');
    const input = screen.getByLabelText('Upload') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText('Only audio files are accepted (MP3, WAV, M4A, AAC, OGG).')).toBeInTheDocument();
  });

  it('rejects oversized file', () => {
    render(<AudioUploader {...defaultProps} />);
    const file = createFile('test.mp3', 'audio/mpeg', 200 * 1024 * 1024);
    const input = screen.getByLabelText('Upload') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText('File too large. Maximum size is 100MB.')).toBeInTheDocument();
  });
});
