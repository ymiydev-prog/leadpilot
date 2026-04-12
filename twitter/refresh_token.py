#!/usr/bin/env python3
"""
Elon Agent -Refrescar Token OAuth 2.0
"""

import os
import sys
import json
from pathlib import Path
import requests

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

def refresh_access_token(refresh_token: str, client_id: str, client_secret: str = None) -> dict:
    """
    Refrescar el access token usando OAuth 2.0
    Twitter requiereclient_id + client_secret para refresh
    """
    url = "https://api.twitter.com/2/oauth2/token"
    
    # Twitter OAuth 2.0 requiere Basic Auth con client_id:client_secret
    import base64
    if client_secret:
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}"
        }
    else:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    if not client_secret:
        data["client_id"] = client_id
    
    print(f"🔄 Intentando refrescar token...")
    print(f"   Client ID: {client_id[:20]}...")
    print(f"   Refresh Token: {refresh_token[:20]}...")
    
    response = requests.post(url, data=data, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    
    return response.json()

def main():
    config = load_config()
    
    refresh_token = config.get('TWITTER_REFRESH_TOKEN', '')
    client_id = config.get('TWITTER_CLIENT_ID', '')
    client_secret = config.get('TWITTER_CONSUMER_SECRET', '')  # OAuth 2.0 usa client_secret
    
    print("=" * 50)
    print("🔄 ELON AGENT - Refrescando Token")
    print("=" * 50)
    
    result = refresh_access_token(refresh_token, client_id, client_secret)
    
    if 'access_token' in result:
        print(f"\n✅ Token refrescado exitosamente!")
        print(f"   Nuevo Access Token: {result['access_token'][:30]}...")
        
        # Guardar nuevos tokens
        config_path = Path(__file__).parent / "config.env"
        with open(config_path, 'r') as f:
            content = f.read()
        
        new_refresh = result.get('refresh_token', refresh_token)
        content = content.replace(
            f"TWITTER_ACCESS_TOKEN={config.get('TWITTER_ACCESS_TOKEN', '')}",
            f"TWITTER_ACCESS_TOKEN={result['access_token']}"
        )
        content = content.replace(
            f"TWITTER_REFRESH_TOKEN={refresh_token}",
            f"TWITTER_REFRESH_TOKEN={new_refresh}"
        )
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        print(f"   ✅ Tokens guardados en config.env")
        return result['access_token']
    else:
        print(f"\n❌ Error refrescando token:")
        print(f"   {result}")
        return None

if __name__ == "__main__":
    main()