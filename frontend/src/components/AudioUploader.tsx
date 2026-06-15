import React, { useState, useRef, useCallback } from 'react';
import type { StudyData } from '../types';

const ACCEPTED_TYPES = ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/mp4', 'audio/x-m4a', 'audio/aac', 'audio/ogg', 'video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-matroska', 'video/webm', 'video/x-flv'];
const MAX_SIZE_MB = 100;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

interface AudioUploaderProps {
  onProcessingStart: () => void;
  onGenerateStart: () => void;
  onProcessingComplete: (data: StudyData) => void;
  onError: (error: string) => void;
}

const AudioUploader: React.FC<AudioUploaderProps> = ({ onProcessingStart, onGenerateStart, onProcessingComplete, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingPhase, setProcessingPhase] = useState<'uploading' | 'generating' | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((f: File): boolean => {
    setValidationError(null);
    if (!ACCEPTED_TYPES.includes(f.type)) {
      setValidationError('Only audio/video files are accepted (MP3, WAV, M4A, AAC, OGG, MP4, AVI, MOV, MKV, WEBM).');
      return false;
    }
    if (f.size > MAX_SIZE_BYTES) {
      setValidationError(`File too large. Maximum size is ${MAX_SIZE_MB}MB.`);
      return false;
    }
    return true;
  }, []);

  const handleFile = useCallback((f: File) => {
    if (validateFile(f)) {
      setFile(f);
    } else {
      setFile(null);
    }
  }, [validateFile]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) handleFile(dropped);
  };

  const handleUpload = () => {
    if (!file) return;
    onProcessingStart();
    setUploadProgress(0);
    setProcessingPhase('uploading');

    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/transcribe');

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        setUploadProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = async () => {
      if (xhr.status < 200 || xhr.status >= 300) {
        setProcessingPhase(null);
        onError('Failed to transcribe audio');
        return;
      }
      const transcribeData = JSON.parse(xhr.responseText);

      onGenerateStart();
      setProcessingPhase('generating');
      setUploadProgress(0);

      try {
        const generateRes = await fetch('/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: transcribeData.filename,
            transcript: transcribeData.transcript,
          }),
        });

        if (!generateRes.ok) {
          throw new Error('Failed to generate study materials');
        }

        const generateData = await generateRes.json();
        setProcessingPhase(null);
        setUploadProgress(100);
        setTimeout(() => onProcessingComplete(generateData), 400);
      } catch (err: unknown) {
        setProcessingPhase(null);
        onError(err instanceof Error ? err.message : 'An error occurred');
      }
    };

    xhr.onerror = () => {
      setProcessingPhase(null);
      onError('Network error during upload');
    };
    xhr.send(formData);
  };

  const isProcessing = uploadProgress > 0;

  return (
    <div
      className={`uploader-container ${dragOver ? 'uploader-container--dragover' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !isProcessing && inputRef.current?.click()}
    >
      <div className="uploader-content">
        <span className="uploader-icon">{dragOver ? '📂' : '🎤'}</span>
        <h2>Upload Lecture Audio</h2>
        <p>Drag & drop an audio/video file here, or click to browse.</p>
        <p className="uploader-hint">Supports MP3, WAV, M4A, AAC, OGG, MP4, AVI, MOV, MKV, WEBM &mdash; max {MAX_SIZE_MB}MB</p>

        <input
          ref={inputRef}
          type="file"
          accept="audio/*,video/*"
          onChange={handleFileChange}
          aria-label="Upload"
          style={{ display: 'none' }}
        />

        {file && !isProcessing && (
          <div className="uploader-file">
            <span>📄 {file.name}</span>
            <span className="uploader-file-size">{(file.size / (1024 * 1024)).toFixed(1)}MB</span>
          </div>
        )}

        {validationError && <p className="validation-error">{validationError}</p>}

        {isProcessing && (
          <div className="uploader-progress">
            <div className="progress-bar">
              <div className={`progress-bar-fill${processingPhase === 'generating' ? ' progress-bar-fill--indeterminate' : ''}`}
                style={processingPhase === 'uploading' ? { width: `${uploadProgress}%` } : undefined}
              />
            </div>
            {processingPhase === 'uploading' && (
              <span className="uploader-progress-text">{uploadProgress}%</span>
            )}
          </div>
        )}

        {!isProcessing && (
          <button className="btn btn-primary" disabled={!file} onClick={(e) => { e.stopPropagation(); handleUpload(); }}>
            Generate Study Notes
          </button>
        )}
      </div>
    </div>
  );
};

export default AudioUploader;
