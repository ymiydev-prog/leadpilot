#!/usr/bin/env python3
"""
MAX - Email Outreach HTML Template
Genera emails HTML profesionales para cold outreach
"""

def generate_outreach_email(prospect):
    """Generar email HTML profesional"""
    
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
<h1>🚀 Automatización IA para {prospect['company']}</h1>
</div>

<div class="content">
<p>Hola {prospect['name']},</p>

<p>Vi que <strong>{prospect['company']}</strong> está creciendo en el sector {prospect.get('industry', 'e-commerce')}.</p>

<div class="highlight">
<p style="margin: 0;"><strong>Dato clave:</strong> Las tiendas online que automatizan su marketing reducen un 60% el tiempo manual y aumentan ventas un 35%.</p>
</div>

<p>En YhasClaw ayudamos a e-commerces españoles como el tuyo a:</p>

<div class="benefits">
<h3>✅ Lo que ofrecemos:</h3>
<ul>
<li>Automatización de email marketing (abandoned cart, welcome series)</li>
<li>Segmentación automática de clientes con IA</li>
<li>Generación de contenido para redes sociales</li>
<li>Monitoreo de competencia y precios</li>
<li>Reducción de 15+ horas/semana en tareas manuales</li>
</ul>
</div>

<p>¿Te interesaría ver cómo funciona en una demo de 15 minutos?</p>

<div class="cta">
<a href="https://blanchedalmond-ibis-360232.hostingersite.com/" class="cta-button">Ver Demo Gratis →</a>
</div>

<p style="font-size: 14px; color: #666;">Sin compromiso. Solo 15 minutos para ver si encaja con tu negocio.</p>

<p>Saludos,<br><strong>Max</strong><br>YhasClaw - Automatización IA para E-commerce</p>
</div>

<div class="footer">
<p>¿No te interesa? <a href="#" style="color: #999;">Darse de baja</a></p>
<p>YhasClaw |Automatización Inteligente para PyMEs</p>
</div>
</div>
</body>
</html>"""
    
    return html

def generate_subject_line(prospect):
    """Generar asunto personalizado"""
    
    subjects = [
        f"Reduciendo tiempo manual en {prospect['company']}",
        f"Idea para {prospect['company']} - Automatización IA",
        f"¿{prospect['name']}, 15 min para ver esto?",
        f"60% menos tiempo en marketing para {prospect['company']}",
        f"Automatización para {prospect.get('industry', 'tu e-commerce')}"
    ]
    
    return subjects[0]

if __name__ == "__main__":
    # Ejemplo
    prospect = {
        "name": "Pau García",
        "company": "TiendaOnline.es",
        "industry": "Moda sostenible",
        "email": "pau@tiendaonline.es"
    }
    
    html = generate_outreach_email(prospect)
    subject = generate_subject_line(prospect)
    
    print(f"Asunto: {subject}")
    print(f"\nHTML generado ({len(html)} caracteres)")
    print("Guardado en: outreach_email_template.html")
    
    with open("/root/.openclaw/workspace/agents/outreach_email_template.html", "w") as f:
        f.write(html)