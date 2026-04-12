#!/usr/bin/env python3
"""Completar thread - tweets 6-9"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/twitter')
from thread_publisher import TwitterThreadPublisher

# Tweets restantes
TWEETS = [
    """5 shifts estructurales en AI trading este año:

1. De backtesting estático a simulación adaptativa
2. De señales manuales a discovery automático
3. De single-strategy a multi-agent orchestration
4. De black-box a interpretable decisions
5. De retail tools a institutional architecture

https://mindflmarkets.ai/ai-trading-2026""",

    """Casos de éxito que no son hype:

• Prediction markets: AI agents sin emoción
• Market making: spreads optimizados en tiempo real
• Portfolio rebalancing: respuesta a macro events

Lo aburrido que funciona > Lo sexy que falla.""",

    """Lo que NO funciona:

• Agents sin human-in-the-loop
• Overfitting a datos históricos
• Ignorar slippage y fees
• Confundir correlación con causalidad

El agent más inteligente pierde si la estrategia base es mala.""",

    """El futuro del trading automatizado:

No bots que ejecutan.
Agents que piensan.

La ventaja competitiva no es tener AI.
Es tener AI que aprende de sus errores.

Fin del thread 🧵"""
]

# Último tweet publicado
LAST_TWEET_ID = "2041830833221243232"

if __name__ == "__main__":
    print("Completando thread...")
    publisher = TwitterThreadPublisher()
    
    previous_id = LAST_TWEET_ID
    for i, tweet in enumerate(TWEETS, start=6):
        print(f"Publicando tweet {i}/9...")
        result = publisher.post_tweet(tweet, reply_to=previous_id)
        
        if "data" in result and "id" in result["data"]:
            previous_id = result["data"]["id"]
            print(f"✅ Tweet {i} publicado: {previous_id}")
        else:
            print(f"❌ Error en tweet {i}: {result}")
            break