#!/usr/bin/env python3
"""
Jaime - Simulación de Trading (Paper Trading)
3 trades diarios de práctica - SIN DINERO REAL
"""

import requests
import json
import random
from datetime import datetime, timezone
from pathlib import Path

# Pares para simulación
TRADING_PAIRS = [
    {"symbol": "BTCUSDT", "name": "Bitcoin", "volatility": "high"},
    {"symbol": "ETHUSDT", "name": "Ethereum", "volatility": "medium"},
    {"symbol": "SOLUSDT", "name": "Solana", "volatility": "high"},
    {"symbol": "BNBUSDT", "name": "BNB", "volatility": "low"},
    {"symbol": "XRPUSDT", "name": "XRP", "volatility": "medium"},
]

# Estado de simulación
SIMULATION_STATE = {
    "balance_usdt": 1000.00,  # Balance simulado
    "trades_today": 0,
    "positions": [],
    "trade_log": [],
    "win_rate": {"wins": 0, "losses": 0}
}

LOG_FILE = Path("/root/.openclaw/workspace/jaime_simulation_log.json")

def get_real_price(symbol):
    """Obtiene precio real de Binance public API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return float(resp.json()["price"])
    except:
        pass
    return None

def analyze_market(symbol, price):
    """Análisis técnico simulado"""
    # Simular indicadores aleatorios pero coherentes
    rsi = random.randint(20, 80)
    macd = random.choice(["bullish", "bearish", "neutral"])
    volume_trend = random.choice(["increasing", "decreasing", "stable"])
    
    # Lógica de decisión
    signals = []
    
    if rsi < 30:
        signals.append(f"RSI sobrevendido ({rsi})")
    elif rsi > 70:
        signals.append(f"RSI sobrecomprado ({rsi})")
    
    if macd == "bullish":
        signals.append("MACD bullish")
    elif macd == "bearish":
        signals.append("MACD bearish")
    
    if volume_trend == "increasing":
        signals.append("Volumen en aumento")
    
    # Decisión
    if rsi < 35 and macd == "bullish":
        decision = "BUY"
        confidence = "high"
    elif rsi > 65 and macd == "bearish":
        decision = "SELL"
        confidence = "high"
    elif rsi < 40:
        decision = "BUY"
        confidence = "medium"
    elif rsi > 60:
        decision = "SELL"
        confidence = "medium"
    else:
        decision = random.choice(["BUY", "SELL"])
        confidence = "low"
    
    return {
        "rsi": rsi,
        "macd": macd,
        "volume": volume_trend,
        "signals": signals,
        "decision": decision,
        "confidence": confidence
    }

def calculate_position_size(symbol, price):
    """Calcula tamaño de posición (1-5% del balance)"""
    global SIMULATION_STATE
    risk_pct = random.uniform(0.01, 0.05)  # 1-5%
    position_usd = SIMULATION_STATE["balance_usdt"] * risk_pct
    qty = position_usd / price
    
    return round(qty, 6)

def execute_simulation_trade(trade_num):
    """Ejecuta un trade simulado"""
    global SIMULATION_STATE
    
    print(f"\n{'='*60}")
    print(f"🔄 TRADE #{trade_num} - SIMULACIÓN")
    print(f"{'='*60}")
    
    # Seleccionar par aleatorio
    pair = random.choice(TRADING_PAIRS)
    symbol = pair["symbol"]
    name = pair["name"]
    
    print(f"\n📊 Par: {name} ({symbol})")
    
    # Obtener precio real
    price = get_real_price(symbol)
    if not price:
        price = random.uniform(100, 50000)  # Fallback
        print(f"   ⚠️ Precio simulado: ${price:,.2f}")
    else:
        print(f"   💰 Precio real: ${price:,.2f}")
    
    # Analizar mercado
    analysis = analyze_market(symbol, price)
    
    print(f"\n📈 ANÁLISIS:")
    print(f"   RSI: {analysis['rsi']}")
    print(f"   MACD: {analysis['macd']}")
    print(f"   Volumen: {analysis['volume']}")
    if analysis['signals']:
        print(f"   Señales: {', '.join(analysis['signals'])}")
    
    # Decisión
    decision = analysis['decision']
    confidence = analysis['confidence']
    
    print(f"\n🎯 DECISIÓN: {decision} (confianza: {confidence})")
    
    # Calcular tamaño
    qty = calculate_position_size(symbol, price)
    position_value = qty * price
    
    print(f"\n📦 POSICIÓN:")
    print(f"   Cantidad: {qty} {symbol.replace('USDT', '')}")
    print(f"   Valor: ${position_value:,.2f}")
    print(f"   Riesgo: {(position_value / SIMULATION_STATE['balance_usdt']) * 100:.1f}% del balance")
    
    # Simular resultado (más realista basado en análisis)
    if confidence == "high":
        win_chance = 0.65
    elif confidence == "medium":
        win_chance = 0.50
    else:
        win_chance = 0.40
    
    # Resultado
    is_win = random.random() < win_chance
    
    if is_win:
        # Ganancia
        pnl_pct = random.uniform(0.02, 0.08)  # 2-8% ganancia
        pnl = position_value * pnl_pct
        result = "WIN"
        SIMULATION_STATE["win_rate"]["wins"] += 1
    else:
        # Pérdida
        pnl_pct = random.uniform(-0.05, -0.02)  # 2-5% pérdida
        pnl = position_value * pnl_pct
        result = "LOSS"
        SIMULATION_STATE["win_rate"]["losses"] += 1
    
    # Actualizar balance
    SIMULATION_STATE["balance_usdt"] += pnl
    SIMULATION_STATE["trades_today"] += 1
    
    # Registrar trade
    trade = {
        "id": f"sim_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "Jaime",
        "platform": "Simulation",
        "symbol": symbol,
        "side": decision,
        "qty": qty,
        "price": price,
        "value": position_value,
        "analysis": analysis,
        "result": result,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "balance_after": SIMULATION_STATE["balance_usdt"]
    }
    
    SIMULATION_STATE["trade_log"].append(trade)
    
    # Mostrar resultado
    print(f"\n{'═'*60}")
    print(f"📊 RESULTADO: {'✅ WIN' if is_win else '❌ LOSS'}")
    print(f"{'═'*60}")
    print(f"   P&L: ${pnl:+,.2f} ({pnl_pct*100:+.1f}%)")
    print(f"   Balance: ${SIMULATION_STATE['balance_usdt']:,.2f}")
    
    # Win rate
    total = SIMULATION_STATE["win_rate"]["wins"] + SIMULATION_STATE["win_rate"]["losses"]
    if total > 0:
        wr = (SIMULATION_STATE["win_rate"]["wins"] / total) * 100
        print(f"   Win Rate: {wr:.1f}% ({SIMULATION_STATE['win_rate']['wins']}/{total})")
    
    # Guardar
    save_trade(trade)
    
    return trade

def save_trade(trade):
    """Guarda trade en log"""
    try:
        log_file = LOG_FILE
        if log_file.exists():
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = {"trades": [], "stats": {}}
        
        logs["trades"].append(trade)
        logs["stats"] = {
            "total_trades": len(logs["trades"]),
            "balance": SIMULATION_STATE["balance_usdt"],
            "win_rate": SIMULATION_STATE["win_rate"]
        }
        
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
        
        print(f"\n💾 Trade guardado en {log_file}")
    except Exception as e:
        print(f"⚠️ Error guardando: {e}")

def run_daily_simulation():
    """Ejecuta 3 trades diarios de simulación"""
    print("🐾 JAIME - SIMULACIÓN DE TRADING")
    print("=" * 60)
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"💰 Balance inicial: ${SIMULATION_STATE['balance_usdt']:,.2f}")
    print("=" * 60)
    
    # Cargar estado anterior si existe
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
                if logs.get("trades"):
                    last_trade = logs["trades"][-1]
                    last_date = datetime.fromisoformat(last_trade["timestamp"].replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    
                    # Si el último trade fue hoy, cargar estado
                    if last_date.date() == now.date():
                        # Stats del día actual
                        today_trades = [t for t in logs["trades"] 
                                      if datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00")).date() == now.date()]
                        SIMULATION_STATE["trades_today"] = len(today_trades)
                        
                        # Recalcular win rate
                        wins = sum(1 for t in today_trades if t["result"] == "WIN")
                        losses = sum(1 for t in today_trades if t["result"] == "LOSS")
                        SIMULATION_STATE["win_rate"] = {"wins": wins, "losses": losses}
                        
                        print(f"📊 Trades hoy: {SIMULATION_STATE['trades_today']}")
        except:
            pass
    
    # Ejecutar trades
    for i in range(1, 4):
        if SIMULATION_STATE["trades_today"] >= 3:
            print(f"\n✅ Ya se completaron los 3 trades diarios")
            break
        
        execute_simulation_trade(i)
        
        if i < 3:
            print(f"\n⏳ Esperando 3 segundos...")
            import time
            time.sleep(3)
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📋 RESUMEN DEL DÍA")
    print("=" * 60)
    print(f"   Trades: {SIMULATION_STATE['trades_today']}")
    print(f"   Balance final: ${SIMULATION_STATE['balance_usdt']:,.2f}")
    
    total = SIMULATION_STATE["win_rate"]["wins"] + SIMULATION_STATE["win_rate"]["losses"]
    if total > 0:
        wr = (SIMULATION_STATE["win_rate"]["wins"] / total) * 100
        print(f"   Win Rate: {wr:.1f}%")
        print(f"   Wins: {SIMULATION_STATE['win_rate']['wins']} | Losses: {SIMULATION_STATE['win_rate']['losses']}")
    
    print("\n🐾 Simulación completada")

if __name__ == "__main__":
    run_daily_simulation()