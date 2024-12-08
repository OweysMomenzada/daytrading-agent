from datetime import datetime
from dotenv import load_dotenv
import os
import ssl
from email.message import EmailMessage
import smtplib
import markdown

load_dotenv()

sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('GMAIL_APP_PASSWORD')
receiver_email = os.getenv('RECIPIENT_EMAIL')

def send_email(body, ticker, proposal):
    """
    Send an email with trading proposal.
    
    Args:
        body (str): The email body content in markdown
        ticker (str): The ticker symbol of the trading proposal
        proposal (str): The trading proposal (either buy or sell)
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
        subject = f"[TradingAgent] New {proposal}ing Proposal for {ticker}! - {current_time}"

        # Convert markdown body to HTML
        html_body = markdown.markdown(body)

        # Create email message
        em = EmailMessage()
        em["From"] = sender_email
        em["To"] = receiver_email
        em["Subject"] = subject
        em.set_content(body)  # Plain text fallback
        em.add_alternative(html_body, subtype='html')  # HTML content

        # Create SSL context and send
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(em)
            print(f"Email sent successfully for {ticker}")
            return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
    
if __name__ == "__main__":
    markdown_content = """
    # Trading Proposal

    **Hello**, 

    This is a test email to propose a **buy** for **AAPL**.

    - Ticker: AAPL
    - Action: Buy
    - Time: Now!

    Thanks,
    Trading Bot
    """
    send_email(markdown_content, "AAPL", "buy")