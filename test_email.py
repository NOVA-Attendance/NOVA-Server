#!/usr/bin/env python3
"""
Test Email Configuration
This script tests if your email setup is working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'

print("=" * 60)
print("📧 NOVA Email Configuration Test")
print("=" * 60)
print()

# Check configuration
print("Checking configuration...")
print(f"  EMAIL_ENABLED: {EMAIL_ENABLED}")
print(f"  EMAIL_SMTP_SERVER: {EMAIL_SMTP_SERVER}")
print(f"  EMAIL_SMTP_PORT: {EMAIL_SMTP_PORT}")
print(f"  EMAIL_SENDER: {EMAIL_SENDER if EMAIL_SENDER else '❌ NOT SET'}")
print(f"  EMAIL_PASSWORD: {'✅ SET' if EMAIL_PASSWORD else '❌ NOT SET'}")
print(f"  EMAIL_USE_TLS: {EMAIL_USE_TLS}")
print()

if not EMAIL_ENABLED:
    print("❌ Email is DISABLED")
    print("   Set EMAIL_ENABLED=true in .env file")
    sys.exit(1)

if not EMAIL_SENDER or not EMAIL_PASSWORD:
    print("❌ Email credentials not configured")
    print("   Set EMAIL_SENDER and EMAIL_PASSWORD in .env file")
    print("   Run 'python3 setup_email.py' for help")
    sys.exit(1)

# Test email sending
print("Testing email connection...")
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Create test message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_SENDER  # Send to self for testing
    msg['Subject'] = 'NOVA - Email Test'
    
    body = "This is a test email from NOVA. If you receive this, your email configuration is working!"
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect and send
    server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
    if EMAIL_USE_TLS:
        server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print("✅ SUCCESS! Email test sent successfully!")
    print(f"   Check your inbox at {EMAIL_SENDER}")
    print("   If you received the test email, 2-step verification will work!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Authentication failed: {str(e)}")
    print("   Check your EMAIL_SENDER and EMAIL_PASSWORD")
    print("   For Gmail: Make sure you're using an App Password")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("   Check your SMTP settings and network connection")
    sys.exit(1)
