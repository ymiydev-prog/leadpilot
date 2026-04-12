# Bybit Trading Module - YhasClaw

Módulo de trading para Bybit sin dependencias de terceros.

## Archivos Creados

```
bybit/
├── __init__.py      # Inicialización del módulo
├── client.py        # Cliente API de Bybit
├── trader.py        # Funciones de trading automático
├── config.env       # Configuración (añade tus API keys aquí)
└── README.md         # Este archivo
```

## Uso

### Sin API Key (Solo lectura)

```python
from bybit import BybitClient, YhasClawTrader

# Crear cliente público
client = BybitClient()

# Obtener precio
price = client.get_price("BTCUSDT")
print(f"BTC: ${price}")

# Obtener datos de mercado
klines = client.get_kline("BTCUSDT", "60", 100)

# Analizar mercado
trader = YhasClawTrader()
analysis = trader.analyze_market("BTCUSDT")
print(analysis)
```

### Con API Key (Trading)

```python
from bybit import YhasClawTrader

# Crear trader con API keys
trader = YhasClawTrader(
    api_key="TU_API_KEY",
    api_secret="TU_API_SECRET",
    testnet=False  # True para testnet
)

# Ver balance
balance = trader.get_balance()

# Compra a mercado
order = trader.place_market_buy("BTCUSDT", qty=0.001)

# Venta a mercado
order = trader.place_market_sell("BTCUSDT", qty=0.001)

# Orden limit
order = trader.place_limit_order(
    symbol="BTCUSDT",
    side="Buy",
    qty=0.001,
    price=65000,
    stop_loss=63000,
    take_profit=70000
)
```

## Funciones Disponibles

### Público (sin autenticación)

| Función | Descripción |
|---------|-------------|
| `get_server_time()` | Tiempo del servidor |
| `get_tickers()` | Precios de mercado |
| `get_kline()` | Velas/OHLCV |
| `get_orderbook()` | Order book |
| `get_instruments_info()` | Info de instrumentos |
| `get_price()` | Precio actual |
| `get_funding_rate()` | Funding rate |

### Privado (con autenticación)

| Función | Descripción |
|---------|-------------|
| `get_wallet_balance()` | Balance de cuenta |
| `get_positions()` | Posiciones abiertas |
| `place_order()` | Crear orden |
| `cancel_order()` | Cancelar orden |
| `get_open_orders()` | Órdenes abiertas |
| `get_order_history()` | Historial |

## Seguridad

- **NO** almacenes API keys en código
- Usa `config.env` para API keys
- Nunca compartas tus API secrets
- Usa testnet para pruebas

## Configuración

1. Copia `config.env.example` a `config.env`
2. Añade tus API keys
3. Importa el módulo

```bash
# Testnet para pruebas (sin dinero real)
BYBIT_TESTNET=true
BYBIT_API_KEY=tu_testnet_api_key
BYBIT_API_SECRET=tu_testnet_api_secret
```