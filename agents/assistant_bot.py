#!/usr/bin/env python3
"""
ASSISTANT - Customer Service Bot for LeadPilot
Receives website contact form submissions and sends to Telegram,
then responds automatically via AI.
"""
import requests
import json
import time
from datetime import datetime

# Telegram Bot Configuration
BOT_TOKEN = "8278104837:AAF8Lo9Gm-qTaGMPYMQ1hr-9GHw51cU-qXs"
CHAT_ID = "1058105434"  # Jefe's Telegram ID

# InsForge Configuration  
INSFORGE_URL = "https://nv96hw8d.eu-central.insforge.app"
INSFORGE_KEY = "ik_35c9fe063dc416d6bb3a636dc44b067c"

def send_telegram(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp.json().get("ok", False)
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def save_lead_to_insforge(name, email, company, message):
    """Save lead to InsForge database"""
    url = f"{INSFORGE_URL}/api/database/records/leads"
    headers = {"Authorization": f"Bearer {INSFORGE_KEY}", "Content-Type": "application/json"}
    data = [{
        "name": name,
        "email": email,
        "company": company or "",
        "message": message,
        "source": "website_contact",
        "created_at": datetime.utcnow().isoformat()
    }]
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"InsForge error: {e}")
        return False

def generate_auto_response(name, message):
    """Generate automatic AI response based on message content"""
    msg_lower = message.lower()
    
    # Check for common questions
    if any(kw in msg_lower for kw in ["precio", "cuesta", "cuanto", "€", "euros", "coste"]):
        return f"""¡Hola {name}! 👋

Gracias por tu interés en LeadPilot.

<b>Planes y Precios:</b>
• <b>Free</b>: 10 leads/mes (gratis)
• <b>Starter</b>: €29/mes (100 leads)
• <b>Pro</b>: €79/mes (500 leads)
• <b>Business</b>: €149/mes (ilimitado)

El primer mes es completamente gratis. ¿Te gustaría empezar? 🚀"""

    elif any(kw in msg_lower for kw in ["funciona", "como", "que es", "explic", "demo"]):
        return f"""¡Hola {name}! 👋

LeadPilot es un generator de leads B2B que:
1. Busca empresas en España según tu nicho
2. Extrae datos de contacto reales (emails, teléfonos)
3. Los organiza en un dashboard fácil de usar

<b>Prueba gratis sin tarjeta:</b> https://leadpilot.es/dashboard

¿Tienes alguna duda específica?"""

    elif any(kw in msg_lower for kw in ["gratis", "free", "trial", "prueba"]):
        return f"""¡Hola {name}! 👋

¡Sí! El plan <b>Free</b> es 100% gratis:
• 10 leads/mes
• Datos verificables
• Dashboard incluido
• Sin límite de tiempo

<b>Regístrate aquí:</b> https://leadpilot.es/dashboard#register

¿En qué te puedo ayudar?"""

    elif any(kw in msg_lower for kw in ["datos", "real", "verific", "calidad"]):
        return f"""¡Hola {name}! 👋

Sí, todos nuestros datos son <b>100% reales y verificables</b>:
• Emails verificados antes de entregar
• Teléfonos de empresas reales
• Datos de empresas españolas activas
• Actualización constante

<b>Prueba gratis:</b> https://leadpilot.es/dashboard#register

¿Hay algo más que quieras saber?"""

    elif any(kw in msg_lower for kw in ["contacto", "hablar", "llamada", "demo", " reunion"]):
        return f"""¡Hola {name}! 👋

¡Por supuesto! Podemos agendar una demo personalizada.

<b>Cuéntame:</b>
1. ¿Cuál es tu empresa?
2. ¿Qué tipo de leads buscas?
3. ¿Cuál es tu presupuesto?

Mientras tanto, te recomiendo empezar con el <b>plan Free</b> para ver cómo funciona: https://leadpilot.es/dashboard#register

Te escribo pronto para coordinar una llamada. 📞"""

    else:
        return f"""¡Hola {name}! 👋

Gracias por contactar con LeadPilot.

He recibido tu mensaje y un miembro de nuestro equipo te responderá en breve.

<b>Resumen de tu consulta:</b>
{message[:200]}

¿Necesitas algo más? Mientras tanto, puedes probar LeadPilot gratis aquí: https://leadpilot.es/dashboard#register

¡Un saludo! 🚀"""

def process_contact_form(data):
    """Process incoming contact form submission"""
    name = data.get("name", "Usuario")
    email = data.get("email", "")
    company = data.get("company", "")
    message = data.get("message", "")
    source = data.get("source", "contact_form")
    
    # Compose Telegram message
    telegram_msg = f"""🔔 <b>Nuevo Lead de LeadPilot</b>

👤 <b>Nombre:</b> {name}
📧 <b>Email:</b> {email}
🏢 <b>Empresa:</b> {company or 'No especificada'}
💬 <b>Mensaje:</b>
{message[:500]}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
    
    # Send to Telegram
    sent = send_telegram(telegram_msg)
    
    # Save to InsForge
    saved = save_lead_to_insforge(name, email, company, message)
    
    # Generate auto response
    auto_response = generate_auto_response(name, message)
    
    # Send auto response to user via email (if they provided email)
    if email:
        send_auto_reply_email(email, name, auto_response)
    
    return {
        "success": True,
        "telegram_sent": sent,
        "lead_saved": saved,
        "auto_response": auto_response
    }

def send_auto_reply_email(to_email, name, html_body):
    """Send auto-reply email to the lead"""
    import smtplib
    from email.mime.text import MIMEText
    
    SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
    SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "ificahhweilgwfjb"
    
    msg = MIMEText(html_body, "html")
    msg["From"] = "LeadPilot <contacto@leadpilot.es>"
    msg["To"] = to_email
    msg["Subject"] = "Re: Gracias por contactar con LeadPilot"
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

if __name__ == "__main__":
    # Test the bot
    test_data = {
        "name": "Test Lead",
        "email": "test@example.com",
        "company": "Test Company",
        "message": "¿Cuánto cuesta LeadPilot?"
    }
    result = process_contact_form(test_data)
    print(json.dumps(result, indent=2))