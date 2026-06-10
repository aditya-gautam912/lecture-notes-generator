import React, { useState } from 'react';

interface AudioUploaderProps {
  onProcessingStart: () => void;
  onGenerateStart: () => void;
  onProcessingComplete: (data: any) => void;
  onError: (error: string) => void;
}

const AudioUploader: React.FC<AudioUploaderProps> = ({ onProcessingStart, onGenerateStart, onProcessingComplete, onError }) => {
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
      // Step 1: Transcribe audio
      const transcribeRes = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!transcribeRes.ok) {
        throw new Error('Failed to transcribe audio');
      }
      
      const transcribeData = await transcribeRes.json();

      // Step 2: Generate notes
      onGenerateStart();

      const generateRes = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: transcribeData.filename,
          transcript: transcribeData.transcript
        }),
      });

      if (!generateRes.ok) {
        throw new Error('Failed to generate study materials');
      }

      const generateData = await generateRes.json();
      onProcessingComplete(generateData);

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
