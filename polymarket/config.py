"""
Poly Agent Configuration - YhasClaw
Configuración del agente de Polymarket
"""

# Credenciales del usuario
WALLET_ADDRESS = "0xdce71ffa4a4fdcf8b3ec7d116a8eb8f2ed1a5d5b"
POLYMARKET_ID = "019d31f9-6f82-7954-aaa1-3ecb702cd692"

# API Endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Configuración de trading
DEFAULT_POSITION_SIZE = 3.00  # USD por trade
MAX_POSITION_SIZE = 5.00     # USD máximo por trade
MIN_LIQUIDITY = 5000         # Liquidez mínima para operar
MAX_MARKETS = 3              # Máximo de mercados para diversificar

# Estrategia
STRATEGY = "value_betting"   # value_betting, market_making, news_trading
RISK_LEVEL = "medium"        # low, medium, high