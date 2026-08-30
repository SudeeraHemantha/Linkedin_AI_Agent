import pytest
from unittest.mock import patch
from src.installer.tray_app import LinkedInAgentTrayApp

def test_tray_app_initialization():
    """Verify system tray application default initialization parameters."""
    app = LinkedInAgentTrayApp("http://localhost:3000")
    assert app.dashboard_url == "http://localhost:3000"
    assert app.worker_active is True
    assert app.is_running is False

def test_tray_app_status_toggle():
    """Verify worker status text generation and state toggling."""
    app = LinkedInAgentTrayApp()
    assert "ACTIVE" in app.get_worker_status_text()

    app.toggle_autonomous_runner()
    assert app.worker_active is False
    assert "IDLE" in app.get_worker_status_text()

    app.toggle_autonomous_runner()
    assert app.worker_active is True
    assert "ACTIVE" in app.get_worker_status_text()

def test_tray_app_open_dashboard():
    """Verify open_dashboard triggers webbrowser.open to dashboard URL."""
    app = LinkedInAgentTrayApp("http://localhost:3000")
    with patch("webbrowser.open") as mock_open:
        app.open_dashboard()
        mock_open.assert_called_once_with("http://localhost:3000")

def test_tray_app_quit_application():
    """Verify quit_application safely terminates application states."""
    app = LinkedInAgentTrayApp()
    app.is_running = True
    app.quit_application()
    assert app.is_running is False
    assert app.worker_active is False
