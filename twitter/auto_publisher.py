#!/usr/bin/env python3
"""
Elon - Publicador Automático
Se ejecuta en horarios programados y publica si hay aprobación pendiente
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

DRAFT_FILE = Path("/root/.openclaw/workspace/twitter/draft_thread.json")
APPROVAL_FILE = Path("/root/.openclaw/workspace/twitter/approval_pending.json")
PUBLISHED_FILE = Path("/root/.openclaw/workspace/twitter/published.json")

def check_pending_approval():
    """Verifica si hay un thread pendiente de aprobación"""
    if APPROVAL_FILE.exists():
        with open(APPROVAL_FILE, "r") as f:
            return json.load(f)
    return None

def check_pending_draft():
    """Verifica si hay un draft pendiente"""
    if DRAFT_FILE.exists():
        with open(DRAFT_FILE, "r") as f:
            return json.load(f)
    return None

def publish_thread(tweets):
    """Publica el thread usando el publicador"""
    from thread_publisher import thread_publisher
    return thread_publisher.post_thread(tweets)

def main():
    print("🐾 ELON - VERIFICADOR DE PUBLICACIÓN")
    print("=" * 60)
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Verificar si es día y hora de publicación
    now = datetime.now(timezone.utc)
    weekday = now.weekday()
    hour = now.hour
    
    # Días permitidos: Lunes(0), Miércoles(2), Viernes(4)
    # Horas: Lunes 9:00, Miércoles 10:00, Viernes 9:00
    posting_schedule = {
        0: 9,   # Lunes 9:00 UTC
        2: 10,  # Miércoles 10:00 UTC
        4: 9    # Viernes 9:00 UTC
    }
    
    is_posting_time = weekday in posting_schedule and hour == posting_schedule[weekday]
    
    if not is_posting_time:
        print(f"⏭️ No es horario de publicación (Día: {weekday}, Hora: {hour})")
        print(f"   Próximo: Lunes/Miércoles/Viernes a las 9:00/10:00 UTC")
        return
    
    print(f"✅ Es horario de publicación: Día {weekday}, Hora {hour}:00")
    
    # Verificar aprobación pendiente
    approval = check_pending_approval()
    
    if approval and approval.get("status") == "approved":
        print("📋 Thread aprobado encontrado")
        print(f"   Tweets: {len(approval.get('tweets', []))}")
        
        # Publicar
        result = publish_thread(approval['tweets'])
        
        # Guardar como publicado
        published = {
            "published_at": datetime.now(timezone.utc).isoformat(),
            "thread_url": result.get("thread_url"),
            "tweets": approval['tweets'],
            "result": result
        }
        
        with open(PUBLISHED_FILE, "w") as f:
            json.dump(published, f, indent=2)
        
        # Limpiar aprobación pendiente
        APPROVAL_FILE.unlink(missing_ok=True)
        DRAFT_FILE.unlink(missing_ok=True)
        
        print(f"✅ Thread publicado: {result.get('thread_url')}")
    
    elif approval:
        print("⏳ Thread pendiente de aprobación")
        print(f"   Status: {approval.get('status')}")
    
    else:
        # Generar nuevo draft
        print("📝 Generando nuevo contenido...")
        subprocess.run(["python3", "/root/.openclaw/workspace/twitter/content_generator.py"])

if __name__ == "__main__":
    main()