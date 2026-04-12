"""
Twitter API Client - YhasClaw
Twitter/X API v2 client for Elon agent
OAuth 1.0a Authentication
"""

import requests
import urllib.parse
import time
import hashlib
import hmac
import base64
import secrets
from typing import Optional, Dict, Any

class TwitterClient:
    """Cliente de Twitter API v2 - OAuth 1.0a"""
    
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, config_path: str = None):
        """Inicializar cliente con credenciales"""
        self.consumer_key = "Larb2XdDIubuV2SXjBs1lyKuv"
        self.consumer_secret = "7OdE1qqSL4T6Pjaqz4O7yuVIHlOXSk410doHNNJkzfAVKXeRMe"
        self.access_token = "339920284-DPw5XcmrEa2AWgEEAKfvybH0AbXzfJ5TKydJS44r"
        self.access_token_secret = "zmIhr026BMp7y925tnjsdyP84fxD3DF1QIMmzWdBFwGtN"
    
    def _create_oauth_signature(self, method: str, url: str, params: dict) -> str:
        """Crear firma OAuth 1.0a"""
        param_string = "&".join([f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted(params.items())])
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(self.access_token_secret, safe='')}"
        signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
        return signature
    
    def _create_oauth_header(self, method: str, url: str, params: dict = None) -> str:
        """Crear header OAuth 1.0a"""
        if params is None:
            params = {}
        
        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_urlsafe(32),
            "oauth_signature_method": "HMAC-SHA1"
        }
        
        all_params = {**params, **oauth_params}
        signature = self._create_oauth_signature(method, url, all_params)
        oauth_params["oauth_signature"] = signature
        
        header_parts = [f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(oauth_params.items())]
        return "OAuth " + ", ".join(header_parts)
    
    def get_me(self) -> Dict[str, Any]:
        """Obtener información del usuario autenticado"""
        url = f"{self.BASE_URL}/users/me"
        headers = {"Authorization": self._create_oauth_header("GET", url)}
        response = requests.get(url, headers=headers)
        return response.json()
    
    def tweet(self, text: str, in_reply_to_tweet_id: str = None) -> Dict[str, Any]:
        """Publicar un tweet (opcionalmente como respuesta para hilos)"""
        url = f"{self.BASE_URL}/tweets"
        headers = {
            "Authorization": self._create_oauth_header("POST", url),
            "Content-Type": "application/json"
        }
        body = {"text": text}
        if in_reply_to_tweet_id:
            body["reply"] = {"in_reply_to_tweet_id": in_reply_to_tweet_id}
        response = requests.post(url, headers=headers, json=body)
        return response.json()
    
    def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Eliminar un tweet"""
        url = f"{self.BASE_URL}/tweets/{tweet_id}"
        headers = {"Authorization": self._create_oauth_header("DELETE", url)}
        response = requests.delete(url, headers=headers)
        return response.json()


# Instancia global para Elon
twitter = TwitterClient()

if __name__ == "__main__":
    # Prueba
    client = TwitterClient()
    print("Usuario:", client.get_me())
    print()
    print("Tweet de prueba:", client.tweet("🐾 Test desde YhasClaw!"))
