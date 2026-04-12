"""
Polymarket API Client - YhasClaw
Client for Polymarket prediction markets
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List
from enum import Enum

class PolymarketAPI:
    """Cliente de Polymarket API"""
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    DATA_API = "https://data-api.polymarket.com"
    CLOB_API = "https://clob.polymarket.com"
    
    def __init__(self, api_key: str = None, chain_id: int = 137):
        """
        Inicializar cliente de Polymarket
        
        Args:
            api_key: API key L1 (Polygon)
            chain_id: Chain ID (137 = Polygon)
        """
        self.api_key = api_key
        self.chain_id = chain_id
        
    # ==================== PUBLIC ENDPOINTS (No Auth) ====================
    
    def get_markets(self, limit: int = 100, offset: int = 0) -> Dict:
        """Obtener mercados activos"""
        response = requests.get(
            f"{self.GAMMA_API}/markets",
            params={"limit": limit, "offset": offset}
        )
        return response.json()
    
    def get_market(self, condition_id: str) -> Dict:
        """Obtener un mercado específico"""
        response = requests.get(
            f"{self.GAMMA_API}/markets/{condition_id}"
        )
        return response.json()
    
    def search_markets(self, query: str) -> Dict:
        """Buscar mercados"""
        response = requests.get(
            f"{self.GAMMA_API}/markets",
            params={"text": query}
        )
        return response.json()
    
    def get_events(self, limit: int = 100) -> Dict:
        """Obtener eventos"""
        response = requests.get(
            f"{self.GAMMA_API}/events",
            params={"limit": limit}
        )
        return response.json()
    
    def get_event(self, slug: str) -> Dict:
        """Obtener un evento específico"""
        response = requests.get(
            f"{self.GAMMA_API}/events/{slug}"
        )
        return response.json()
    
    def get_trending_markets(self) -> Dict:
        """Obtener mercados trending"""
        response = requests.get(
            f"{self.GAMMA_API}/markets",
            params={"_s": "trending"}
        )
        return response.json()
    
    # ==================== DATA API ====================
    
    def get_positions(self, address: str) -> Dict:
        """Obtener posiciones de una wallet"""
        response = requests.get(
            f"{self.DATA_API}/positions",
            params={"user": address}
        )
        return response.json()
    
    def get_trades(self, address: str) -> Dict:
        """Obtener trades de una wallet"""
        response = requests.get(
            f"{self.DATA_API}/trades",
            params={"user": address}
        )
        return response.json()
    
    def get_leaderboard(self) -> Dict:
        """Obtener leaderboard"""
        response = requests.get(f"{self.DATA_API}/leaderboard")
        return response.json()
    
    # ==================== CLOB API (Orderbook) ====================
    
    def get_orderbook(self, token_id: str) -> Dict:
        """Obtener orderbook para un token"""
        response = requests.get(
            f"{self.CLOB_API}/book",
            params={"token_id": token_id}
        )
        return response.json()
    
    def get_price(self, token_id: str) -> Dict:
        """Obtener precio actual"""
        response = requests.get(
            f"{self.CLOB_API}/price",
            params={"token_id": token_id}
        )
        return response.json()
    
    def get_prices(self, token_ids: List[str]) -> Dict:
        """Obtener precios para múltiples tokens"""
        response = requests.post(
            f"{self.CLOB_API}/prices",
            json={"tokens": token_ids}
        )
        return response.json()
    
    def get_midpoint(self, token_id: str) -> float:
        """Obtener precio medio (midpoint)"""
        data = self.get_price(token_id)
        if "price" in data:
            return float(data["price"])
        return 0.5  # Default midpoint


class PolyAgent:
    """Agente de Polymarket para YhasClaw"""
    
    def __init__(self, api_key: str = None, address: str = None):
        """
        Inicializar agente de Polymarket
        
        Args:
            api_key: API key L1 (Polygon)
            address: Wallet address
        """
        self.client = PolymarketAPI(api_key)
        self.address = address
        
    def get_trending(self) -> List[Dict]:
        """Obtener mercados trending"""
        data = self.client.get_trending_markets()
        if isinstance(data, list):
            return data
        return []
    
    def search(self, query: str) -> List[Dict]:
        """Buscar mercados"""
        data = self.client.search_markets(query)
        if isinstance(data, list):
            return data
        return []
    
    def get_market_info(self, condition_id: str) -> Dict:
        """Obtener info de un mercado"""
        return self.client.get_market(condition_id)
    
    def analyze_market(self, condition_id: str) -> Dict:
        """
        Analizar un mercado
        
        Returns:
            - Precio YES/NO
            - Volumen
            - Descripción
            - Odds implied
        """
        market = self.get_market_info(condition_id)
        
        if "condition_id" not in market:
            return {"error": "Market not found"}
        
        # Extraer datos relevantes
        result = {
            "condition_id": market.get("condition_id"),
            "question": market.get("question", ""),
            "description": market.get("description", ""),
            "end_date": market.get("end_date"),
            "outcome_prices": [],
        }
        
        # Obtener precios de outcomes
        outcomes = market.get("outcomes", [])
        for outcome in outcomes:
            price = float(outcome.get("price", 0))
            result["outcome_prices"].append({
                "name": outcome.get("outcome", ""),
                "price": price,
                "probability": price  # price = probability
            })
        
        return result
    
    def find_value_markets(self, min_volume: float = 10000) -> List[Dict]:
        """
        Encontrar mercados con potencial valor
        
        Args:
            min_volume: Volumen mínimo en USD
        
        Returns:
            Lista de mercados con valor potencial
        """
        markets = self.get_trending()
        value_markets = []
        
        for market in markets:
            volume = float(market.get("volume", 0))
            if volume >= min_volume:
                analysis = self.analyze_market(market.get("condition_id", ""))
                if "error" not in analysis:
                    value_markets.append({
                        "condition_id": market.get("condition_id"),
                        "question": market.get("question", ""),
                        "volume": volume,
                        "prices": analysis.get("outcome_prices", [])
                    })
        
        return value_markets


if __name__ == "__main__":
    # Test sin autenticación
    client = PolymarketAPI()
    
    print("=== Polymarket API Test ===")
    print()
    
    print("Buscando mercados trending...")
    trending = client.get_trending_markets()
    
    if isinstance(trending, list) and len(trending) > 0:
        print(f"Encontrados {len(trending)} mercados trending:")
        for m in trending[:5]:
            print(f"  - {m.get('question', 'N/A')[:60]}...")
    else:
        print(f"Respuesta: {trending}")
    
    print()
    print("Poly listo para operar")