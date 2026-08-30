import React, { useState, useEffect } from 'react';
import { Play, Pause, Bot, ShieldCheck, Activity, Terminal, CheckCircle2 } from 'lucide-react';

export default function AutoPilotPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [keywords, setKeywords] = useState('Full Stack Engineer');
  const [location, setLocation] = useState('Remote');
  const [logs, setLogs] = useState([
    { time: '13:30:01', level: 'INFO', msg: 'Agent stealth engine initialized with Chrome persistent context.' },
    { time: '13:30:04', level: 'SUCCESS', msg: 'Session verified: Authenticated as active LinkedIn user.' }
  ]);
  const [appliedCount, setAppliedCount] = useState(14);

  const toggleAgent = () => {
    if (!isRunning) {
      setIsRunning(true);
      const newLog = {
        time: new Date().toLocaleTimeString(),
        level: 'INFO',
        msg: `Starting autonomous job application runner for [${keywords}] in [${location}]...`
      };
      setLogs(prev => [newLog, ...prev]);
    } else {
      setIsRunning(false);
      const newLog = {
        time: new Date().toLocaleTimeString(),
        level: 'WARN',
        msg: 'Agent paused by user.'
      };
      setLogs(prev => [newLog, ...prev]);
    }
  };

  useEffect(() => {
    let interval;
    if (isRunning) {
      interval = setInterval(() => {
        setAppliedCount(c => c + 1);
        const sampleLogs = [
          `Parsing job posting: Lead Python Developer at TechNova...`,
          `Simulating Bezier cursor move (24 points) to Easy Apply button...`,
          `Solving application form steps & submitting resume...`,
          `Application successfully logged to SQLite database.`
        ];
        const randomMsg = sampleLogs[Math.floor(Math.random() * sampleLogs.length)];
        setLogs(prev => [{
          time: new Date().toLocaleTimeString(),
          level: 'SUCCESS',
          msg: randomMsg
        }, ...prev]);
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', maxWidth: '1250px' }}>
      {/* Control Panel Sidebar */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: isRunning ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Bot size={24} color={isRunning ? 'var(--accent-emerald)' : 'var(--accent-indigo)'} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff' }}>Auto-Pilot Control</h3>
            <span className={isRunning ? 'badge badge-emerald' : 'badge badge-amber'}>
              {isRunning ? 'AGENT ACTIVE' : 'PAUSED'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Target Job Search Keywords</label>
            <input type="text" value={keywords} onChange={(e) => setKeywords(e.target.value)} className="glass-input" disabled={isRunning} />
          </div>
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Location Filter</label>
            <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} className="glass-input" disabled={isRunning} />
          </div>
        </div>

        <button 
          onClick={toggleAgent} 
          className="btn-primary" 
          style={{ 
            width: '100%', 
            justifyContent: 'center',
            background: isRunning ? 'linear-gradient(135deg, #f43f5e, #e11d48)' : 'linear-gradient(135deg, #10b981, #059669)'
          }}
        >
          {isRunning ? <><Pause size={18} /> Stop Auto-Pilot</> : <><Play size={18} /> Launch Auto-Pilot Agent</>}
        </button>

        {/* Quick Stats */}
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--glass-border)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.75rem', borderRadius: '10px' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Total Submitted</span>
            <h4 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff' }}>{appliedCount}</h4>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.75rem', borderRadius: '10px' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Stealth Mode</span>
            <h4 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>100%</h4>
          </div>
        </div>
      </div>

      {/* Terminal Real-Time Logs */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', background: '#070a0f' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Terminal size={18} color="var(--accent-cyan)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', fontFamily: 'var(--font-mono)' }}>
              Agent Telemetry Stream
            </h4>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            Playwright Stealth Runtime v1.0
          </span>
        </div>

        <div style={{
          flex: 1,
          fontFamily: 'var(--font-mono)',
          fontSize: '0.82rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.6rem',
          overflowY: 'auto',
          maxHeight: '520px'
        }}>
          {logs.map((log, index) => (
            <div key={index} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <span style={{ color: 'var(--text-dim)' }}>[{log.time}]</span>
              <span style={{
                color: log.level === 'SUCCESS' ? 'var(--accent-emerald)' : log.level === 'WARN' ? 'var(--accent-amber)' : 'var(--accent-cyan)',
                fontWeight: 600,
                minWidth: '65px'
              }}>
                {log.level}
              </span>
              <span style={{ color: '#e2e8f0' }}>{log.msg}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
