import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

# Configure your email server
SMTP_SERVER = ""
SMTP_PORT =  587 # For TLS
SMTP_USERNAME = ""
SMTP_PASSWORD = ""


def send_email(recipient_email: str, reset_token: str):
    subject = "Password Reset Request"
    body = f"To reset your password, please click on the following link:\n\n" \
           f"http://yourdomain.com/reset_password?token={reset_token}\n\n" \
           f"If you did not request this, please ignore this email."

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email: Authentication error")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email")
