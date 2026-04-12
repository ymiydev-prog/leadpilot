"""
Bybit API Client - YhasClaw
Trading functions for Bybit exchange
"""

import requests
import hmac
import hashlib
import time
import json
from typing import Optional, Dict, Any

class BybitClient:
    """Cliente de Bybit API v5"""
    
    BASE_URL = "https://api.bybit.com"
    TESTNET_URL = "https://api-testnet.bybit.com"
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = self.TESTNET_URL if testnet else self.BASE_URL
        
    # ==================== PUBLIC ENDPOINTS ====================
    
    def get_server_time(self) -> Dict:
        """Obtener tiempo del servidor"""
        response = requests.get(f"{self.base_url}/v5/market/time")
        return response.json()
    
    def get_tickers(self, category: str = "linear", symbol: str = None) -> Dict:
        """
        Obtener tickers de mercado
        category: linear (perpetual), spot, inverse, option
        """
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        response = requests.get(f"{self.base_url}/v5/market/tickers", params=params)
        return response.json()
    
    def get_kline(self, symbol: str, interval: str = "60", category: str = "linear", limit: int = 100) -> Dict:
        """
        Obtener velas (klines)
        interval: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M
        """
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(f"{self.base_url}/v5/market/kline", params=params)
        return response.json()
    
    def get_orderbook(self, symbol: str, category: str = "linear", limit: int = 25) -> Dict:
        """Obtener order book"""
        params = {"category": category, "symbol": symbol, "limit": limit}
        response = requests.get(f"{self.base_url}/v5/market/orderbook", params=params)
        return response.json()
    
    def get_instruments_info(self, category: str = "linear", symbol: str = None) -> Dict:
        """Obtener información de instrumentos"""
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        response = requests.get(f"{self.base_url}/v5/market/instruments-info", params=params)
        return response.json()
    
    # ==================== PRIVATE ENDPOINTS ====================
    
    def _generate_signature(self, timestamp: str, recv_window: str, query_string: str = "") -> str:
        """Generar firma para autenticación"""
        # Para GET requests, query_string va en la firma
        if query_string:
            param_str = str(timestamp) + self.api_key + recv_window + query_string
        else:
            param_str = str(timestamp) + self.api_key + recv_window
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self, query_string: str = "") -> Dict[str, str]:
        """Obtener headers con autenticación"""
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        signature = self._generate_signature(timestamp, recv_window, query_string)
        
        return {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature,
            "Content-Type": "application/json"
        }
    
    def get_wallet_balance(self, account_type: str = "UNIFIED") -> Dict:
        """
        Obtener balance de wallet
        account_type: UNIFIED, CONTRACT, SPOT
        """
        if not self.api_key or not self.api_secret:
            raise ValueError("Se requiere API key y secret para esta operación")
        
        params = {"accountType": account_type}
        query_string = "accountType=" + account_type
        headers = self._get_headers(query_string)
        
        response = requests.get(
            f"{self.base_url}/v5/account/wallet-balance",
            params=params,
            headers=headers
        )
        return response.json()
    
    def get_positions(self, category: str = "linear", symbol: str = None) -> Dict:
        """Obtener posiciones abiertas"""
        if not self.api_key or not self.api_secret:
            raise ValueError("Se requiere API key y secret para esta operación")
        
        params = {"category": category, "settleCoin": "USDT"}
        if symbol:
            params["symbol"] = symbol
        params_str = json.dumps(params, separators=(',', ':'))
        headers = self._get_headers(params_str)
        
        response = requests.get(
            f"{self.base_url}/v5/position/list",
            params=params,
            headers=headers
        )
        return response.json()
    
    def place_order(self, category: str, symbol: str, side: str, order_type: str, 
                    qty: float, price: float = None, stop_loss: float = None,
                    take_profit: float = None) -> Dict:
        """
        Crear orden
        
        Args:
            category: linear, spot
            symbol: BTCUSDT, ETHUSDT, etc
            side: Buy, Sell
            order_type: Market, Limit
            qty: Cantidad
            price: Precio (requerido para Limit)
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
        """
        if not self.api_key or not self.api_secret:
            raise ValueError("Se requiere API key y secret para esta operación")
        
        payload = {
            "category": category,
            "symbol": symbol,
            "side": side.capitalize(),
            "orderType": order_type.capitalize(),
            "qty": str(qty)
        }
        
        if order_type.lower() == "limit" and price:
            payload["price"] = str(price)
        
        if stop_loss:
            payload["stopLoss"] = str(stop_loss)
        
        if take_profit:
            payload["takeProfit"] = str(take_profit)
        
        headers = self._get_headers(json.dumps(payload))
        
        response = requests.post(
            f"{self.base_url}/v5/order/create",
            json=payload,
            headers=headers
        )
        return response.json()
    
    def cancel_order(self, category: str, symbol: str, order_id: str = None, 
                     order_link_id: str = None) -> Dict:
        """Cancelar orden"""
        if not self.api_key or not self.api_secret:
            raise ValueError("Se requiere API key y secret para esta operación")
        
        payload = {"category": category, "symbol": symbol}
        if order_id:
            payload["orderId"] = order_id
        if order_link_id:
            payload["orderLinkId"] = order_link_id
        
        headers = self._get_headers(json.dumps(payload))
        
        response = requests.post(
            f"{self.base_url}/v5/order/cancel",
            json=payload,
            headers=headers
        )
        return response.json()
    
    def get_open_orders(self, category: str = "linear", symbol: str = None) -> Dict:
        """Obtener órdenes abiertas"""
        if not self.api_key or not self.api_secret:
            raise ValueError("Se requiere API key y secret para esta operación")
        
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        params_str = json.dumps(params, separators=(',', ':'))
        headers = self._get_headers(params_str)
        
        response = requests.get(
            f"{self.base_url}/v5/order/realtime",
            params=params,
            headers=headers
        )
        return response.json()
    
    def get_order_history(self, category: str = "linear", symbol: str = None, limit: int = 50) -> Dict:
        """Obtener historial de órdenes"""
        if not self.api_key or not self.api_secret:
            raise ValueError("Se requiere API key y secret para esta operación")
        
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        params_str = json.dumps(params, separators=(',', ':'))
        headers = self._get_headers(params_str)
        
        response = requests.get(
            f"{self.base_url}/v5/order/history",
            params=params,
            headers=headers
        )
        return response.json()
    
    # ==================== UTILITY METHODS ====================
    
    def get_price(self, symbol: str, category: str = "linear") -> Optional[float]:
        """Obtener precio actual de un símbolo"""
        try:
            result = self.get_tickers(category, symbol)
            if result.get("retCode") == 0 and result.get("result", {}).get("list"):
                return float(result["result"]["list"][0]["lastPrice"])
            return None
        except Exception as e:
            print(f"Error obteniendo precio: {e}")
            return None
    
    def get_funding_rate(self, symbol: str, category: str = "linear") -> Optional[Dict]:
        """Obtener funding rate"""
        params = {"category": category, "symbol": symbol}
        response = requests.get(f"{self.base_url}/v5/market/funding/history", params=params)
        return response.json()


