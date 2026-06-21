import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["Subject"] = "Test Email"
msg["From"] = "your_email@example.com"
msg["To"] = "recipient@example.com"
msg.set_content("Hello from Python!")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login("your_email@example.com", "app_password")
    smtp.send_message(msg)

print("Email sent!")
