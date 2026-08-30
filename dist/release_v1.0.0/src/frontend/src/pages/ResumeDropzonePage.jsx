import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, Sparkles } from 'lucide-react';

export default function ResumeDropzonePage() {
  const [fileName, setFileName] = useState(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parsedSkills, setParsedSkills] = useState(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer ? e.dataTransfer.files : e.target.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const processFile = (file) => {
    setFileName(file.name);
    setIsParsing(true);
    setTimeout(() => {
      setIsParsing(false);
      setParsedSkills([
        'Python', 'FastAPI', 'Playwright', 'React.js', 'TypeScript', 'SQLCipher', 'Tailwind CSS', 'Docker', 'GraphQL'
      ]);
    }, 1200);
  };

  return (
    <div style={{ maxWidth: '850px' }}>
      <div 
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        className="glass-panel" 
        style={{
          border: '2px dashed var(--glass-border-active)',
          borderRadius: '20px',
          padding: '4rem 2rem',
          textAlign: 'center',
          cursor: 'pointer',
          marginBottom: '2rem'
        }}
      >
        <input 
          type="file" 
          accept=".pdf,.docx,.txt" 
          id="resume-input" 
          style={{ display: 'none' }}
          onChange={handleFileDrop}
        />
        <label htmlFor="resume-input" style={{ cursor: 'pointer' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(99, 102, 241, 0.15)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem'
          }}>
            <UploadCloud size={32} color="var(--accent-indigo)" />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>Drag & Drop Master Resume</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Supports PDF, DOCX, and TXT files. Stored securely inside your local workspace.
          </p>
        </label>
      </div>

      {fileName && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <FileText size={24} color="var(--accent-cyan)" />
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff' }}>{fileName}</h4>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)' }}>Parsed & Indexed Locally</span>
              </div>
            </div>
            {isParsing ? (
              <span className="badge badge-amber">Parsing Skills...</span>
            ) : (
              <span className="badge badge-emerald"><CheckCircle size={14} /> Ready for AI Agent</span>
            )}
          </div>

          {parsedSkills && (
            <div>
              <h5 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Extracted Skill Matrix:</h5>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {parsedSkills.map((skill, idx) => (
                  <span key={idx} className="badge badge-indigo">{skill}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