# ==================== CONVENIENCE FUNCTIONS ====================

def create_client(api_key: str = None, api_secret: str = None, testnet: bool = False) -> BybitClient:
    """Crear cliente de Bybit"""
    return BybitClient(api_key, api_secret, testnet)

def get_market_price(symbol: str) -> Optional[float]:
    """Obtener precio de mercado (sin autenticación)"""
    client = BybitClient()
    return client.get_price(symbol)
    
def get_market_data(symbol: str, interval: str = "60", limit: int = 100) -> Dict:
    """Obtener datos de mercado (sin autenticación)"""
    client = BybitClient()
    return client.get_kline(symbol, interval, "linear", limit)


if __name__ == "__main__":
    # Ejemplo de uso (solo endpoints públicos)
    client = BybitClient()
    
    print("=== Tiempo del servidor ===")
    print(json.dumps(client.get_server_time(), indent=2))
    
    print("\n=== Precio BTC ===")
    price = client.get_price("BTCUSDT")
    print(f"BTC/USDT: ${price}")
    
    print("\n=== Instrumentos disponibles ===")
    instruments = client.get_instruments_info(category="linear")
    if instruments.get("result", {}).get("list"):
        for inst in instruments["result"]["list"][:5]:
            print(f"{inst['symbol']}: {inst['status']}")
    
    print("\n=== Para trading, inicializar con API keys ===")
    print("client = BybitClient(api_key='xxx', api_secret='xxx')")