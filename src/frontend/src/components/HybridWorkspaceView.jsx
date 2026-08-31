import React, { useState } from 'react';
import { Home, Briefcase, Bookmark, ExternalLink, ShieldCheck, Monitor, Rocket } from 'lucide-react';

export default function HybridWorkspaceView() {
  const [activeUrl, setActiveUrl] = useState("https://www.linkedin.com/feed/");
  const [isLaunching, setIsLaunching] = useState(false);

  const handleLaunchNativeWindow = async (url) => {
    setIsLaunching(true);
    setActiveUrl(url);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/linkedin/launch-workspace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_url: url })
      });
      const data = await res.json();
      if (data && data.status === "success") {
        console.log(`[SUCCESS] Launched native workspace window at ${url}`);
      } else {
        window.open(url, '_blank');
      }
    } catch (err) {
      console.error(`[ERROR] Network error launching workspace: ${err.message}`);
      window.open(url, '_blank');
    } finally {
      setIsLaunching(false);
    }
  };


  return (
    <div style={{
      display: 'flex',
      height: '420px',
      width: '100%',
      backgroundColor: '#020617',
      color: '#f8fafc',
      borderRadius: '16px',
      overflow: 'hidden',
      border: '1px solid rgba(59, 130, 246, 0.3)',
      marginTop: '1.5rem',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
    }}>
      {/* LEFT CONTROL PANEL */}
      <div style={{
        width: '38%',
        backgroundColor: '#0f172a',
        padding: '1.5rem',
        borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <ShieldCheck size={20} color="#3b82f6" />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#3b82f6' }}>
              Secure Pop-Out Workspace Bridge
            </h2>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1.25rem', lineHeight: '1.4' }}>
            LinkedIn blocks external iframe embedding via X-Frame-Options. Launch a dedicated autonomous session window that syncs with your stored cookies.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <button 
              onClick={() => handleLaunchNativeWindow("https://www.linkedin.com/feed/")}
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
                justifyContent: 'space-between'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Home size={16} /> Open LinkedIn Feed Window
              </span>
              <ExternalLink size={14} />
            </button>

            <button 
              onClick={() => handleLaunchNativeWindow("https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=Remote")}
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
                justifyContent: 'space-between'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Briefcase size={16} /> Open Job Search Hub Window
              </span>
              <ExternalLink size={14} />
            </button>

            <button 
              onClick={() => handleLaunchNativeWindow("https://www.linkedin.com/my-items/saved-jobs/")}
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
                justifyContent: 'space-between'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Bookmark size={16} /> Open Saved Applications Queue
              </span>
              <ExternalLink size={14} />
            </button>
          </div>
        </div>

        <div style={{ backgroundColor: '#020617', padding: '0.85rem 1rem', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#4ade80', marginBottom: '0.2rem' }}>
            ● NATIVE PLAYWRIGHT ENGINE READY
          </div>
          <p style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
            Cookies locked: <span style={{ color: '#e2e8f0' }}>%APPDATA%\LinkedInAgent\linkedin_cookies.json</span>
          </p>
        </div>
      </div>

      {/* RIGHT CENTRAL CONTROL DASHBOARD */}
      <div style={{
        width: '62%',
        backgroundColor: '#070a0f',
        padding: '2rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        position: 'relative'
      }}>
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '20px',
          background: 'linear-gradient(135deg, #0a66c2, #3b82f6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.25rem',
          boxShadow: '0 8px 24px rgba(10, 102, 194, 0.4)'
        }}>
          <Monitor size={36} color="#ffffff" />
        </div>

        <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#ffffff', marginBottom: '0.5rem' }}>
          Autonomous Workspace Browser Window
        </h3>
        <p style={{ fontSize: '0.88rem', color: '#94a3b8', maxWidth: '440px', lineHeight: '1.5', marginBottom: '1.5rem' }}>
          Launches an independent, secure Chrome session pre-configured with your verified session cookies. Interact natively with full bypass of X-Frame-Options restrictions.
        </p>

        <button
          onClick={() => handleLaunchNativeWindow(activeUrl)}
          disabled={isLaunching}
          style={{
            padding: '0.85rem 1.75rem',
            backgroundColor: '#0a66c2',
            color: '#ffffff',
            borderRadius: '10px',
            fontSize: '0.92rem',
            fontWeight: 700,
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            boxShadow: '0 4px 14px rgba(10, 102, 194, 0.4)'
          }}
        >
          {isLaunching ? (
            <>Launching Browser Session...</>
          ) : (
            <><Rocket size={18} /> Launch Native Workspace Window</>
          )}
        </button>
      </div>
    </div>
  );
}
