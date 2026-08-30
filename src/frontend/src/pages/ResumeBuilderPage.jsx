import React, { useState } from 'react';
import { Plus, Trash2, Save, Sparkles } from 'lucide-react';

export default function ResumeBuilderPage() {
  const [experiences, setExperiences] = useState([
    { id: 1, title: 'Senior Software Engineer', company: 'Acme Corp', duration: '2023 - Present', details: 'Built high-concurrency microservices and Playwright scrapers.' }
  ]);

  const addExperience = () => {
    setExperiences([
      ...experiences,
      { id: Date.now(), title: '', company: '', duration: '', details: '' }
    ]);
  };

  const removeExperience = (id) => {
    setExperiences(experiences.filter(e => e.id !== id));
  };

  return (
    <div style={{ maxWidth: '850px' }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>Structured Resume Builder</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Manually fine-tune work history for the AI Tailor module.</p>
          </div>
          <button onClick={addExperience} className="btn-secondary">
            <Plus size={16} /> Add Position
          </button>
        </div>

        {experiences.map((exp, index) => (
          <div key={exp.id} style={{
            background: 'rgba(15, 23, 42, 0.4)',
            border: '1px solid var(--glass-border)',
            borderRadius: '12px',
            padding: '1.25rem',
            marginBottom: '1.25rem',
            position: 'relative'
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Job Title</label>
                <input type="text" defaultValue={exp.title} className="glass-input" />
              </div>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Company</label>
                <input type="text" defaultValue={exp.company} className="glass-input" />
              </div>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Duration</label>
                <input type="text" defaultValue={exp.duration} className="glass-input" />
              </div>
            </div>
            <div>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Responsibilities & Key Achievements</label>
              <textarea defaultValue={exp.details} rows={3} className="glass-input" style={{ resize: 'vertical' }} />
            </div>
            <button 
              onClick={() => removeExperience(exp.id)}
              style={{
                position: 'absolute',
                top: '12px',
                right: '12px',
                background: 'none',
                border: 'none',
                color: 'var(--accent-rose)',
                cursor: 'pointer'
              }}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}

        <button className="btn-primary">
          <Save size={18} /> Save Resume Data
        </button>
      </div>
    </div>
  );
}
