import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_report(name: str, recipient_email: str, company_name: str, pdf_path: str) -> bool:
    """
    Sends the generated PDF report to the prospect via email.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not all([sender_email, smtp_server, smtp_username, smtp_password]):
        print("Warning: Email configuration missing in .env. Skipping email sending.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Strategic Audit Report - {company_name}"
        
        body = f"""
        Hi {name},
        
        Thank you for submitting your details. 
        
        Our AI system has analyzed {company_name}'s digital presence and compiled a personalized strategic audit.
        
        Please find your report attached to this email. We look forward to discussing how we can help you implement these insights.
        
        Best regards,
        The SimplifIQ Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                msg.attach(attach)
        else:
            print(f"Error: PDF not found at {pdf_path}")
            return False
            
        # Connect to SMTP server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
