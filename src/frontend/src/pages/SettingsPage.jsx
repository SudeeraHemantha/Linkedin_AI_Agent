import React, { useState } from 'react';
import { Settings, Shield, Sliders, Key, Save } from 'lucide-react';

export default function SettingsPage() {
  const [chromePath, setChromePath] = useState('C:\\Users\\Elite computers\\AppData\\Local\\Google\\Chrome\\User Data\\Default');
  const [openaiKey, setOpenaiKey] = useState('sk-local-mock-key-••••••••••••');
  const [minDelay, setMinDelay] = useState(1.2);
  const [maxDelay, setMaxDelay] = useState(3.5);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div style={{ maxWidth: '850px' }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Settings size={22} color="var(--accent-cyan)" /> Agent & Security Configuration
        </h3>

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
              Local Chrome Profile Path (for Persistent Login State)
            </label>
            <input type="text" value={chromePath} onChange={(e) => setChromePath(e.target.value)} className="glass-input" />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.25rem', display: 'block' }}>
              Playwright attaches directly to this profile to bypass 2FA challenges.
            </span>
          </div>

          <div>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
              OpenAI / Anthropic API Key (Local Storage Only)
            </label>
            <input type="password" value={openaiKey} onChange={(e) => setOpenaiKey(e.target.value)} className="glass-input" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Minimum Human Delay (Seconds): {minDelay}s
              </label>
              <input 
                type="range" 
                min="0.5" 
                max="3.0" 
                step="0.1" 
                value={minDelay} 
                onChange={(e) => setMinDelay(parseFloat(e.target.value))} 
                style={{ width: '100%' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Maximum Human Delay (Seconds): {maxDelay}s
              </label>
              <input 
                type="range" 
                min="2.0" 
                max="8.0" 
                step="0.2" 
                value={maxDelay} 
                onChange={(e) => setMaxDelay(parseFloat(e.target.value))} 
                style={{ width: '100%' }}
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" style={{ width: 'fit-content' }}>
            <Save size={18} /> {saved ? 'Configuration Saved!' : 'Save System Settings'}
          </button>
        </form>
      </div>
    </div>
  );
}
