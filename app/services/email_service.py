import smtplib
from email.mime.text import MIMEText
from flask import current_app


def send_email(to_email, subject, body):
    """Send email using SMTP with app configuration"""
    smtp_server = current_app.config["MAIL_SERVER"]
    smtp_port = current_app.config["MAIL_PORT"]
    username = current_app.config["MAIL_USERNAME"]
    password = current_app.config["MAIL_PASSWORD"]
    sender = current_app.config["MAIL_DEFAULT_SENDER"]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
    server.starttls()
    server.login(username, password)
    server.sendmail(sender, [to_email], msg.as_string())
    server.quit()
