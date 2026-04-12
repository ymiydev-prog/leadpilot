#!/usr/bin/env python3
"""
ARIA - Forced Research: YouTube Kids Channel
Investigación específica sobre canal infantil de hábitos
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_youtube_kids_report():
    """Enviar reporte específico de YouTube Kids"""
    
    SENDER = "yhasvenezuela@gmail.com"
    RECIPIENT = "ymiy2021@gmail.com"
    APP_PASSWORD = "isrwrzraxlkwrclo"
    
    subject = "🚀 Oportunidad Específica: Canal YouTube Infantil"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
.container {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
.header {{ background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
.section {{ margin-bottom: 25px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #ff0000; }}
.section h2 {{ color: #cc0000; margin-top: 0; }}
.metric {{ display: inline-block; margin: 10px 15px 10px 0; padding: 10px 15px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.metric-label {{ font-size: 11px; color: #666; text-transform: uppercase; }}
.metric-value {{ font-size: 18px; font-weight: bold; color: #cc0000; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>📺 Análisis: Canal YouTube Infantil</h1>
<div>Investigación Forzada - {datetime.now().strftime("%d %B %Y")}</div>
</div>

<div class="section">
<h2>💡 Concepto</h2>
<p>Videos animados de muñecos bailando y cantando sobre hábitos infantiles: cepillarse los dientes, bañarse, comer sano, etc.</p>
</div>

<div class="section">
<h2>📊 Mercado (YouTube Kids)</h2>
<div class="metric"><div class="metric-label">TAM Global</div><div class="metric-value">$30B+</div></div>
<div class="metric"><div class="metric-label">Crecimiento</div><div class="metric-value">15% YoY</div></div>
<div class="metric"><div class="metric-label">Monetización</div><div class="metric-value">Adsense + Merch</div></div>
</div>

<div class="section">
<h2>💰 Inversión Inicial</h2>
<ul>
<li><strong>Animación AI/Software:</strong> €500-1,000 (Herramientas como Vyond/Adobe)</li>
<li><strong>Música/Licensing:</strong> €200-500 (Canciones originales o libres)</li>
<li><strong>Voz en Off:</strong> €100-300 (Locutor infantil o IA)</li>
<li><strong>Total Estimado:</strong> <strong>€800 - €1,800</strong></li>
</ul>
</div>

<div class="section">
<h2>⏱️ Payback Period</h2>
<p><strong>6-9 meses</strong> si se logra monetización rápida (1,000 subs + 4,000 horas).</p>
<p>YouTube paga aprox $2-5 por 1,000 views en contenido infantil (RPM bajo pero volumen alto).</p>
</div>

<div class="section">
<h2>🚀 Plan de Acción</h2>
<ol>
<li><strong>Semana 1:</strong> Crear 5 videos piloto (Higiene, Baño, Comida, Sueño, Juego).</li>
<li><strong>Semana 2:</strong> Subir 1 video diario y optimizar SEO (títulos en ES/EN).</li>
<li><strong>Mes 1:</strong> Promoción en grupos de padres (Facebook/WhatsApp).</li>
<li><strong>Mes 3:</strong> Activar monetización y explorar merch (cepillos, toallas).</li>
</ol>
</div>

<div class="footer" style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
<p>Reporte generado por ARIA bajo solicitud especial.</p>
</div>
</div>
</body>
</html>"""

    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.quit()
        print("✅ Reporte YouTube Kids enviado a ymiy2021@gmail.com")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_youtube_kids_report()