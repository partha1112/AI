from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

html_template = ""

with open("resources/security_alert_content.html", "r", encoding="utf-8") as file:
    html_template = file.read()

html_content = html_template.replace("{{timestamp}}", "2026-04-12 10:30 AM") \
                           .replace("{{ip_address}}", "192.168.1.1") \
                           .replace("{{location}}", "Chennai, India") \
                           .replace("{{action_link}}", "https://yourapp.com/security")


def send_security_alert_email(log_messages: list):
    message = Mail(
    from_email='[FROM_EMAIL_ADDRESS]',
    to_emails='[TO_EMAIL_ADDRESS]',
    subject='SECURITY ALERT',
    html_content= html_content
    )
    # sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))

    print("SENT SECURITY ALERT MAIL")
    
