#!/usr/bin/env python3
"""Send batch 3 - 6 verified emails"""
import smtplib, json, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "ificahhweilgwfjb"

BATCH3 = [
    {"email": "info@optimoclick.com", "name": "Equipo Optimoclick", "domain": "optimoclick.com"},
    {"email": "agencia@im.education", "name": "Equipo Tresce", "domain": "tresce.com"},
    {"email": "agencia@kreaset.com", "name": "Equipo Kreaset", "domain": "kreaset.com"},
    {"email": "info@digency.es", "name": "Equipo Digency", "domain": "digency.es"},
    {"email": "hola@eyclick.com", "name": "Equipo EYClick", "domain": "eyclick.com"},
    {"email": "hello@n3xtwave.com", "name": "Equipo N3XTwave", "domain": "n3xtwave.com"},
]

SUBJECT = "LeadPilot - Herramienta para generar leads cualificados"
BODY = """Hola {name},

Te escribo porque sé que tu agencia trabaja con empresas que necesitan leads de calidad.

LeadPilot es una herramienta que te ayuda a encontrar empresas interesadas en tus servicios en minutos. Búsqueda real, datos verificables.

Primer mes gratis. Sin compromiso.

¿Hablamos 15 minutos esta semana?

Saludos,
Carlos
LeadPilot.es
https://leadpilot.es"""

def send(to_email, to_name):
    try:
        msg = MIMEMultipart()
        msg["From"] = "LeadPilot <contacto@leadpilot.es>"
        msg["To"] = to_email
        msg["Subject"] = SUBJECT
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
    print("=== Batch 3: 6 emails ===\n")
    results = []
    for i, p in enumerate(BATCH3):
        success = send(p["email"], p["name"])
        results.append({"email": p["email"], "status": "sent" if success else "failed"})
        if i < len(BATCH3) - 1:
            time.sleep(2)
    
    sent = sum(1 for r in results if r["status"] == "sent")
    print(f"\n=== {sent}/{len(results)} sent ===")
    
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json") as f:
        log = json.load(f)
    log["batch3"] = {"date": "2026-04-12", "results": results, "total": sent}
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump(log, f, indent=2)
    
    total = log.get("total_sent", 0)
    log["total_sent"] = total + sent
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump(log, f, indent=2)