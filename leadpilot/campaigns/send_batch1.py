#!/usr/bin/env python3
"""Send batch 1 - 10 more emails to prospects"""
import smtplib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "ificahhweilgwfjb"

BATCH = [
    {"email": "info@topmadrid.com.es", "name": "Equipo TopMadrid", "domain": "topmadrid.com.es"},
    {"email": "info@iomarketing.es", "name": "Equipo IOMarketing", "domain": "iomarketing.es"},
    {"email": "info@budamarketing.es", "name": "Equipo Buda Marketing", "domain": "budamarketing.es"},
    {"email": "info@ad-do.com", "name": "Equipo ADDO", "domain": "ad-do.com"},
    {"email": "info@gmedia.es", "name": "Equipo Gmedia", "domain": "gmedia.es"},
    {"email": "info@bcm.marketing", "name": "Equipo BCM", "domain": "bcm.marketing"},
    {"email": "info@advertis.es", "name": "Equipo Advertis", "domain": "advertis.es"},
    {"email": "info@comodoromarketing.es", "name": "Equipo Comodoro", "domain": "comodoromarketing.es"},
    {"email": "info@openinnova.es", "name": "Equipo OpenInnova", "domain": "openinnova.es"},
    {"email": "info@aliciazunzunegui.com", "name": "Equipo Alicia Zunzunegui", "domain": "aliciazunzunegui.com"},
]

SUBJECT = "Breve - LeadPilot para agencias como {domain}"
BODY = """Hola {name},

Hope you're doing well!

We built LeadPilot to help agencies save time prospecting new clients. Real leads, real data, no fluff.

Free trial, no credit card. If you're curious, happy to show you how it works in 15 minutes.

Best,
Carlos
LeadPilot.es"""

def send(to_email, to_name, domain):
    try:
        msg = MIMEMultipart()
        msg["From"] = "LeadPilot <contacto@leadpilot.es>"
        msg["To"] = to_email
        msg["Subject"] = SUBJECT.format(domain=domain)
        msg.attach(MIMEText(BODY.format(name=to_name), "plain"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"✓ {to_email}")
        return True
    except Exception as e:
        print(f"✗ {to_email}: {e}")
        return False

if __name__ == "__main__":
    print("=== Batch 1: 10 emails ===")
    results = []
    for i, p in enumerate(BATCH):
        success = send(p["email"], p["name"], p["domain"])
        results.append({"email": p["email"], "status": "sent" if success else "failed"})
        if i < len(BATCH) - 1:
            time.sleep(1.5)
    
    sent = sum(1 for r in results if r["status"] == "sent")
    print(f"\n=== {sent}/{len(results)} sent ===")
    
    # Update prospects status
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json") as f:
        log = json.load(f)
    log["batch1"] = results
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump(log, f, indent=2)