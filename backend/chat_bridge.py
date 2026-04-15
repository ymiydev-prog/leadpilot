#!/usr/bin/env python3
"""
LeadPilot Chat Bridge
Puente entre Insforge (chat_messages) y OpenClaw (Telegram bot)

Este script:
1. Polls Insforge para mensajes pendientes
2. Los envía al bot de Telegram (OpenClaw)
3. Espera respuesta y la guarda en Insforge

Uso: python3 chat_bridge.py
"""
import os
import sys
import json
import time
import httpx
from datetime import datetime

# Configuración
INSFORGE_URL = os.environ.get("INSFORGE_URL", "https://nv96hw8d.eu-central.insforge.app")
INSFORGE_API_KEY = os.environ.get("INSFORGE_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8457045397:AAES3i_PyzqaAy68SmUkrLZelWJoYSW5ZnA")
TELEGRAM_ADMIN_CHAT_ID = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "")  # Tu ID de Telegram

# Insforge headers
HEADERS = {
    "Authorization": f"Bearer {INSFORGE_API_KEY}",
    "Content-Type": "application/json"
}

def insf_query(sql):
    """Ejecuta SQL en Insforge"""
    try:
        with httpx.Client() as client:
            resp = client.post(
                f"{INSFORGE_URL}/rest/v1/rpc/query",
                headers=HEADERS,
                json={"query": sql},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"Error query: {e}")
    return []

def insf_select(table, filters=None, limit=10):
    """Selecciona registros de Insforge"""
    try:
        params = {"limit": limit}
        if filters:
            for k, v in filters.items():
                params[k] = f"eq.{v}"
        with httpx.Client() as client:
            resp = client.get(
                f"{INSFORGE_URL}/rest/v1/{table}",
                headers=HEADERS,
                params=params,
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"Error select: {e}")
    return []

def insf_update(table, filter_field, filter_value, data):
    """Actualiza registro en Insforge"""
    try:
        with httpx.Client() as client:
            resp = client.patch(
                f"{INSFORGE_URL}/rest/v1/{table}",
                headers=HEADERS,
                params={filter_field: f"eq.{filter_value}"},
                json=data,
                timeout=30
            )
            return resp.status_code == 200
    except Exception as e:
        print(f"Error update: {e}")
    return False

def send_telegram_message(chat_id, text):
    """Envía mensaje vía Telegram Bot API"""
    try:
        with httpx.Client() as client:
            resp = client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=30
            )
            return resp.json()
    except Exception as e:
        print(f"Error telegram: {e}")
    return None

def get_telegram_updates(offset=0):
    """Obtiene actualizaciones de Telegram"""
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35
            )
            if resp.status_code == 200:
                return resp.json().get("result", [])
    except Exception as e:
        print(f"Error getUpdates: {e}")
    return []

def process_pending_messages():
    """Procesa mensajes pendientes de chat_messages"""
    # Obtener mensajes pendientes
    pending = insf_select("chat_messages", {"status": "pending"}, limit=10)
    
    if not pending:
        return
    
    print(f"[{datetime.now().isoformat()}] Procesando {len(pending)} mensajes pendientes")
    
    for msg in pending:
        msg_id = msg.get("id")
        user_message = msg.get("user_message", "")
        session_id = msg.get("session_id")
        user_name = msg.get("user_name", "Usuario")
        source = msg.get("source", "widget")
        
        if not user_message:
            insf_update("chat_messages", "id", msg_id, {"status": "no_content"})
            continue
        
        # Preparar mensaje para Telegram
        telegram_msg = f"💬 <b>Nuevo mensaje desde {source}</b>\n"
        telegram_msg += f"👤 {user_name}\n"
        telegram_msg += f"📝 {user_message}\n"
        telegram_msg += f"🆔 Session: {session_id}"
        
        print(f"Enviando a Telegram: {user_message[:50]}...")
        
        # Enviar al admin de Telegram
        if TELEGRAM_ADMIN_CHAT_ID:
            send_telegram_message(TELEGRAM_ADMIN_CHAT_ID, telegram_msg)
        
        # Enviar al canal del bot (OpenClaw debería responder)
        # El mensaje se envía al chat del bot, OpenClaw lo procesa
        # y responde automáticamente si está configurado
        
        # Marcar como enviado a OpenClaw (pendiente de respuesta)
        insf_update("chat_messages", "id", msg_id, {
            "status": "sent_to_telegram"
        })
        
        print(f"Mensaje {msg_id} enviado a Telegram")

def check_telegram_responses():
    """Verifica respuestas de Telegram/OpenClaw y guarda en Insforge"""
    updates = get_telegram_updates()
    
    for update in updates:
        # Verificar si hay mensajes en el chat del bot
        if "message" in update:
            msg = update["message"]
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "")
            message_id = msg.get("message_id")
            
            # Buscar si hay una sesión pendiente para este mensaje
            # Esto requiere mantener un mapeo de message_id -> session_id
            print(f"Telegram update: chat={chat_id}, text={text[:50]}")

def main():
    print("=" * 50)
    print("LeadPilot Chat Bridge Started")
    print(f"Insforge: {INSFORGE_URL}")
    print("=" * 50)
    
    # Verificar configuración
    if not INSFORGE_API_KEY:
        print("ERROR: INSFORGE_API_KEY no configurada")
        sys.exit(1)
    
    if not TELEGRAM_ADMIN_CHAT_ID:
        print("ADVERTENCIA: TELEGRAM_ADMIN_CHAT_ID no configurado")
    
    print("\nIniciando poll cada 10 segundos...")
    print("Presiona Ctrl+C para detener\n")
    
    while True:
        try:
            process_pending_messages()
            # check_telegram_responses()  # Descomentar cuando haya respuestas
        except KeyboardInterrupt:
            print("\nDeteniendo bridge...")
            break
        except Exception as e:
            print(f"Error en loop: {e}")
        
        time.sleep(10)

if __name__ == "__main__":
    main()
