import React, { useState } from 'react';
import { Activity, CheckCircle, Clock, ExternalLink, Filter } from 'lucide-react';

export default function LiveTrackerPage() {
  const [filter, setFilter] = useState('ALL');
  
  const applications = [
    { id: 1, title: 'Senior Full Stack Engineer', company: 'TechScale Inc.', location: 'Remote - US', url: 'https://linkedin.com', status: 'APPLIED', score: 94, date: '2026-08-30' },
    { id: 2, title: 'Lead Python Architect', company: 'DataDrive AI', location: 'Remote - Global', url: 'https://linkedin.com', status: 'INTERVIEWING', score: 98, date: '2026-08-29' },
    { id: 3, title: 'Autonomous Systems Engineer', company: 'CyberEdge Labs', location: 'Hybrid - NY', url: 'https://linkedin.com', status: 'APPLIED', score: 89, date: '2026-08-28' },
    { id: 4, title: 'Backend Cloud Developer', company: 'CloudNimbus Systems', location: 'Remote', url: 'https://linkedin.com', status: 'OFFER', score: 96, date: '2026-08-25' }
  ];

  const filteredApps = filter === 'ALL' ? applications : applications.filter(a => a.status === filter);

  return (
    <div style={{ maxWidth: '1200px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem', marginBottom: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Applications Sent</span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', marginTop: '0.25rem' }}>42</h3>
        </div>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Average ATS Match</span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>93.8%</h3>
        </div>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Active Interviews</span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-indigo)', marginTop: '0.25rem' }}>3</h3>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>Application Audit Log</h4>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {['ALL', 'APPLIED', 'INTERVIEWING', 'OFFER'].map((st) => (
              <button 
                key={st}
                onClick={() => setFilter(st)}
                style={{
                  background: filter === st ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                  border: filter === st ? '1px solid var(--accent-indigo)' : '1px solid var(--glass-border)',
                  color: filter === st ? '#fff' : 'var(--text-muted)',
                  padding: '0.35rem 0.75rem',
                  borderRadius: '8px',
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
              <th style={{ padding: '0.75rem 1rem' }}>JOB TITLE & COMPANY</th>
              <th style={{ padding: '0.75rem 1rem' }}>LOCATION</th>
              <th style={{ padding: '0.75rem 1rem' }}>MATCH SCORE</th>
              <th style={{ padding: '0.75rem 1rem' }}>STATUS</th>
              <th style={{ padding: '0.75rem 1rem' }}>APPLIED DATE</th>
              <th style={{ padding: '0.75rem 1rem' }}>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {filteredApps.map((app) => (
              <tr key={app.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '1rem' }}>
                  <div style={{ fontWeight: 700, color: '#fff' }}>{app.title}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{app.company}</div>
                </td>
                <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{app.location}</td>
                <td style={{ padding: '1rem' }}>
                  <span className="badge badge-emerald">{app.score}% Match</span>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span className={app.status === 'OFFER' ? 'badge badge-emerald' : app.status === 'INTERVIEWING' ? 'badge badge-indigo' : 'badge badge-amber'}>
                    {app.status}
                  </span>
                </td>
                <td style={{ padding: '1rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{app.date}</td>
                <td style={{ padding: '1rem' }}>
                  <a href={app.url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-cyan)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    View <ExternalLink size={14} />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
