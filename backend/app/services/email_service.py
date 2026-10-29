import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, otp: str, user_name: str = "Citizen") -> bool:
    """
    Sends a password reset email with the OTP to the user.
    Returns False if SMTP credentials are not configured or delivery fails.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(
            f"[EMAIL SERVICE] SMTP not configured. Unable to send reset email to {to_email}. "
            f"To send real emails, set SMTP_USER and SMTP_PASSWORD in backend/.env"
        )
        return False

    sender_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    sender_name = settings.SMTP_FROM_NAME or "SmartGov AI"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your SmartGov AI Password Reset OTP: {otp}"
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = to_email

    text_body = f"""Hello {user_name},

We received a request to reset your password for your SmartGov AI account.

Your 6-digit verification OTP code is: {otp}

This code is valid for 10 minutes. Please do not share this code with anyone.

If you did not request this password reset, please ignore this email.

Best regards,
SmartGov AI Team
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
    .header {{ background: linear-gradient(135deg, #102a43, #243b53); color: #ffffff; padding: 24px 30px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
    .content {{ padding: 30px; color: #334e68; line-height: 1.6; font-size: 15px; }}
    .otp-box {{ background: #f0f4f8; border: 2px dashed #627d98; border-radius: 8px; padding: 18px; text-align: center; margin: 24px 0; }}
    .otp-code {{ font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #102a43; font-family: monospace; }}
    .notice {{ font-size: 13px; color: #829ab1; margin-top: 10px; }}
    .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px; text-align: center; font-size: 12px; color: #9fb3c8; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🏛️ SmartGov AI</h1>
    </div>
    <div class="content">
      <p>Hello <strong>{user_name}</strong>,</p>
      <p>We received a request to reset the password for your SmartGov AI account. Use the verification code below to complete the reset process:</p>
      
      <div class="otp-box">
        <div class="otp-code">{otp}</div>
        <div class="notice">Valid for 10 minutes</div>
      </div>
      
      <p>Enter this code on the password reset page along with your new password.</p>
      <p>If you did not make this request, you can safely ignore this email. Your account remains secure.</p>
      
      <p style="margin-top: 24px;">Warm regards,<br><strong>SmartGov AI Team</strong></p>
    </div>
    <div class="footer">
      This is an automated system email from SmartGov AI. Please do not reply directly.
    </div>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        if settings.SMTP_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        logger.info(f"[EMAIL SERVICE] Successfully sent reset email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL SERVICE] Failed to send email to {to_email}: {e}")
        return False
