import React, { useState } from 'react';
import { Home, Briefcase, Bookmark, RefreshCw, Globe, Shield } from 'lucide-react';

export default function HybridWorkspaceView() {
  const [activeUrl, setActiveUrl] = useState("https://www.linkedin.com/feed/");
  const [isLoading, setIsLoading] = useState(false);

  const handleNavigate = (url) => {
    setIsLoading(true);
    setActiveUrl(url);
    setTimeout(() => setIsLoading(false), 800);
  };

  return (
    <div style={{
      display: 'flex',
      height: '620px',
      width: '100%',
      backgroundColor: '#020617',
      color: '#f8fafc',
      borderRadius: '16px',
      overflow: 'hidden',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      marginTop: '1.5rem'
    }}>
      {/* LEFT CONTROL PANEL (Your App's Workspace Commands) */}
      <div style={{
        width: '35%',
        backgroundColor: '#0f172a',
        padding: '1.5rem',
        borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#3b82f6', marginBottom: '0.4rem' }}>
            Hybrid Workspace Bridge
          </h2>
          <p style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '1.5rem', lineHeight: '1.4' }}>
            Interact with LinkedIn live in the central viewport while your autonomous agent monitors prerequisites and processes Groq AI tailoring.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <button 
              onClick={() => handleNavigate("https://www.linkedin.com/feed/")}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: activeUrl.includes('/feed/') ? '#2563eb' : '#1e293b',
                color: '#ffffff',
                borderRadius: '8px',
                fontSize: '0.88rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.2s'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Home size={16} /> Open LinkedIn Feed
              </span>
              {activeUrl.includes('/feed/') && (
                <span style={{ fontSize: '0.7rem', backgroundColor: '#1d4ed8', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>Active</span>
              )}
            </button>

            <button 
              onClick={() => handleNavigate("https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=Remote")}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: activeUrl.includes('/jobs/') ? '#2563eb' : '#1e293b',
                color: '#ffffff',
                borderRadius: '8px',
                fontSize: '0.88rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.2s'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Briefcase size={16} /> Open Job Search Hub
              </span>
              {activeUrl.includes('/jobs/') && (
                <span style={{ fontSize: '0.7rem', backgroundColor: '#1d4ed8', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>Active</span>
              )}
            </button>

            <button 
              onClick={() => handleNavigate("https://www.linkedin.com/my-items/saved-jobs/")}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: activeUrl.includes('/saved-jobs/') ? '#2563eb' : '#1e293b',
                color: '#ffffff',
                borderRadius: '8px',
                fontSize: '0.88rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.2s'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Bookmark size={16} /> Saved Applications Queue
              </span>
              {activeUrl.includes('/saved-jobs/') && (
                <span style={{ fontSize: '0.7rem', backgroundColor: '#1d4ed8', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>Active</span>
              )}
            </button>
          </div>
        </div>

        <div style={{ backgroundColor: '#020617', padding: '1rem', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#4ade80', marginBottom: '0.25rem' }}>
            ● HYBRID ENGINE ONLINE
          </div>
          <p style={{ fontSize: '0.72rem', color: '#94a3b8', wordBreak: 'break-all' }}>
            Viewport target: <span style={{ color: '#e2e8f0' }}>{activeUrl}</span>
          </p>
        </div>
      </div>

      {/* CENTRAL LIVE VIEWPORT (LinkedIn Embedded Frame) */}
      <div style={{ width: '65%', backgroundColor: '#000000', display: 'flex', flexDirection: 'column', position: 'relative' }}>
        {isLoading && (
          <div style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: 'rgba(2, 6, 23, 0.85)',
            zIndex: 20,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#60a5fa',
            fontSize: '0.88rem',
            fontFamily: 'monospace'
          }}>
            Loading Workspace Viewport...
          </div>
        )}
        
        {/* Viewport Header Bar */}
        <div style={{
          backgroundColor: '#0f172a',
          padding: '0.6rem 1rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.78rem',
          color: '#94a3b8',
          fontFamily: 'monospace'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444' }}></div>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#eab308' }}></div>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#22c55e' }}></div>
            <span style={{ marginLeft: '0.5rem', color: '#cbd5e1' }}>Secure Viewport: {activeUrl}</span>
          </div>
          <button 
            onClick={() => {
              const iframe = document.getElementById('linkedin-viewport');
              if (iframe) iframe.src = activeUrl;
            }}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.75rem'
            }}
          >
            <RefreshCw size={13} /> Refresh View
          </button>
        </div>

        {/* Embedded Browser Frame */}
        <iframe 
          id="linkedin-viewport"
          src={activeUrl}
          title="LinkedIn Workspace Viewport"
          style={{ width: '100%', height: '100%', border: 'none', backgroundColor: '#ffffff' }}
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        />
      </div>
    </div>
  );
}
