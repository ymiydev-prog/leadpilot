#!/usr/bin/env python3
"""
Jaime - Práctica Diaria de Trading Futuros
2 trades por día en Bybit Testnet
"""

import requests
import hashlib
import hmac
import time
import json
from urllib.parse import urlencode
from datetime import datetime, timezone
import random

# Credenciales Testnet
API_KEY = "7AeK9X0cBSorua2KWR"
API_SECRET = "sLXYHQNMvZT4NoJH2WBoFKfNbIjy6Jj5rvco"
BASE_URL = "https://api-testnet.bybit.com"

def private_get(endpoint, params=None):
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    if params is None:
        params = {}
    sorted_params = dict(sorted(params.items()))
    query_string = urlencode(sorted_params) if sorted_params else ""
    sign_string = f"{timestamp}{API_KEY}{recv_window}{query_string}"
    signature = hmac.new(API_SECRET.encode('utf-8'), sign_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }
    url = f"{BASE_URL}{endpoint}"
    if query_string:
        url += f"?{query_string}"
    response = requests.get(url, headers=headers)
    return response.json()

def private_post(endpoint, params=None):
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    if params is None:
        params = {}
    sorted_params = dict(sorted(params.items()))
    json_string = json.dumps(sorted_params)
    sign_string = f"{timestamp}{API_KEY}{recv_window}{json_string}"
    signature = hmac.new(API_SECRET.encode('utf-8'), sign_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, headers=headers, data=json_string)
    return response.json()

def public_get(endpoint, params=None):
    if params is None:
        params = {}
    query_string = urlencode(sorted(params.items())) if params else ""
    url = f"{BASE_URL}{endpoint}?{query_string}" if query_string else f"{BASE_URL}{endpoint}"
    response = requests.get(url)
    return response.json()

def get_balance():
    return private_get("/v5/account/wallet-balance", params={"accountType": "UNIFIED"})

def get_ticker(symbol):
    return public_get("/v5/market/tickers", params={"category": "linear", "symbol": symbol})

def get_position(symbol):
    return private_get("/v5/position/list", params={"category": "linear", "symbol": symbol})

def set_leverage(symbol, buy_lev, sell_lev):
    params = {
        "category": "linear",
        "symbol": symbol,
        "buyLeverage": str(buy_lev),
        "sellLeverage": str(sell_lev)
    }
    return private_post("/v5/position/set-leverage", params=params)

def place_market_order(symbol, side, qty):
    params = {
        "category": "linear",
        "symbol": symbol,
        "side": side.capitalize(),
        "orderType": "Market",
        "qty": str(qty)
    }
    return private_post("/v5/order/create", params=params)

def get_instrument_info(symbol):
    return public_get("/v5/market/instruments-info", params={"category": "linear", "symbol": symbol})

def close_position(symbol, side, qty):
    """Cierra posición existente"""
    params = {
        "category": "linear",
        "symbol": symbol,
        "side": side,  # "Sell" para cerrar long, "Buy" para cerrar short
        "orderType": "Market",
        "qty": str(qty),
        "reduceOnly": True
    }
    return private_post("/v5/order/create", params=params)

def get_order_history(symbol=None, limit=10):
    params = {"category": "linear", "limit": str(limit)}
    if symbol:
        params["symbol"] = symbol
    return private_get("/v5/order/history", params=params)

# ============ Pares de práctica ============
PRACTICE_PAIRS = [
    "ETHUSDT",   # Ethereum - Alta liquidez
    "SOLUSDT",   # Solana - Volátily popular
    "BTCUSDT",   # Bitcoin - El principal
    "BNBUSDT",   # BNB - Medio término
    "XRPUSDT",   # Ripple - Estable
]

