import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

import config


def send_email(body, to_email, from_email=config.EMAIL_ADRESS, password=config.EMAIL_PASS,
               subject='Your Verification Code', ):
    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add HTML body
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .container {{
                width: 80%;
                max-width: 600px;
                margin: auto;
                background: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #4CAF50;
            }}
            p {{
                font-size: 16px;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                color: #ffffff;
                background-color: #4CAF50;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Verification Code</h1>
            <p>Hello,</p>
            <p>Here is your verification code:</p>
            <p style="font-size: 24px; font-weight: bold; color: #4CAF50;">{body}</p>
            <p>If you did not request this, please ignore this email.</p>
            <p>Thank you!</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, 'html'))

    # Connect to the Gmail SMTP server and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)



# Example usage
from_email = config.EMAIL_ADRESS
password = config.EMAIL_PASS





def create_verify_code():
    code = int(''.join([str(random.randint(0, 9)) for _ in range(6)]))
    return code
