#!/usr/bin/env python3
"""Send HTML emails to prospects - Batch 4 with beautiful template"""
import smtplib, json, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "ificahhweilgwfjb"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f4f4f9">
    <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:30px;text-align:center">
            <h1 style="color:#fff;margin:0;font-size:28px;font-weight:700">🚀 LeadPilot</h1>
            <p style="color:rgba(255,255,255,0.9);margin:10px 0 0;font-size:16px">Genera leads cualificados en minutos</p>
        </div>
        
        <div style="padding:30px">
            <h2 style="color:#1f2937;margin:0 0 20px;font-size:22px">Hola {name},</h2>
            
            <p style="color:#4b5563;line-height:1.8;font-size:16px;margin:0 0 20px">
                {message}
            </p>
            
            <div style="background:#f9fafb;border-radius:8px;padding:20px;margin:20px 0">
                <h3 style="color:#6366f1;margin:0 0 15px;font-size:18px">✨ ¿Qué incluye el trial gratis?</h3>
                <ul style="color:#374151;font-size:15px;margin:0;padding-left:20px">
                    <li style="margin-bottom:8px">✓ Búsqueda de empresas reales en España</li>
                    <li style="margin-bottom:8px">✓ Datos verificables (email, teléfono, ubicación)</li>
                    <li style="margin-bottom:8px">✓ Dashboard para gestionar tu pipeline</li>
                    <li style="margin-bottom:8px">✓ Hasta 100 leads gratis el primer mes</li>
                </ul>
            </div>
            
            <div style="text-align:center;margin:30px 0">
                <a href="https://leadpilot.es" style="display:inline-block;background:#6366f1;color:#fff;padding:16px 32px;text-decoration:none;border-radius:8px;font-weight:600;font-size:16px">
                    🚀 Probar Gratis Ahora
                </a>
            </div>
            
            <p style="color:#6b7280;font-size:13px;text-align:center;margin:20px 0 0">
                Sin compromiso. Sin tarjeta de crédito. Solo resultados.
            </p>
        </div>
        
        <div style="background:#1f2937;padding:20px;text-align:center">
            <p style="color:#fff;font-size:14px;margin:0">
                <strong>LeadPilot.es</strong> - Tu herramienta de prospección B2B
            </p>
            <p style="color:#9ca3af;font-size:12px;margin:10px 0 0">
                ¿Preguntas? Responde este email y te ayudamos.
            </p>
        </div>
    </div>
</body>
</html>
"""

# Messages variation
MESSAGES = [
    "Vi que tu agencia trabaja con empresas que buscan soluciones de marketing digital. LeadPilot te ayuda a encontrar这些 empresas interesadas en minutos, no horas.",
    "El desafío de conseguir leads качественые consume tiempo valioso de tu equipo. Con LeadPilot, puedes identificar empresas реальные interessadas en tus servicios sin perder horas en investigación.",
    "Si tu agencia pasa tiempo buscando prospectos en lugar de cerrar deals, necesitas ver esto. LeadPilot automatiza la prospección para que te enfoques en lo importante: vender."
]

BATCH4 = [
    {"email": "info@sortlist.es", "name": "Equipo Sortlist"},
    {"email": "info@expiey.com", "name": "Equipo Expiey"},
    {"email": "info@openinnova.es", "name": "Equipo OpenInnova"},
    {"email": "info@comodoromarketing.es", "name": "Equipo Comodoro"},
]

def send_html(to_email, to_name, message):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = "LeadPilot <contacto@leadpilot.es>"
        msg["To"] = to_email
        msg["Subject"] = "LeadPilot - Trial gratis para agencias"
        
        html_content = HTML_TEMPLATE.replace("{name}", to_name).replace("{message}", message)
        msg.attach(MIMEText(html_content, "html"))
        
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
    print("=== HTML Emails Batch 4 ===\n")
    results = []
    for i, p in enumerate(BATCH4):
        msg_idx = i % len(MESSAGES)
        success = send_html(p["email"], p["name"], MESSAGES[msg_idx])
        results.append({"email": p["email"], "status": "sent" if success else "failed"})
        time.sleep(2)
    
    sent = sum(1 for r in results if r["status"] == "sent")
    print(f"\n=== {sent}/{len(results)} sent with HTML ===")
    
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json") as f:
        log = json.load(f)
    log["batch4_html"] = {"date": "2026-04-12", "results": results, "total": sent}
    log["total_sent"] = log.get("total_sent", 0) + sent
    with open("/root/.openclaw/workspace/leadpilot/campaigns/send_log.json", "w") as f:
        json.dump(log, f, indent=2)