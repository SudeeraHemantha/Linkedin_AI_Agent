import React, { useState } from 'react';
import { User, Briefcase, MapPin, Globe, Save } from 'lucide-react';

export default function ProfilePage({ user }) {
  const [targetRole, setTargetRole] = useState('Senior Full Stack Engineer');
  const [location, setLocation] = useState('Remote - US & Canada');
  const [minSalary, setMinSalary] = useState('140,000');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div style={{ maxWidth: '800px' }}>
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
            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff' }}>{user?.full_name || 'Alex Mercer'}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user?.email || 'alex@enterprise.com'}</p>
          </div>
        </div>

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Primary Target Role
              </label>
              <input type="text" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="glass-input" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Preferred Location / Remote
              </label>
              <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} className="glass-input" />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
              Minimum Target Salary ($ USD)
            </label>
            <input type="text" value={minSalary} onChange={(e) => setMinSalary(e.target.value)} className="glass-input" />
          </div>

          <button type="submit" className="btn-primary" style={{ width: 'fit-content' }}>
            <Save size={18} /> {saved ? 'Profile Saved!' : 'Save Career Preferences'}
          </button>
        </form>
      </div>
    </div>
  );
}
