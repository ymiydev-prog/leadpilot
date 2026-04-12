#!/usr/bin/env python3
"""Send to VERIFIED emails only"""
import smtplib, json, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "ificahhweilgwfjb"

VERIFIED = [
    {"email": "hola@estrategikadigital.com", "name": "Equipo Estrategika", "domain": "estrategikadigital.com"},
    {"email": "hola@internetrepublica.com", "name": "Internet República", "domain": "internetrepublica.com"},
    {"email": "info@topmadrid.com.es", "name": "Equipo TopMadrid", "domain": "topmadrid.com.es"},
    {"email": "info@iomarketing.es", "name": "Equipo IOMarketing", "domain": "iomarketing.es"},
    {"email": "info@budamarketing.es", "name": "Equipo Buda", "domain": "budamarketing.es"},
    {"email": "hola@ad-do.com", "name": "Equipo ADDO", "domain": "ad-do.com"},
    {"email": "hello@gmedia.es", "name": "Equipo Gmedia", "domain": "gmedia.es"},
]

SUBJECT = "LeadPilot - Herramienta para generar leads cualificados"
BODY = """Hola {name},

Te escribo porque видим que tu agencia trabaja con clientes que necesitan leads cualificados.

LeadPilot es una herramienta que te ayuda a encontrar empresas interesadas en tus servicios en minutos, no horas. Búsqueda real, datos verificables.

Primer mes gratis. Sin compromiso.

¿Hablamos 15 minutos esta semana?

Saludos,
Carlos
LeadPilot.es

P.D. Si no es el momento, simplemente ignore. Pero si necesita leads de calidad, creo que podemos ayudar."""

def send(to_email, to_name, domain):
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
    print("=== Verified Emails Campaign ===\n")
    results = []
    for i, p in enumerate(VERIFIED):
        success = send(p["email"], p["name"], p["domain"])
        results.append({"email": p["email"], "name": p["name"], "status": "sent" if success else "failed"})
        if i < len(VERIFIED) - 1:
            time.sleep(2)
    
    sent = sum(1 for r in results if r["status"] == "sent")
    print(f"\n=== {sent}/{len(results)} sent to VERIFIED emails ===")
    
    # Update log
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json") as f:
        log = json.load(f)
    log["verified_campaign"] = {"date": "2026-04-12", "results": results}
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump(log, f, indent=2)