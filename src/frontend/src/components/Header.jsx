import React from 'react';
import { Search, Bell, Shield, Cpu } from 'lucide-react';

export default function Header({ title }) {
  return (
    <header style={{
      height: '70px',
      background: 'rgba(10, 13, 20, 0.8)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--glass-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>{title}</h2>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Local Autonomous Hybrid Architecture</p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Search Bar */}
        <div style={{ position: 'relative', width: '260px' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          <input 
            type="text" 
            placeholder="Search applications, logs..." 
            className="glass-input"
            style={{ paddingLeft: '36px', fontSize: '0.85rem' }}
          />
        </div>

        {/* System Health Badge */}
        <div className="glass-panel" style={{ padding: '0.4rem 0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={16} color="var(--accent-emerald)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>Engine Ready</span>
        </div>

        <button className="glass-panel" style={{ padding: '0.5rem', cursor: 'pointer', display: 'flex' }}>
          <Bell size={18} color="var(--text-muted)" />
        </button>
      </div>
    </header>
  );
}
