import { useState, useRef } from 'react';
import { api } from '../api/client';

export default function IngestForm() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      await uploadFile(file);
    } else {
      setError('Please upload a valid PDF file.');
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file: File) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name.replace('.pdf', ''));

    try {
      const response = await api.ingestPaper(formData);
      setSuccess(`Success! Ingested paper as ${response.chunk_count} semantic chunks.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="card fade-in">
      <div className="card-header">
        <h3 className="card-title">Ingest Literature</h3>
      </div>

      <div
        className="upload-zone"
        onDragOver={e => { e.preventDefault(); e.currentTarget.classList.add('dragover'); }}
        onDragLeave={e => { e.preventDefault(); e.currentTarget.classList.remove('dragover'); }}
        onDrop={e => { e.currentTarget.classList.remove('dragover'); handleFileDrop(e); }}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <div className="upload-text">Drag and drop a PDF paper here</div>
        <div className="upload-subtext">or click to browse files</div>

        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept="application/pdf"
          onChange={handleFileSelect}
        />

        {loading && (
          <div className="mt-2">
            <span className="loading-spinner"><span className="spinner"></span> Processing document...</span>
          </div>
        )}
      </div>

      {error && <div className="error-message mt-2">{error}</div>}
      {success && <div className="success-message mt-2">{success}</div>}
    </div>
  );
}
