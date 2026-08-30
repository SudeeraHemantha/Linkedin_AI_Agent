import React, { useState } from 'react';
import { Shield, KeyRound, Mail, User, Lock, ArrowRight, CheckCircle2, Sparkles, AlertCircle, Loader2 } from 'lucide-react';

export default function AuthPage({ onLoginSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register' | 'forgot'
  const [showOtpModal, setShowOtpModal] = useState(false);
  
  // Form State
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [debugOtp, setDebugOtp] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [errorCode, setErrorCode] = useState('');
  const [loading, setLoading] = useState(false);

  // Helper to safely parse JSON response or return fallback error object
  const parseJsonResponse = async (res) => {
    try {
      const text = await res.text();
      if (!text || text.trim() === '') {
        return { detail: 'Server returned an empty response.', code: 'EMPTY_RESPONSE' };
      }
      const data = JSON.parse(text);
      if (Array.isArray(data.detail)) {
        // Format Pydantic validation errors nicely
        const msg = data.detail.map(err => err.msg.replace('Value error, ', '')).join(' | ');
        return { detail: msg, error: msg, code: 'VALIDATION_ERROR' };
      }
      return data;
    } catch (err) {
      return { detail: 'Server error or invalid response format.', code: 'PARSING_ERROR' };
    }
  };

  // Handle Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setErrorCode('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username_or_email: username, password })
      });
      const data = await parseJsonResponse(res);
      if (!res.ok) {
        setErrorCode(data.code || 'INVALID_CREDENTIALS');
        throw new Error(data.error || data.detail || 'Server error or invalid credentials.');
      }
      onLoginSuccess(data.user, data.access_token);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle Registration Step 1 -> Triggers OTP Dispatch
  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setErrorCode('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, full_name: fullName })
      });
      const data = await parseJsonResponse(res);
      if (!res.ok) {
        setErrorCode(data.code || 'REGISTRATION_FAILED');
        throw new Error(data.error || data.detail || 'Server error or registration failed.');
      }
      
      setDebugOtp(data.debug_otp || '');
      setShowOtpModal(true);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle OTP Verification Step 2
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setErrorCode('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp_code: otpCode })
      });
      const data = await parseJsonResponse(res);
      if (!res.ok) {
        setErrorCode(data.code || 'INVALID_OTP');
        throw new Error(data.error || data.detail || 'Server error or invalid OTP code.');
      }
      
      setShowOtpModal(false);
      onLoginSuccess(data.user, data.access_token);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle Password Reset
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setErrorCode('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp_code: otpCode, new_password: password })
      });
      const data = await parseJsonResponse(res);
      if (!res.ok) {
        setErrorCode(data.code || 'RESET_FAILED');
        throw new Error(data.error || data.detail || 'Server error or password reset failed.');
      }
      alert('Password updated! You can now log in.');
      setMode('login');
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '440px', padding: '2.5rem' }}>
        
        {/* Header Branding */}
        <div style={{ textAlignment: 'center', marginBottom: '2rem', textAlign: 'center' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #0077b5, #6366f1)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            boxShadow: '0 8px 24px rgba(0, 119, 181, 0.4)'
          }}>
            <Shield size={28} color="#fff" />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>LinkedIn Agent</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Enterprise Local-First Security Core
          </p>
        </div>

        {errorMsg && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.15)',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            color: '#f43f5e',
            padding: '0.75rem 1rem',
            borderRadius: '10px',
            fontSize: '0.85rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.5rem'
          }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              {errorCode && <strong style={{ display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>[{errorCode}]</strong>}
              <span>{errorMsg}</span>
            </div>
          </div>
        )}

        {/* LOGIN FORM */}
        {mode === 'login' && (
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Username or Email
              </label>
              <div style={{ position: 'relative' }}>
                <User size={18} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <input 
                  type="text" 
                  required 
                  value={username} 
                  onChange={(e) => setUsername(e.target.value)} 
                  className="glass-input" 
                  style={{ paddingLeft: '38px' }}
                  placeholder="admin or user@domain.com" 
                />
              </div>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={18} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <input 
                  type="password" 
                  required 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  className="glass-input" 
                  style={{ paddingLeft: '38px' }}
                  placeholder="••••••••••••" 
                />
              </div>
            </div>

            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" /> Authenticating...
                </>
              ) : (
                <>
                  Sign In to Workspace <ArrowRight size={18} />
                </>
              )}
            </button>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginTop: '0.5rem' }}>
              <button type="button" onClick={() => { setMode('forgot'); setErrorMsg(''); }} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer' }}>
                Forgot password?
              </button>
              <button type="button" onClick={() => { setMode('register'); setErrorMsg(''); }} style={{ background: 'none', border: 'none', color: 'var(--accent-indigo)', cursor: 'pointer', fontWeight: 600 }}>
                Create Local Account
              </button>
            </div>
          </form>
        )}

        {/* REGISTER FORM */}
        {mode === 'register' && (
          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>Full Name</label>
              <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} className="glass-input" placeholder="Alex Mercer" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>Username</label>
              <input type="text" required value={username} onChange={(e) => setUsername(e.target.value)} className="glass-input" placeholder="alexm" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>Email Address</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="glass-input" placeholder="alex@enterprise.com" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>Password</label>
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="glass-input" placeholder="Min 8 chars (1 uppercase, 1 number, 1 special)" />
            </div>

            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" /> Dispatching OTP...
                </>
              ) : (
                <>
                  Register & Verify OTP <Sparkles size={18} />
                </>
              )}
            </button>

            <button type="button" onClick={() => { setMode('login'); setErrorMsg(''); }} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.82rem', marginTop: '0.5rem' }}>
              Already have an account? Sign In
            </button>
          </form>
        )}

        {/* FORGOT PASSWORD FORM */}
        {mode === 'forgot' && (
          <form onSubmit={handleResetPassword} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Enter your email and reset code sent to your account.</p>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>Email Address</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="glass-input" placeholder="alex@enterprise.com" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>OTP Code</label>
              <input type="text" required value={otpCode} onChange={(e) => setOtpCode(e.target.value)} className="glass-input" placeholder="6-digit code" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>New Password</label>
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="glass-input" placeholder="New strong password" />
            </div>

            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" /> Resetting Password...
                </>
              ) : (
                'Reset Password'
              )}
            </button>

            <button type="button" onClick={() => { setMode('login'); setErrorMsg(''); }} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.82rem' }}>
              Back to Login
            </button>
          </form>
        )}
      </div>

      {/* ENTERPRISE MOCK OTP MODAL */}
      {showOtpModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: '380px', padding: '2rem', textAlign: 'center' }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: 'rgba(16, 185, 129, 0.2)',
              border: '1px solid var(--accent-emerald)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem'
            }}>
              <KeyRound size={24} color="var(--accent-emerald)" />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff' }}>2FA Verification</h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0.5rem 0 1.25rem 0' }}>
              Enterprise OTP dispatched to <span style={{ color: 'var(--accent-cyan)' }}>{email}</span>
            </p>

            {debugOtp && (
              <div style={{
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px border var(--accent-indigo)',
                padding: '0.5rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontSize: '0.8rem',
                fontFamily: 'var(--font-mono)'
              }}>
                [MOCK OTP CODE]: <strong style={{ color: '#fff', letterSpacing: '2px' }}>{debugOtp}</strong>
              </div>
            )}

            <form onSubmit={handleVerifyOtp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <input 
                type="text" 
                maxLength={6} 
                required 
                value={otpCode} 
                onChange={(e) => setOtpCode(e.target.value)} 
                className="glass-input" 
                style={{ textAlign: 'center', fontSize: '1.4rem', letterSpacing: '6px', fontFamily: 'var(--font-mono)' }}
                placeholder="000000"
              />
              <button type="submit" className="btn-primary" style={{ justifyContent: 'center' }} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" /> Verifying...
                  </>
                ) : (
                  <>
                    Confirm OTP <CheckCircle2 size={18} />
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
