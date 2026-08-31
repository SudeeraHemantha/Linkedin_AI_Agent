import React, { useState, useEffect } from 'react';
import { User, Briefcase, MapPin, Globe, Save, CheckCircle2, AlertCircle, Link, ShieldCheck, Loader2 } from 'lucide-react';

export default function ProfilePage({ user }) {
  const [targetRoles, setTargetRoles] = useState('Software Engineer');
  const [techStack, setTechStack] = useState('Full Stack');
  const [workMode, setWorkMode] = useState('Remote');
  const [geography, setGeography] = useState('Global');
  const [minSalary, setMinSalary] = useState(120000);
  
  const [loading, setLoading] = useState(false);
  const [savedStatus, setSavedStatus] = useState(null); // 'success' | 'error' | null

  // LinkedIn Session Bridge states
  const [linkedinStatus, setLinkedinStatus] = useState('disconnected'); // 'connected' | 'disconnected'
  const [connectingLinkedin, setConnectingLinkedin] = useState(false);
  const [linkedinMessage, setLinkedinMessage] = useState(null);

  useEffect(() => {
    // Fetch saved preferences on mount
    fetch('http://127.0.0.1:8000/api/preferences?user_id=1')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          if (data.target_roles) setTargetRoles(data.target_roles);
          if (data.tech_stack) setTechStack(data.tech_stack);
          if (data.work_mode) setWorkMode(data.work_mode);
          if (data.geography) setGeography(data.geography);
          if (data.min_salary !== undefined) setMinSalary(data.min_salary);
        }
      })
      .catch((err) => console.warn('[PREFERENCES FETCH WARN]', err));

    // Fetch LinkedIn Session Status
    fetch('http://127.0.0.1:8000/api/linkedin/status')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.status) {
          setLinkedinStatus(data.status);
        }
      })
      .catch((err) => console.warn('[LINKEDIN STATUS FETCH WARN]', err));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSavedStatus(null);

    const payload = {
      user_id: 1,
      target_roles: targetRoles,
      tech_stack: techStack,
      work_mode: workMode,
      geography: geography,
      min_salary: parseInt(minSalary, 10) || 0
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setSavedStatus('success');
      } else {
        setSavedStatus('error');
      }
    } catch (err) {
      console.error('[PREFERENCES SAVE ERROR]', err);
      setSavedStatus('error');
    } finally {
      setLoading(false);
      setTimeout(() => setSavedStatus(null), 3000);
    }
  };

  const handleConnectLinkedin = async () => {
    setConnectingLinkedin(true);
    setLinkedinMessage('Opening interactive browser... Please log into LinkedIn in the pop-up window.');

    try {
      const res = await fetch('http://127.0.0.1:8000/api/linkedin/connect', {
        method: 'POST'
      });
      const data = await res.json();

      if (res.ok && data.status === 'connected') {
        setLinkedinStatus('connected');
        setLinkedinMessage('LinkedIn session cookies successfully captured and stored!');
      } else {
        setLinkedinMessage(data.detail || data.message || 'Failed to authenticate LinkedIn session.');
      }
    } catch (err) {
      console.error('[LINKEDIN CONNECT ERROR]', err);
      setLinkedinMessage('Connection error. Ensure backend server is active.');
    } finally {
      setConnectingLinkedin(false);
    }
  };

  return (
    <div style={{ maxWidth: '850px' }}>
      {/* LinkedIn Session Bridge Glass Panel */}
      <div className="glass-panel" style={{ padding: '1.75rem', marginBottom: '1.5rem', borderLeft: '4px solid #0a66c2' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.3rem' }}>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>LinkedIn Live Session Bridge</h4>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px',
                background: linkedinStatus === 'connected' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                color: linkedinStatus === 'connected' ? '#10b981' : '#f59e0b',
                border: `1px solid ${linkedinStatus === 'connected' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`
              }}>
                {linkedinStatus === 'connected' ? '● Session Connected' : '○ Not Authenticated'}
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Authorize your live LinkedIn account session so the autonomous Playwright worker can apply to Easy Apply jobs.
            </p>
          </div>

          <button
            type="button"
            onClick={handleConnectLinkedin}
            disabled={connectingLinkedin}
            className="btn-primary"
            style={{ background: '#0a66c2', borderColor: '#0a66c2' }}
          >
            {connectingLinkedin ? (
              <>
                <Loader2 className="animate-spin" size={18} /> Connecting Browser...
              </>
            ) : (
              <>
                <Link size={18} /> Connect / Authenticate LinkedIn Session
              </>
            )}
          </button>
        </div>

        {linkedinMessage && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            background: connectingLinkedin ? 'rgba(59, 130, 246, 0.15)' : linkedinStatus === 'connected' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${connectingLinkedin ? 'rgba(59, 130, 246, 0.4)' : linkedinStatus === 'connected' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
            color: connectingLinkedin ? '#60a5fa' : linkedinStatus === 'connected' ? '#10b981' : '#ef4444',
            fontSize: '0.88rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            {connectingLinkedin ? <Loader2 className="animate-spin" size={16} /> : linkedinStatus === 'connected' ? <ShieldCheck size={16} /> : <AlertCircle size={16} />}
            {linkedinMessage}
          </div>
        )}
      </div>

      {/* Main Preferences Settings Card */}
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '2rem' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-indigo))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
            fontWeight: 800
          }}>
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'A'}
          </div>
          <div>
            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff' }}>{user?.full_name || 'Enterprise Candidate'}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user?.email || 'candidate@enterprise.com'}</p>
          </div>
        </div>

        {savedStatus === 'success' && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            color: '#10b981',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.9rem',
            fontWeight: 600
          }}>
            <CheckCircle2 size={18} /> Career preferences synchronized with backend SQLite database!
          </div>
        )}

        {savedStatus === 'error' && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            color: '#ef4444',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.9rem',
            fontWeight: 600
          }}>
            <AlertCircle size={18} /> Failed to save preferences. Ensure backend server is active.
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                Primary Target Roles
              </label>
              <input
                type="text"
                value={targetRoles}
                onChange={(e) => setTargetRoles(e.target.value)}
                placeholder="e.g. Lead Architect, Software Engineer"
                className="glass-input"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                Technical Stack Specialty
              </label>
              <select
                value={techStack}
                onChange={(e) => setTechStack(e.target.value)}
                className="glass-input"
                style={{ background: '#111827', color: '#fff' }}
              >
                <option value="Backend">Backend Engineering</option>
                <option value="Frontend">Frontend Engineering</option>
                <option value="Full Stack">Full Stack Engineering</option>
                <option value="AI / ML">AI / Machine Learning Systems</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                Preferred Work Mode
              </label>
              <select
                value={workMode}
                onChange={(e) => setWorkMode(e.target.value)}
                className="glass-input"
                style={{ background: '#111827', color: '#fff' }}
              >
                <option value="Remote">100% Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="Onsite">On-Site</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                Target Geography / Region
              </label>
              <select
                value={geography}
                onChange={(e) => setGeography(e.target.value)}
                className="glass-input"
                style={{ background: '#111827', color: '#fff' }}
              >
                <option value="Global">Global / Worldwide</option>
                <option value="US">United States</option>
                <option value="EU">European Union</option>
                <option value="Local">Local Region</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
              Minimum Target Salary ($ USD per year)
            </label>
            <input
              type="number"
              value={minSalary}
              onChange={(e) => setMinSalary(e.target.value)}
              step="5000"
              min="0"
              className="glass-input"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width: 'fit-content', marginTop: '0.5rem' }}
          >
            <Save size={18} /> {loading ? 'Saving...' : 'Save Career Preferences'}
          </button>
        </form>
      </div>
    </div>
  );
}
