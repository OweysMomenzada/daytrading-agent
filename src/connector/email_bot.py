from datetime import datetime
from dotenv import load_dotenv
import os
import ssl

from email.message import EmailMessage
import smtplib

load_dotenv()

sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('GMAIL_APP_PASSWORD')
receiver_email = os.getenv('RECEIVER_EMAIL')

def send_email(body, ticker):
    """
    Send an email to the receiver.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        ticker (str): The ticker symbol of the trading proposal
    """
    body = """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    subject = f"A new Trading Proposal for {ticker}! - " + current_time

    em = EmailMessage()
    em["From"] = sender_email
    em["To"] = receiver_email
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    