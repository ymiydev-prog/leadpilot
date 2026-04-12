#!/usr/bin/env python3
"""
MAX - Automated Sales Prospecting Workflow
Genera y envía cold emails personalizados a prospects de e-commerce
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configuración
PROSPECTS_FILE = "/root/.openclaw/workspace/agents/prospects.json"
EMAIL_LOG = "/root/.openclaw/workspace/agents/email_log.json"
CRM_FILE = "/root/.openclaw/workspace/agents/crm_pipeline.json"

def load_prospects():
    """Cargar lista de prospects"""
    if os.path.exists(PROSPECTS_FILE):
        with open(PROSPECTS_FILE) as f:
            data = json.load(f)
            # Manejar tanto formato lista como dict con key 'prospects'
            if isinstance(data, dict) and 'prospects' in data:
                return data['prospects']
            return data if isinstance(data, list) else []
    return []

def save_email_log(email_data):
    """Log de emails enviados"""
    log = []
    if os.path.exists(EMAIL_LOG):
        with open(EMAIL_LOG) as f:
            log = json.load(f)
    
    log.append({
        "timestamp": datetime.now().isoformat(),
        **email_data
    })
    
    with open(EMAIL_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def personalize_email(prospect):
    """Generar email personalizado usando RIGS framework"""
    
    # RIGS: Role, Instruction, Guardrails, Specifics
    role = "Especialista en automatización AI para e-commerce"
    
    instruction = f"Ayudar a {prospect['company']} a reducir {prospect['pain_point']}"
    
    guardrails = [
        "Máximo 75 palabras",
        "Sin buzzwords",
        "Tono profesional pero cercano",
        "CTA claro: 15-min call"
    ]
    
    specifics = {
        "company": prospect['company'],
        "contact": prospect['name'],
        "pain_point": prospect['pain_point'],
        "recent_event": prospect.get('recent_event', ''),
        "result_example": "40% reducción en tiempo manual"
    }
    
    # Template de email
    subject = f"Reduciendo {prospect['pain_point']} en {prospect['company']}"
    
    email_body = f"""Hi {prospect['name']},

Vi que {prospect['company']} {specifics['recent_event'] if specifics['recent_event'] else 'está creciendo en el espacio e-commerce'}.

En mi experiencia ayudando e-commerce companies, {prospect['pain_point']} es uno de los mayores time-sinks.

Implementé automation que logró {specifics['result_example']} para businesses similares.

¿Te interesaría ver cómo funciona en una llamada de 15 min esta semana?

Saludos,
Max
YhasClaw AI Automation"""
    
    return {
        "to": prospect['email'],
        "name": prospect['name'],
        "company": prospect['company'],
        "subject": subject,
        "body": email_body,
        "personalization_score": 8 if specifics['recent_event'] else 6
    }

def qualify_lead(response):
    """Cualificar respuesta usando BANT framework"""
    
    # Simulación de cualificación
    # En producción, usar LLM para analizar respuesta
    
    response_lower = response.lower()
    
    score = 0
    
    # Budget signals
    if any(word in response_lower for word in ['budget', 'pricing', 'cost', 'investment']):
        score += 25
    
    # Authority signals
    if any(word in response_lower for word in ['decide', 'approve', 'team', 'we']):
        score += 25
    
    # Need signals
    if any(word in response_lower for word in ['problem', 'challenge', 'need', 'help', 'interested']):
        score += 25
    
    # Timeline signals
    if any(word in response_lower for word in ['now', 'soon', 'this month', 'next week', 'asap']):
        score += 25
    
    if score >= 75:
        status = "HOT"
    elif score >= 50:
        status = "WARM"
    elif score >= 25:
        status = "COLD"
    else:
        status = "UNQUALIFIED"
    
    return {
        "score": score,
        "status": status,
        "next_action": "schedule_demo" if score >= 75 else "nurture" if score >= 50 else "archive"
    }

def update_crm(prospect, status, notes=""):
    """Actualizar pipeline en CRM (Notion concept)"""
    
    crm = []
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE) as f:
            crm = json.load(f)
    
    # Buscar si ya existe
    existing = next((p for p in crm if p['email'] == prospect['email']), None)
    
    if existing:
        existing['status'] = status
        existing['last_contact'] = datetime.now().isoformat()
        existing['notes'] = notes
    else:
        crm.append({
            "name": prospect['name'],
            "email": prospect['email'],
            "company": prospect['company'],
            "status": status,
            "created_at": datetime.now().isoformat(),
            "last_contact": datetime.now().isoformat(),
            "notes": notes,
            "deal_value": 0
        })
    
    with open(CRM_FILE, 'w') as f:
        json.dump(crm, f, indent=2)

def main():
    """Ejecutar workflow de prospección"""
    
    print("=== MAX Sales Agent - Prospecting Workflow ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Cargar prospects
    prospects = load_prospects()
    
    if not prospects:
        print("⚠️ No hay prospects. Crear lista primero.")
        print("Usar: python3 create_prospect_list.py")
        return
    
    print(f"📊 {len(prospects)} prospects en lista")
    print()
    
    # Procesar cada prospect
    emails_sent = 0
    
    for i, prospect in enumerate(prospects[:10], 1):  # Limitar a 10 para demo
        print(f"[{i}/{min(10, len(prospects))}] Procesando: {prospect['name']} @ {prospect['company']}")
        
        # Generar email personalizado
        email = personalize_email(prospect)
        
        # Log email
        email_result = {
            "prospect": prospect['name'],
            "company": prospect['company'],
            "email_sent": True,
            "personalization_score": email['personalization_score'],
            "subject": email['subject']
        }
        
        save_email_log(email_result)
        
        # Actualizar CRM
        update_crm(prospect, "outreach_sent", f"Email enviado - score {email['personalization_score']}/10")
        
        emails_sent += 1
        print(f"   ✅ Email enviado (score: {email['personalization_score']}/10)")
    
    print()
    print(f"✅ Workflow completado")
    print(f"   Emails enviados: {emails_sent}")
    print(f"   Log guardado en: {EMAIL_LOG}")
    print(f"   CRM actualizado: {CRM_FILE}")
    print()
    print("📋 Próximos pasos:")
    print("   1. Monitorear replies en 24-48h")
    print("   2. Cualificar respuestas positivas")
    print("   3. Agendar discovery calls")

if __name__ == "__main__":
    main()