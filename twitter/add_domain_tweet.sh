#!/bin/bash
cd /root/.openclaw/workspace/twitter
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/root/.openclaw/workspace/twitter')
from thread_publisher import TwitterThreadPublisher

# Tweet aclaratorio sobre el dominio
tweet_text = """SOBRE EL DOMINIO 👇

Para los que preguntan: LeadPilot está en leadpilot.es (no en bio, directooo)

Landing + Dashboard + Trial gratis ahí.

Si tienes agencia o consultancy y quieres leads de calidad, echale un vistazo."""

publisher = TwitterThreadPublisher()
result = publisher.post_tweet(tweet_text)

print(f"Tweet publicado: {result}")
PYEOF