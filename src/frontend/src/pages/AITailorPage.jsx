import React, { useState } from 'react';
import { Sparkles, FileCheck, Copy, Send } from 'lucide-react';

export default function AITailorPage() {
  const [jobDescription, setJobDescription] = useState('');
  const [targetRole, setTargetRole] = useState('Full Stack Engineer');
  const [tailorResult, setTailorResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTailor = async () => {
    if (!jobDescription) return alert('Please enter a target job description.');
    setLoading(true);
    try {
      const res = await fetch('/api/llm/tailor-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: "Master Resume Data",
          job_description: jobDescription,
          target_role: targetRole
        })
      });
      const data = await res.json();
      setTailorResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', maxWidth: '1200px' }}>
      {/* Input Form */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={20} color="var(--accent-purple)" /> AI Tailor Engine
        </h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Paste target job posting description to generate optimized resume bullet points & keywords.
        </p>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
            Target Position Title
          </label>
          <input type="text" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="glass-input" />
        </div>

        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
            LinkedIn Job Description
          </label>
          <textarea 
            rows={10} 
            value={jobDescription} 
            onChange={(e) => setJobDescription(e.target.value)} 
            placeholder="Paste job posting text here..." 
            className="glass-input"
            style={{ resize: 'vertical' }}
          />
        </div>

        <button onClick={handleTailor} className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
          {loading ? 'Analyzing Keywords...' : 'Generate Tailored Resume & Cover Letter'}
        </button>
      </div>

      {/* Output Panel */}
      <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column' }}>
        <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
          Tailored Analysis Output
        </h4>

        {tailorResult ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1, overflowY: 'auto' }}>
            <div style={{
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              padding: '1rem',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 700 }}>ATS MATCH SCORE</span>
                <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff' }}>{tailorResult.match_score}%</h3>
              </div>
              <span className="badge badge-emerald">High Compatibility</span>
            </div>

            <div>
              <h5 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Target Keywords to Highlight:</h5>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {tailorResult.recommended_keywords?.map((kw, i) => (
                  <span key={i} className="badge badge-indigo">{kw}</span>
                ))}
              </div>
            </div>

            <div>
              <h5 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Suggested Bullet Points:</h5>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '0.88rem', color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {tailorResult.suggested_bullet_points?.map((pt, i) => (
                  <li key={i}>{pt}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', textAlign: 'center', flexDirection: 'column', gap: '0.5rem' }}>
            <FileCheck size={40} color="var(--glass-border)" />
            <p style={{ fontSize: '0.88rem' }}>Enter job text and run the LLM Tailor Engine to view match metrics.</p>
          </div>
        )}
      </div>
    </div>
  );
}