def get_valid_qty(symbol, price, min_usd=5, available_usd=100):
    """Calcula cantidad válida para trading
    
    Args:
        symbol: Par de trading
        price: Precio actual
        min_usd: Valor mínimo de orden
        available_usd: USD disponible para trading (reducido por seguridad)
    """
    info = get_instrument_info(symbol)
    if info.get("retCode") != 0:
        return None
    
    inst = info.get("result", {}).get("list", [])[0]
    lot_size = inst.get("lotSizeFilter", {})
    min_qty = float(lot_size.get("minOrderQty", 0.001))
    qty_step = float(lot_size.get("qtyStep", 0.001))
    min_notional = float(lot_size.get("minNotionalValue", 5))
    
    # Usar solo una fracción del disponible para práctica
    safe_usd = min(available_usd, 50)  # Máximo $50 por trade de práctica
    
    # Calcular qty basado en el disponible seguro
    qty_for_safe = safe_usd / price
    
    # Redondear al step correcto
    steps = max(1, int(qty_for_safe / qty_step))
    valid_qty = steps * qty_step
    
    # Asegurar que cumple el mínimo
    if valid_qty < min_qty:
        valid_qty = min_qty
    
    return valid_qty

def practice_trade():
    print("🐾 JAIME - PRÁCTICA DIARIA DE TRADING")
    print("=" * 60)
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # 1. Seleccionar par aleatorio
    symbol = random.choice(PRACTICE_PAIRS)
    print(f"\n📊 Par seleccionado: {symbol}")
    
    # 2. Obtener precio
    ticker = get_ticker(symbol)
    if ticker.get("retCode") != 0:
        print(f"❌ Error obteniendo precio: {ticker.get('retMsg')}")
        return
    
    price = float(ticker['result']['list'][0]['lastPrice'])
    print(f"💰 Precio: ${price:,.4f}")
    
    # 3. Obtener balance
    balance = get_balance()
    if balance.get("retCode") != 0:
        print(f"❌ Error obteniendo balance: {balance.get('retMsg')}")
        return
    
    accounts = balance.get("result", {}).get("list", [])
    if not accounts:
        print("❌ Sin cuenta disponible")
        return
    
    equity = float(accounts[0].get('totalEquity', 0) or 0)
    print(f"💵 Equity: ${equity:,.2f}")
    
    # 4. Decidir dirección (50/50)
    direction = random.choice(["Buy", "Sell"])
    print(f"🎯 Dirección: {direction.upper()}")
    
    # 5. Calcular cantidad válida
    qty = get_valid_qty(symbol, price)
    if qty is None:
        print("❌ No se pudo calcular cantidad válida")
        return
    
    print(f"📦 Cantidad: {qty}")
    
    # 6. Configurar leverage bajo (1x para práctica)
    print("\n⚙️ Configurando leverage...")
    lev = set_leverage(symbol, 1, 1)
    if lev.get("retCode") == 0:
        print("✅ Leverage 1x configurado")
    elif lev.get("retCode") == 110043:
        print("⚠️ Leverage ya configurado")
    else:
        print(f"⚠️ Leverage: {lev.get('retMsg')}")
    
    # 7. Verificar posición existente
    pos = get_position(symbol)
    has_position = False
    pos_size = 0
    pos_side = None
    
    if pos.get("retCode") == 0:
        positions = pos.get("result", {}).get("list", [])
        if positions:
            p = positions[0]
            pos_size = float(p.get("size", 0))
            if pos_size > 0:
                has_position = True
                pos_side = p.get("side")
                print(f"📊 Posición existente: {pos_size} {symbol} ({pos_side})")
    
    # 8. Ejecutar trade
    print(f"\n🔄 Ejecutando trade #{1}...")
    print(f"   📤 {direction} {qty} {symbol} @ Market")
    
    order = place_market_order(symbol, direction, qty)
    ret_code = order.get("retCode")
    ret_msg = order.get("retMsg")
    
    if ret_code == 0:
        order_id = order.get("result", {}).get("orderId")
        print(f"\n   ═════════════════════════")
        print(f"   ✅ TRADE #1 EJECUTADO")
        print(f"   ═════════════════════════")
        print(f"   📋 Order ID: {order_id}")
        print(f"   📊 {direction} {qty} {symbol}")
        print(f"   💵 ~${price * qty:,.2f}")
        
        # Guardar transacción
        save_trade(symbol, direction, qty, price, order_id, "SUCCESS")
        
    elif ret_code == 30208:
        print(f"❌ Error: Precio fuera de rango")
        print(f"   Intentando con ETHUSDT...")
        
        # Fallback a ETH
        symbol = "ETHUSDT"
        ticker = get_ticker(symbol)
        price = float(ticker['result']['list'][0]['lastPrice'])
        qty = get_valid_qty(symbol, price)
        
        if qty:
            print(f"\n   📤 {direction} {qty} {symbol} @ ${price:,.2f}")
            order = place_market_order(symbol, direction, qty)
            
            if order.get("retCode") == 0:
                order_id = order.get("result", {}).get("orderId")
                print(f"   ✅ TRADE #1 EJECUTADO en ETH")
                save_trade(symbol, direction, qty, price, order_id, "SUCCESS")
            else:
                print(f"   ❌ Error: {order.get('retMsg')}")
                save_trade(symbol, direction, qty, price, None, "FAILED")
    else:
        print(f"❌ Error ({ret_code}): {ret_msg}")
        save_trade(symbol, direction, qty, price, None, "FAILED")
    
    # 9. Trade #2 - Cerrar posición o operación inversa
    print(f"\n🔄 Esperando 5 segundos...")
    time.sleep(5)
    
    print(f"\n🔄 Ejecutando trade #2...")
    
    # Obtener posición actual
    pos = get_position(symbol)
    if pos.get("retCode") == 0:
        positions = pos.get("result", {}).get("list", [])
        if positions:
            p = positions[0]
            new_size = float(p.get("size", 0))
            new_side = p.get("side")
            
            if new_size > 0:
                print(f"   📊 Posición abierta: {new_size} {symbol} ({new_side})")
                print(f"   📤 Cerrando posición...")
                
                # Cerrar posición
                close_side = "Sell" if new_side == "Buy" else "Buy"
                close_order = close_position(symbol, close_side, new_size)
                
                if close_order.get("retCode") == 0:
                    close_id = close_order.get("result", {}).get("orderId")
                    print(f"\n   ═════════════════════════")
                    print(f"   ✅ TRADE #2 EJECUTADO (CLOSE)")
                    print(f"   ═════════════════════════")
                    print(f"   📋 Close ID: {close_id}")
                    print(f"   📊 {close_side} {new_size} {symbol}")
                    
                    save_trade(symbol, close_side, new_size, price, close_id, "SUCCESS")
                else:
                    print(f"   ❌ Error cerrando: {close_order.get('retMsg')}")
                    save_trade(symbol, close_side, new_size, price, None, "FAILED")
            else:
                # Sin posición, hacer operación inversa
                inverse_dir = "Sell" if direction == "Buy" else "Buy"
                print(f"   📤 {inverse_dir} {qty} {symbol} @ Market")
                
                order2 = place_market_order(symbol, inverse_dir, qty)
                if order2.get("retCode") == 0:
                    order_id2 = order2.get("result", {}).get("orderId")
                    print(f"\n   ✅ TRADE #2 EJECUTADO")
                    save_trade(symbol, inverse_dir, qty, price, order_id2, "SUCCESS")
                else:
                    print(f"   ❌ Error: {order2.get('retMsg')}")
                    save_trade(symbol, inverse_dir, qty, price, None, "FAILED")
    
    # 10. Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRÁCTICA")
    print("=" * 60)
    print(f"   Par: {symbol}")
    print(f"   Trades intentados: 2")
    print(f"   Balance: ${equity:,.2f}")
    
    # Obtener historial reciente
    history = get_order_history(limit=5)
    if history.get("retCode") == 0:
        orders = history.get("result", {}).get("list", [])
        if orders:
            print(f"\n   Últimas órdenes:")
            for o in orders[:3]:
                print(f"   • {o.get('symbol')}: {o.get('side')} {o.get('qty')} @ ${float(o.get('avgPrice', 0)):,.4f}")
    
    print("\n🐾 Práctica completada")
    return True

def save_trade(symbol, side, qty, price, order_id, status):
    """Guarda trade en archivo de log"""
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "Jaime",
        "platform": "Bybit Testnet",
        "type": side,
        "symbol": symbol,
        "qty": qty,
        "price": price,
        "order_id": order_id,
        "status": status
    }
    
    # Guardar en archivo
    log_file = "/root/.openclaw/workspace/jaime_practice_log.json"
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(trade) + "\n")
    except:
        pass

if __name__ == "__main__":
    practice_trade()