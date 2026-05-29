import React, { useState } from 'react';

interface AudioUploaderProps {
  onProcessingStart: () => void;
  onProcessingComplete: (data: any) => void;
  onError: (error: string) => void;
}

const AudioUploader: React.FC<AudioUploaderProps> = ({ onProcessingStart, onProcessingComplete, onError }) => {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    onProcessingStart();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/process-audio', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process audio');
      }

      const data = await response.json();
      onProcessingComplete(data);
    } catch (err: any) {
      onError(err.message || 'An error occurred');
    }
  };

  return (
    <div className="uploader-container">
      <h2>Upload Lecture Audio</h2>
      <p>Select an MP3, WAV, or M4A file from your lecture.</p>
      <input type="file" accept="audio/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file}>
        Generate Study Notes
      </button>
    </div>
  );
};

export default AudioUploader;
