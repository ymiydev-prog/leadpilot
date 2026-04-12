#!/usr/bin/env python3
"""
Elon Agent - Publicar Tweets
Publica tweets de marketing para YhasClaw
USING OAuth 2.0 User Context
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

# Cargar credenciales
def load_config():
    config = {}
    config_path = Path(__file__).parent / "config.env"
    
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value
    
    return config

# Tweets a publicar
TWEETS = [
    {
        "text": "💡 Smart Money está moviéndose... ¿Estás siguiendo las señales correctas?\n\nEn YhasClaw monitoreamos los movimientos de las ballenas para que no te pierdas nada.\n\n📊 Los grandes jugadores no esperan a que el mercado suba - actúan antes.\n\n#SmartMoney #Trading #Crypto #Bitcoin",
        "topic": "Smart Money signals"
    },
    {
        "text": "🤖 Trading con IA: El futuro ya llegó\n\nYhasClaw no es solo un bot - es tu asistente de trading inteligente:\n\n✅ Monitoreo 24/7\n✅ Señales en tiempo real\n✅ Análisis automático\n\nLa IA no reemplaza tu criterio - lo potencia.\n\n#TradingBot #AI #Crypto #Trading",
        "topic": "Trading con IA"
    },
    {
        "text": "📚 Educación financiera del día:\n\n¿Cuál es la diferencia entre un trader exitoso y uno que pierde?\n\nEl trader exitoso tiene:\n1️⃣ Reglas claras de entrada/salida\n2️⃣ Gestión de riesgo definida\n3️⃣ Paciencia para esperar setups\n\nSin sistema = juego de azar 🎰\n\n#EducaciónFinanciera #Trading #Crypto",
        "topic": "Educación financiera"
    }
]

def post_tweet_oauth2(text: str, access_token: str) -> dict:
    """
    Publicar tweet usando OAuth 2.0 User Context
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {"text": text}
    
    response = requests.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers=headers
    )
    
    return response.json()

def refresh_access_token(refresh_token: str, client_id: str) -> dict:
    """
    Refrescar el access token usando OAuth 2.0
    """
    url = "https://api.twitter.com/2/oauth2/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": client_id
    }
    
    response = requests.post(url, data=data, headers=headers)
    return response.json()

def main():
    # Cargar configuración
    config = load_config()
    
    print("=" *50)
    print("🐦 ELON AGENT - Publicando Tweets (OAuth 2.0)")
    print("=" * 50)
    
    access_token = config.get('TWITTER_ACCESS_TOKEN', '')
    refresh_token = config.get('TWITTER_REFRESH_TOKEN', '')
    client_id = config.get('TWITTER_CLIENT_ID', '')
    
    if not access_token:
        print("❌ No hay ACCESS_TOKEN configurado")
        return False
    
    print(f"📋 Access Token: {access_token[:20]}...")
    print(f"📋 Client ID: {client_id[:20]}...")
    
    results = []
    
    for i, tweet in enumerate(TWEETS, 1):
        print(f"\n📤 Tweet {i}/3: {tweet['topic']}")
        print(f"   Texto: {tweet['text'][:60]}...")
        
        try:
            response = post_tweet_oauth2(tweet['text'], access_token)
            
            if 'data' in response:
                tweet_id = response['data'].get('id', 'N/A')
                print(f"   ✅ Publicado! ID: {tweet_id}")
                results.append({
                    "success": True,
                    "tweet_id": tweet_id,
                    "topic": tweet['topic'],
                    "text": tweet['text'],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif 'errors' in response:
                error = response['errors'][0] if response['errors'] else response
                error_msg = error.get('message', str(error))
                print(f"   ❌ Error: {error_msg}")
                
                # Si el token expiró, intentar refrescar
                if '401' in str(error) or 'Unauthorized' in str(error) or 'expired' in str(error).lower():
                    print("   🔄 Intentando refrescar token...")
                    if refresh_token and client_id:
                        refresh_response = refresh_access_token(refresh_token, client_id)
                        if 'access_token' in refresh_response:
                            new_access_token = refresh_response['access_token']
                            new_refresh_token = refresh_response.get('refresh_token', refresh_token)
                            print(f"   ✅ Token refrescado!")
                            # Intentar de nuevo con el nuevo token
                            response = post_tweet_oauth2(tweet['text'], new_access_token)
                            if 'data' in response:
                                tweet_id = response['data'].get('id', 'N/A')
                                print(f"   ✅ Publicado con nuevo token! ID: {tweet_id}")
                                results.append({
                                    "success": True,
                                    "tweet_id": tweet_id,
                                    "topic": tweet['topic'],
                                    "text": tweet['text'],
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                })
                                # Guardar nuevos tokens
                                config_path = Path(__file__).parent / "config.env"
                                with open(config_path, 'r') as f:
                                    content = f.read()
                                content = content.replace(f"TWITTER_ACCESS_TOKEN={access_token}", f"TWITTER_ACCESS_TOKEN={new_access_token}")
                                content = content.replace(f"TWITTER_REFRESH_TOKEN={refresh_token}", f"TWITTER_REFRESH_TOKEN={new_refresh_token}")
                                with open(config_path, 'w') as f:
                                    f.write(content)
                                continue
                
                results.append({
                    "success": False,
                    "topic": tweet['topic'],
                    "error": error_msg
                })
            else:
                print(f"   ❌ Respuesta inesperada: {response}")
                results.append({
                    "success": False,
                    "topic": tweet['topic'],
                    "error": str(response)
                })
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
            results.append({
                "success": False,
                "topic": tweet['topic'],
                "error": str(e)
            })
    
    # Guardar resultados
    output_path = Path(__file__).parent / "published_tweets.json"
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"\n📊 Resultados guardados en: {output_path}")
    
    # Resumen
    success_count = sum(1 for r in results if r.get('success'))
    print(f"\n{'='*50}")
    print(f"📈 RESUMEN: {success_count}/{len(TWEETS)} tweets publicados")
    print(f"{'='*50}")
    
    return success_count > 0

if __name__ == "__main__":
    main()