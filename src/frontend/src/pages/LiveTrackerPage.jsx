import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, Clock, ExternalLink, Filter, Inbox } from 'lucide-react';

export default function LiveTrackerPage() {
  const [filter, setFilter] = useState('ALL');
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/applications?user_id=1')
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        if (Array.isArray(data)) {
          setApplications(data);
        }
      })
      .catch((err) => console.warn('[LIVE TRACKER FETCH WARN]', err))
      .finally(() => setLoading(false));
  }, []);

  const filteredApps = filter === 'ALL'
    ? applications
    : applications.filter(a => (a.status || '').toUpperCase() === filter);

  const totalCount = applications.length;
  const avgScore = totalCount > 0
    ? (applications.reduce((acc, curr) => acc + (curr.match_score || curr.score || 85), 0) / totalCount).toFixed(1)
    : '0.0';

  return (
    <div style={{ maxWidth: '1200px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem', marginBottom: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Submitted Applications</span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', marginTop: '0.25rem' }}>{totalCount}</h3>
        </div>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Average ATS Match Score</span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>{avgScore}%</h3>
        </div>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Live SQLite Storage</span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-indigo)', marginTop: '0.25rem' }}>Active</h3>
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

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading live application records from SQLite...
          </div>
        ) : filteredApps.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Inbox size={48} style={{ opacity: 0.4, marginBottom: '1rem' }} />
            <h4 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '0.4rem' }}>No Live Applications Logged Yet</h4>
            <p style={{ fontSize: '0.88rem', maxWidth: '480px', margin: '0 auto' }}>
              Launch the Auto-Pilot Agent on the Auto-Pilot page to harvest matching roles and submit live applications.
            </p>
          </div>
        ) : (
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
              {filteredApps.map((app, idx) => (
                <tr key={app.id || idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ fontWeight: 700, color: '#fff' }}>{app.job_title || app.title}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{app.company}</div>
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{app.location || 'Remote'}</td>
                  <td style={{ padding: '1rem' }}>
                    <span className="badge badge-emerald">{(app.match_score || app.score || 85).toFixed(0)}% Match</span>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <span className={app.status === 'OFFER' ? 'badge badge-emerald' : app.status === 'INTERVIEWING' ? 'badge badge-indigo' : 'badge badge-amber'}>
                      {app.status}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    {app.applied_at ? app.applied_at.substring(0, 10) : 'Just Now'}
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <a href={app.job_url || app.url || '#'} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-cyan)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      View <ExternalLink size={14} />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
