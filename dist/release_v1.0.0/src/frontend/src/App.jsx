import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import AuthPage from './pages/AuthPage';

import ProfilePage from './pages/ProfilePage';
import ResumeDropzonePage from './pages/ResumeDropzonePage';
import ResumeBuilderPage from './pages/ResumeBuilderPage';
import AITailorPage from './pages/AITailorPage';
import AutoPilotPage from './pages/AutoPilotPage';
import LiveTrackerPage from './pages/LiveTrackerPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [activeTab, setActiveTab] = useState('auto-pilot');

  const handleLoginSuccess = (userData, accessToken) => {
    setUser(userData);
    setToken(accessToken);
  };

  const handleLogout = () => {
    setUser(null);
    setToken(null);
  };

  // Render Auth view if not logged in
  if (!user) {
    return <AuthPage onLoginSuccess={handleLoginSuccess} />;
  }

  // Titles mapping
  const titles = {
    'profile': 'Career Profile & Preferences',
    'dropzone': 'Master Resume Dropzone',
    'builder': 'Manual Resume Builder',
    'ai-tailor': 'AI Resume Tailor & Cover Letter Engine',
    'auto-pilot': 'Playwright Auto-Pilot Autonomous Agent',
    'live-tracker': 'Live Job Application Analytics',
    'settings': 'System & Stealth Settings'
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Left Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        user={user}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, marginLeft: '280px', display: 'flex', flexDirection: 'column' }}>
        <Header title={titles[activeTab] || 'Dashboard'} />
        
        <main style={{ padding: '2rem', flex: 1 }}>
          {activeTab === 'profile' && <ProfilePage user={user} />}
          {activeTab === 'dropzone' && <ResumeDropzonePage />}
          {activeTab === 'builder' && <ResumeBuilderPage />}
          {activeTab === 'ai-tailor' && <AITailorPage />}
          {activeTab === 'auto-pilot' && <AutoPilotPage />}
          {activeTab === 'live-tracker' && <LiveTrackerPage />}
          {activeTab === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
}
