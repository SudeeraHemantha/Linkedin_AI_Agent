import os
import pytest
from unittest.mock import patch, MagicMock
from src.backend.email_service import send_otp_email

def test_send_otp_email_dev_mode_fallback():
    """Verify dev-mode fallback when SMTP credentials are not configured."""
    if "SMTP_HOST" in os.environ:
        del os.environ["SMTP_HOST"]
        
    result = send_otp_email("user@example.com", "123456")
    assert result["status"] == "dev_mode"
    assert result["otp_code"] == "123456"
    assert "dev logs" in result["message"]

def test_send_otp_email_smtp_live_dispatch():
    """Verify live SMTP email construction and dispatch when credentials are set."""
    os.environ["SMTP_HOST"] = "smtp.mailtrap.io"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_USER"] = "testuser"
    os.environ["SMTP_PASSWORD"] = "testpass"

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        result = send_otp_email("candidate@enterprise.com", "889900")

        assert result["status"] == "delivered"
        assert result["to_email"] == "candidate@enterprise.com"
        
        # Verify server calls
        mock_smtp_cls.assert_called_once_with("smtp.mailtrap.io", 587, timeout=10)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("testuser", "testpass")
        mock_server.sendmail.assert_called_once()

        # Check sendmail arguments
        args, kwargs = mock_server.sendmail.call_args
        from_addr, to_addrs, msg_str = args
        assert "candidate@enterprise.com" in to_addrs
        assert "889900" in msg_str
        assert "LinkedIn Autonomous Agent" in msg_str

    # Clean up environment variables
    for var in ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"]:
        if var in os.environ:
            del os.environ[var]
