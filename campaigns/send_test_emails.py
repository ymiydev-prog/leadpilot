#!/usr/bin/env python3
"""Send test email campaign - 5 emails to validate everything works"""
import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "yhasvenezuela@gmail.com"
SMTP_PASS = "ificahhweilgwfjb"

TEST_EMAILS = [
    {"email": "info@estrategikadigital.com", "name": "Equipo Estrategika", "domain": "estrategikadigital.com"},
    {"email": "info@dinamiq.com", "name": "Equipo Dinamiq", "domain": "dinamiq.com"},
    {"email": "info@mkparadise.com", "name": "Equipo MKParadise", "domain": "mkparadise.com"},
    {"email": "info@internetrepublica.com", "name": "Equipo Internet República", "domain": "internetrepublica.com"},
    {"email": "info@talentumdigital.com", "name": "Equipo Talentum", "domain": "talentumdigital.com"},
]

EMAIL_BODY = """
Hola {name},

Hope you're doing well!

I'm reaching out because we built LeadPilot - a tool that helps agencies find qualified leads in minutes instead of spending hours prospecting.

We help companies like yours save time and get more clients. Free trial, no credit card needed.

Would you be open to a 15-minute demo this week?

Best,
Carlos
LeadPilot.es
"""

def send_email(to_email, to_name, subject):
    try:
        msg = MIMEMultipart()
        msg["From"] = "LeadPilot <contacto@leadpilot.es>"
        msg["To"] = to_email
        msg["Subject"] = subject
        body = EMAIL_BODY.format(name=to_name)
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"✓ Sent to {to_email}")
        return True
    except Exception as e:
        print(f"✗ Failed to {to_email}: {e}")
        return False

if __name__ == "__main__":
    print("=== LeadPilot Test Email Campaign ===")
    print(f"Sending {len(TEST_EMAILS)} test emails...\n")
    
    results = []
    for i, prospect in enumerate(TEST_EMAILS):
        subject = f"Breve - LeadPilot para {prospect['domain']}"
        success = send_email(prospect["email"], prospect["name"], subject)
        results.append({"email": prospect["email"], "status": "sent" if success else "failed"})
        if i < len(TEST_EMAILS) - 1:
            time.sleep(2)  # Delay between emails
    
    print(f"\n=== Results: {sum(1 for r in results if r['status']=='sent')}/{len(results)} sent ===")
    
    # Save results
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump({"date": "2026-04-12", "results": results}, f, indent=2)
    
    print("Log saved to campaigns/send_log.json")