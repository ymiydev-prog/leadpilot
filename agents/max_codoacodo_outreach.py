#!/usr/bin/env python3
"""
MAX - Outreach para Codo a Codo
Emails a asociaciones de vecinos y ayuntamientos
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from max_email_template import generate_subject_line

# SMTP Config
SENDER = "yhasvenezuela@gmail.com"
APP_PASSWORD = "isrwrzraxlkwrclo"

# Targets reales de Madrid (ejemplo - ajustar según ciudad real)
targets = [
    {
        "name": "Asociación de Vecinos Chamberí",
        "type": "asociacion",
        "email": "info@avchamberi.org",
        "location": "Chamberí, Madrid",
        "custom_intro": "Vi que la Asociación de Vecinos de Chamberí trabaja activamente por la cohesión comunitaria del barrio."
    },
    {
        "name": "Federación Regional de Asociaciones de Vecinos",
        "type": "federacion",
        "email": "contacto@fravmadrid.org",
        "location": "Madrid",
        "custom_intro": "Como federación que representa a centaines de asociaciones vecinales, siempre buscan herramientas innovadoras."
    },
    {
        "name": "Concejalía de Participación Ciudadana",
        "type": "ayuntamiento",
        "email": "participacion@madrid.es",
        "location": "Ayuntamiento de Madrid",
        "custom_intro": "El Ayuntamiento de Madrid impulsa programas de economía colaborativa y cohesión social."
    },
    {
        "name": "Centro Comunitario Retiro",
        "type": "centro",
        "email": "centro.retiro@madrid.es",
        "location": "Retiro, Madrid",
        "custom_intro": "El Centro Comunitario de Retiro organiza actividades para fortalecer el tejido social del barrio."
    },
    {
        "name": "Asociación Vecinos Salamanca",
        "type": "asociacion",
        "email": "info@avsalamanca.org",
        "location": "Salamanca, Madrid",
        "custom_intro": "La AV de Salamanca promueve iniciativas que mejoran la calidad de vida del vecindario."
    },
    {
        "name": "Comunidad de Propietarios Gran Vía 45",
        "type": "comunidad",
        "email": "admin@comunidadgv45.com",
        "location": "Centro, Madrid",
        "custom_intro": "Las comunidades de vecinos buscan formas de facilitar la convivencia y ayuda mutua."
    },
    {
        "name": "Plataforma Mayores Activos Madrid",
        "type": "ong",
        "email": "contacto@mayoresactivos.org",
        "location": "Madrid",
        "custom_intro": "Mayores Activos conecta a personas jubiladas con oportunidades de aportar su experiencia."
    },
    {
        "name": "Universidad Popular de Madrid",
        "type": "educacion",
        "email": "info@univpopulardemadrid.org",
        "location": "Madrid",
        "custom_intro": "La Universidad Popular fomenta el intercambio de conocimientos entre generaciones."
    }
]

def generate_codoacodo_email(target):
    """Generar email personalizado para Codo a Codo"""
    
    subject = f"Herramienta gratuita para fortalecer {target['location']}"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
.container {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
.header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
.header h1 {{ margin: 0; font-size: 22px; }}
.content {{ padding: 10px 0; }}
.content p {{ margin: 15px 0; }}
.highlight {{ background: #f0f4ff; padding: 15px; border-left: 4px solid #667eea; border-radius: 6px; margin: 20px 0; }}
.benefits {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
.benefits h3 {{ color: #667eea; margin-top: 0; }}
.benefits ul {{ list-style: none; padding: 0; }}
.benefits li {{ padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
.benefits li:before {{ content: "✓ "; color: #28a745; font-weight: bold; }}
.cta {{ text-align: center; margin: 30px 0; }}
.cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; }}
.footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🤝 Codo a Codo - Red Vecinal</h1>
</div>

<div class="content">
<p>Hola {target['name']},</p>

<p>{target['custom_intro']}</p>

<div class="highlight">
<p style="margin: 0;"><strong>Codo a Codo</strong> es una plataforma donde vecinos intercambian servicios por tiempo (no dinero): 1 hora de ayuda = 1 hora ganada.</p>
</div>

<p>Ejemplos reales:</p>

<div class="benefits">
<h3>✅ Cómo funciona:</h3>
<ul>
<li>María monta muebles → Gana 1 hora</li>
<li>Usa esa hora con Pedro para clases de inglés</li>
<li>Pedro usa sus horas con Ana para paseo de mascotas</li>
<li>Sin dinero, solo comunidad y confianza</li>
</ul>
</div>

<p><strong>Beneficios para {target['location']}:</strong></p>
<ul>
<li>Fortalece el tejido social del barrio</li>
<li>Conecta generaciones (mayores ↔ jóvenes)</li>
<li>Reduce aislamiento y soledad no deseada</li>
<li>Fomenta economía colaborativa local</li>
<li>100% gratuito para asociaciones/ayuntamientos</li>
</ul>

<p>¿Te interesaría una demo de 15 minutos para ver si encaja con vuestra misión?</p>

<div class="cta">
<a href="https://codoacodo.es" class="cta-button">Ver Demo Gratuita →</a>
</div>

<p style="font-size: 14px; color: #666;">Sin compromiso. Podemos adaptarlo a las necesidades específicas de {target['location']}.</p>

<p>Saludos,<br><strong>Max</strong><br>Codo a Codo - Tu red de apoyo vecinal</p>
</div>

<div class="footer">
<p><a href="https://codoacodo.es" style="color: #667eea;">www.codoacodo.es</a></p>
</div>
</div>
</body>
</html>"""
    
    return subject, html

def send_email(target, subject, html):
    """Enviar email"""
    
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER
    msg['To'] = target['email']
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, target['email'], msg.as_string())
        server.quit()
        return {"status": "sent"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def main():
    """Ejecutar outreach de Codo a Codo"""
    
    print("=== MAX - Outreach Codo a Codo ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    sent = 0
    failed = 0
    
    for i, target in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] Enviando a {target['name']}...")
        
        subject, html = generate_codoacodo_email(target)
        result = send_email(target, subject, html)
        
        if result['status'] == 'sent':
            sent += 1
            print(f"   ✅ Enviado a {target['email']}")
        else:
            failed += 1
            print(f"   ❌ Fallido: {result.get('error', 'Unknown')}")
        
        import time
        time.sleep(3)  # Delay para no saturar
    
    print(f"\n✅ Outreach completado")
    print(f"   Enviados: {sent}")
    print(f"   Fallidos: {failed}")

if __name__ == "__main__":
    main()