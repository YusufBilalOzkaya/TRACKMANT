import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load .env file from root directory if it exists
load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

def send_email_notification(to_email: str, subject: str, body: str):
    """
    Sends a simple HTML email notification.
    """
    if not SMTP_USER or not SMTP_PASS:
        print(f"Skipping email to {to_email}: SMTP credentials not configured.")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"TRACKMANT <{SMTP_USER}>"
    msg['To'] = to_email
    msg['Subject'] = f"🔔 TRACKMANT: {subject}"

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def generate_alert_body(tracker_name, url, old_value, new_value):
    return f"""
    <div style="font-family: sans-serif; padding: 20px; border: 1px solid #6366f1; border-radius: 10px;">
        <h2 style="color: #6366f1;">TRACKMANT Found a Signal!</h2>
        <p>The condition you were waiting for has occurred for <b>{tracker_name}</b>.</p>
        <hr>
        <p><b>Old Value:</b> {old_value}</p>
        <p><b>New Value:</b> <span style="color: #22c55e; font-weight: bold;">{new_value}</span></p>
        <br>
        <a href="{url}" style="background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Product</a>
    </div>
    """
