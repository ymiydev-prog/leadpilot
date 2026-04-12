"""
Twitter Thread Publisher - YhasClaw
Publica hilos en Twitter/X usando OAuth 1.0a
"""

import requests
import urllib.parse
import time
import hashlib
import hmac
import base64
import secrets
from typing import List, Optional

class TwitterThreadPublisher:
    """Publicador de hilos Twitter"""
    
    def __init__(self):
        self.consumer_key = "Larb2XdDIubuV2SXjBs1lyKuv"
        self.consumer_secret = "7OdE1qqSL4T6Pjaqz4O7yuVIHlOXSk410doHNNJkzfAVKXeRMe"
        self.access_token = "339920284-DPw5XcmrEa2AWgEEAKfvybH0AbXzfJ5TKydJS44r"
        self.access_token_secret = "zmIhr026BMp7y925tnjsdyP84fxD3DF1QIMmzWdBFwGtN"
        self.base_url = "https://api.twitter.com/2"
    
    def _create_oauth_signature(self, method: str, url: str, params: dict) -> str:
        param_string = "&".join([f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted(params.items())])
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(self.access_token_secret, safe='')}"
        signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
        return signature
    
    def _create_oauth_header(self, method: str, url: str, params: dict = None) -> str:
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
    
    def post_tweet(self, text: str, reply_to: Optional[str] = None) -> dict:
        """Publicar un tweet, opcionalmente como reply"""
        url = f"{self.base_url}/tweets"
        body = {"text": text}
        
        if reply_to:
            body["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        headers = {
            "Authorization": self._create_oauth_header("POST", url),
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=body)
        return response.json()
    
    def post_thread(self, tweets: List[str]) -> dict:
        """Publicar un hilo completo"""
        if not tweets:
            return {"error": "No tweets provided"}
        
        results = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            print(f"Publicando tweet {i+1}/{len(tweets)}...")
            
            result = self.post_tweet(tweet_text, reply_to=previous_tweet_id)
            
            if "data" in result and "id" in result["data"]:
                previous_tweet_id = result["data"]["id"]
                results.append({
                    "tweet_number": i + 1,
                    "id": previous_tweet_id,
                    "text": tweet_text,
                    "status": "success"
                })
                print(f"✅ Tweet {i+1} publicado: {previous_tweet_id}")
            else:
                results.append({
                    "tweet_number": i + 1,
                    "text": tweet_text,
                    "status": "error",
                    "error": result
                })
                print(f"❌ Error en tweet {i+1}")
                break
            
            # Rate limiting
            time.sleep(1)
        
        return {
            "total_tweets": len(tweets),
            "published": len([r for r in results if r.get("status") == "success"]),
            "thread_url": f"https://twitter.com/yhas1984/status/{results[0]['id']}" if results[0].get("status") == "success" else None,
            "results": results
        }


# Instancia global
thread_publisher = TwitterThreadPublisher()


if __name__ == "__main__":
    # Ejemplo de uso
    test_thread = [
        "🧵 Test thread desde YhasClaw",
        "Este es el segundo tweet del hilo.",
        "Y este es el tercero. Los hilos permiten desarrollar ideas completas.",
        "¿Te parece mejor este formato? #AI #Twitter"
    ]
    
    print("Publicando hilo de prueba...")
    result = thread_publisher.post_thread(test_thread)
    print(result)