"""
Bybit Trading Functions - YhasClaw
Funciones de trading automáticopara Bybit
"""

from client import BybitClient, get_market_price, get_market_data
import json

class YhasClawTrader:
    """Sistema de trading de YhasClaw para Bybit"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = False):
        self.client = BybitClient(api_key, api_secret, testnet)
        self.positions = {}
        self.signals_history = []
        
    # ==================== MARKET ANALYSIS ====================
    
    def get_symbol_info(self, symbol: str) -> dict:
        """Obtener información completa de un símbolo"""
        try:
            # Precio actual
            price = self.client.get_price(symbol)
            
            # Order book
            orderbook = self.client.get_orderbook(symbol)
            
            #Info del instrumento
            instruments = self.client.get_instruments_info("linear", symbol)
            
            return {
                "symbol": symbol,
                "price": price,
                "orderbook": orderbook.get("result", {}),
                "info": instruments.get("result", {}).get("list", [{}])[0] if instruments.get("result", {}).get("list") else {}
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_market(self, symbol: str, interval: str = "60", limit: int = 100) -> dict:
        """Analizar mercado con datos históricos"""
        try:
            kline_data = self.client.get_kline(symbol, interval, "linear", limit)
            
            if kline_data.get("retCode") != 0:
                return {"error": kline_data.get("retMsg", "Unknown error")}
            
            candles = kline_data.get("result", {}).get("list", [])
            
            if not candles:
                return {"error": "No data available"}
            
            # Calcular indicadores simples
            closes = [float(c[4]) for c in candles]
            highs = [float(c[3]) for c in candles]
            lows = [float(c[2]) for c in candles]
            volumes = [float(c[5]) for c in candles]
            
            current_price = closes[0]
            
            # SMA
            sma_20 = sum(closes[:20]) / 20 if len(closes) >= 20 else None
            sma_50 = sum(closes[:50]) / 50 if len(closes) >= 50 else None
            
            # RSI simple
            gains = []
            losses = []
            for i in range(1, min(15, len(closes))):
                change = closes[i-1] - closes[i]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs)) if rs > 0 else 100
            
            # Volatilidad
            price_range = max(highs[:20]) - min(lows[:20]) if len(highs) >= 20 else 0
            volatility = (price_range / current_price) * 100 if current_price > 0 else 0
            
            #Volumen promedio
            avg_volume = sum(volumes[:20]) / 20 if len(volumes) >= 20 else 0
            
            # Señal simple
            signal = "NEUTRAL"
            if sma_20 and sma_50:
                if current_price > sma_20 > sma_50 and rsi < 70:
                    signal = "BUY"
                elif current_price < sma_20 < sma_50 and rsi > 30:
                    signal = "SELL"
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "rsi": rsi,
                "volatility": volatility,
                "avg_volume": avg_volume,
                "signal": signal,
                "trend": "BULLISH" if current_price > sma_20 > sma_50 else "BEARISH" if current_price < sma_20 < sma_50 else "NEUTRAL"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== TRADING ====================
    
    def place_market_buy(self, symbol: str, qty: float, stop_loss: float = None, take_profit: float = None) -> dict:
        """Compra a mercado"""
        if not self.client.api_key:
            return {"error": "Se requiere API key para trading"}
        
        return self.client.place_order(
            category="linear",
            symbol=symbol,
            side="Buy",
            order_type="Market",
            qty=qty,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    def place_market_sell(self, symbol: str, qty: float, stop_loss: float = None, take_profit: float = None) -> dict:
        """Venta a mercado"""
        if not self.client.api_key:
            return {"error": "Se requiere API key para trading"}
        
        return self.client.place_order(
            category="linear",
            symbol=symbol,
            side="Sell",
            order_type="Market",
            qty=qty,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    def place_limit_order(self, symbol: str, side: str, qty: float, price: float,
                          stop_loss: float = None, take_profit: float = None) -> dict:
        """Orden limit"""
        if not self.client.api_key:
            return {"error": "Se requiere API key para trading"}
        
        return self.client.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            order_type="Limit",
            qty=qty,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    def get_balance(self) -> dict:
        """Obtener balance de la cuenta"""
        if not self.client.api_key:
            return {"error": "Se requiere API key"}
        
        return self.client.get_wallet_balance()
    
    def get_open_positions(self, symbol: str = None) -> dict:
        """Obtener posiciones abiertas"""
        if not self.client.api_key:
            return {"error": "Se requiere API key"}
        
        return self.client.get_positions(symbol=symbol)
    
    def close_position(self, symbol: str, side: str, qty: float) -> dict:
        """Cerrar posición"""
        # Para cerrar una posición, hacemos una orden opuesta
        close_side = "Sell" if side.lower() == "buy" else "Buy"
        return self.place_market_order(symbol, close_side, qty)
    
    # ====================SIGNAL INTEGRATION ====================
    
    def process_smart_money_signal(self, signal: dict) -> dict:
        """
        Procesar señal de Smart Money de Binance
        signal debe tener: ticker, direction (buy/sell), smartMoneyCount, maxGain
        """
        ticker = signal.get("ticker", "").upper()
        direction = signal.get("direction", "buy").lower()
        smart_money_count = signal.get("smartMoneyCount", 0)
        max_gain = float(signal.get("maxGain", 0))
        
        # Convertir ticker deBinance a Bybit si es necesario
        symbol = f"{ticker}USDT"
        
        # Análisis del mercado
        analysis = self.analyze_market(symbol)
        
        if "error" in analysis:
            return analysis
        
        # Decisión basada en señales y análisis
        action = "WAIT"
        confidence = 0
        
        if direction == "buy":
            if smart_money_count >= 5 and max_gain > 20:
                action = "STRONG_BUY"
                confidence = 80 + min(smart_money_count * 2, 20)
            elif smart_money_count >= 3 and max_gain > 10:
                action = "BUY"
                confidence = 60 + min(smart_money_count * 2, 20)
            else:
                action = "WATCH"
                confidence = 40
        
        return {
            "symbol": symbol,
            "action": action,
            "confidence": confidence,
            "smart_money_count": smart_money_count,
            "max_gain": max_gain,
            "analysis": analysis
        }


if __name__ == "__main__":
    # Ejemplo de uso (modo público)
    trader = YhasClawTrader()
    
    print("=== Análisis de mercado ===")
    analysis = trader.analyze_market("BTCUSDT", "60", 100)
    print(json.dumps(analysis, indent=2, default=str))
    
    print("\n=== Para trading activo ===")
    print("trader = YhasClawTrader(api_key='xxx', api_secret='xxx')")