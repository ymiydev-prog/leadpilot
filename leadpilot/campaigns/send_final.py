#!/usr/bin/env python3
import smtplib, json, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "ificahhweilgwfjb"

CLEAN_EMAILS = [
    ("hola@internetrepublica.com", "Equipo Internet República"),
    ("info@topmadrid.com.es", "Equipo TopMadrid"),
    ("info@iomarketing.es", "Equipo IOMarketing"),
    ("info@budamarketing.es", "Equipo Buda Marketing"),
    ("hola@ad-do.com", "Equipo ADDO"),
    ("hello@gmedia.es", "Equipo Gmedia"),
    ("info@optimoclick.com", "Equipo Optimoclick"),
    ("agencia@im.education", "Equipo Tresce"),
    ("agencia@kreaset.com", "Equipo Kreaset"),
    ("info@digency.es", "Equipo Digency"),
    ("hola@eyclick.com", "Equipo EYClick"),
    ("hello@n3xtwave.com", "Equipo N3XTwave"),
]

SUBJECT = "LeadPilot - Prueba gratis para agencias de marketing"

BODY = """Hola {name},

Espero que te encuentres bien. Te escribo porque he visto que tu agencia trabaja con empresas que buscan soluciones de marketing digital.

LeadPilot es una herramienta que permite encontrar empresas interesadas en tus servicios de forma rápida y con datos verificables. El primer mes es gratis, sin compromiso.

Si te interesa, puedes registrarte directamente en: https://leadpilot.es/dashboard

Si tienes cualquier pregunta, responde este correo y te contesto personalmente.

Un saludo,
Carlos
LeadPilot.es"""

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
        print(f"Enviado: {to_email}")
        return True
    except Exception as e:
        print(f"Error {to_email}: {e}")
        return False

if __name__ == "__main__":
    print("=== Envio final - 12 emails en espanol ===")
    results = []
    for i, (email, name) in enumerate(CLEAN_EMAILS):
        success = send(email, name)
        results.append({"email": email, "name": name, "status": "sent" if success else "failed"})
        if i < len(CLEAN_EMAILS) - 1:
            time.sleep(2)
    
    sent = sum(1 for r in results if r["status"] == "sent")
    print(f"\nResultado: {sent}/{len(results)} enviados")
    
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json") as f:
        log = json.load(f)
    log["final_batch"] = {"date": "2026-04-12", "results": results, "total_sent": sent}
    log["total_sent"] = sent
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print("Log guardado")