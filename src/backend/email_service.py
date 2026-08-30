import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any

def send_otp_email(to_email: str, otp_code: str) -> Dict[str, Any]:
    """
    Sends a 6-digit OTP verification email via SMTP.
    Falls back gracefully to dev-mode console logging if SMTP credentials are missing or unreachable.
    """
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_password = os.environ.get("SMTP_PASSWORD", "").strip()
    from_email = os.environ.get("SMTP_FROM_EMAIL", "noreply@linkedinagent.com").strip()

    subject = "LinkedIn Autonomous Agent - Verification Code"
    
    # HTML and Plain Text Templates
    text_content = (
        f"LinkedIn Autonomous Agent Verification Code\n\n"
        f"Your 6-digit verification code is: {otp_code}\n\n"
        f"This code will expire in 5 minutes. If you did not request this code, please ignore this email."
    )
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 20px; }}
        .card {{ max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e1e4e8; }}
        .header {{ font-size: 20px; font-weight: 700; color: #0a66c2; text-align: center; margin-bottom: 20px; }}
        .otp-box {{ font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #111827; background: #f0f7ff; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; border: 1px dashed #0a66c2; }}
        .footer {{ font-size: 12px; color: #6b7280; text-align: center; margin-top: 25px; line-height: 1.5; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">LinkedIn Autonomous Agent</div>
        <p style="color: #374151; font-size: 15px;">Use the verification code below to complete your authentication:</p>
        <div class="otp-box">{otp_code}</div>
        <p style="color: #4b5563; font-size: 14px;">This code will expire in <strong>5 minutes</strong>.</p>
        <div class="footer">If you did not request this verification code, please secure your account credentials immediately.</div>
      </div>
    </body>
    </html>
    """

    # If SMTP credentials are missing, run safe dev-mode fallback
    if not smtp_host or not smtp_user or not smtp_password:
        print(f"[ENTERPRISE SMTP DEV-MODE] Outbound OTP for {to_email}: {otp_code}")
        return {
            "status": "dev_mode",
            "message": "SMTP not configured. OTP printed to dev logs.",
            "to_email": to_email,
            "otp_code": otp_code
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())

        return {
            "status": "delivered",
            "message": f"Verification email dispatched successfully to {to_email}.",
            "to_email": to_email
        }
    except Exception as err:
        print(f"[SMTP DISPATCH ERROR] Failed to send email to {to_email}: {err}")
        return {
            "status": "error",
            "message": f"SMTP dispatch failed: {str(err)}",
            "to_email": to_email,
            "otp_code": otp_code
        }
