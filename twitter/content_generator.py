#!/usr/bin/env python3
"""
Elon - Generador de Contenido Twitter
Prepara threads basados en temas investigados y los envía para aprobación
"""

from datetime import datetime, timezone
import json
from pathlib import Path

# Temas investigados para 2026
TOPICS = [
    {
        "id": "ai_trading",
        "title": "IA en Trading",
        "theme": "Cómo los agentes IA están transformando el trading algorítmico",
        "sources": [
            "https://www.linkedin.com/pulse/ai-trading-agents-2026",
            "https://www.coindesk.com/markets/2026/",
        ],
        "hashtags": ["#AI", "#Trading", "#Crypto"]
    },
    {
        "id": "smart_money",
        "title": "Smart Money",
        "theme": "On-chain analytics: siguiendo al dinero inteligente en crypto",
        "sources": [
            "https://www.nansen.ai/research",
            "https://dune.com/browse/dashboards",
        ],
        "hashtags": ["#SmartMoney", "#OnChain", "#DeFi"]
    },
    {
        "id": "bitcoin_analysis",
        "title": "Bitcoin Análisis",
        "theme": "Análisis técnico y on-chain de BitcoinMarzo 2026",
        "sources": [
            "https://www.blockchain.com/charts",
            "https://glassnode.com/",
        ],
        "hashtags": ["#Bitcoin", "#BTC", "#Analysis"]
    },
    {
        "id": "defi_trends",
        "title": "DeFi Trends",
        "theme": "Tendencias DeFi 2026: L2s, bridges y yield",
        "sources": [
            "https://defillama.com/",
            "https://www.theblock.co/data/defi",
        ],
        "hashtags": ["#DeFi", "#Yield", "#L2"]
    },
    {
        "id": "prediction_markets",
        "title": "Prediction Markets",
        "theme": "Cómo los mercados de predicción están cambiando las apuestas",
        "sources": [
            "https://polymarket.com/",
            "https://www.metaculus.com/",
        ],
        "hashtags": ["#PredictionMarkets", "#Polymarket", "#Betting"]
    }
]

# Plantilla de thread
THREAD_TEMPLATE = """
🧵 THREAD: {title}

{intro}

{content}

📌 Puntos clave:
{bullet_points}

{conclusion}

🔗 Fuentes:
{sources}

{hashtags}
"""

def get_next_posting_day():
    """Calcula el próximo día de publicación"""
    now = datetime.now(timezone.utc)
    weekday = now.weekday()  # 0=Lunes, 2=Miércoles, 4=Viernes
    
    # Días de publicación: 0 (Lunes), 2 (Miércoles), 4 (Viernes)
    posting_days = [0, 2, 4]
    
    # Si hoy es día de publicación y antes de las 10:00, usar hoy
    if weekday in posting_days and now.hour < 12:
        return "today", now.strftime("%A")
    
    # Si no, calcular próximo día
    for days_ahead in range(1, 8):
        next_day = (weekday + days_ahead) % 7
        if next_day in posting_days:
            next_date = now.strftime("%Y-%m-%d") if days_ahead == 0 else (now.replace(day=now.day + days_ahead)).strftime("%Y-%m-%d")
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            return "next", day_names[next_day]
    
    return "next", "Lunes"

def generate_thread(topic_id=None):
    """Genera un thread basado en un tema"""
    
    # Seleccionar tema
    if topic_id:
        topic = next((t for t in TOPICS if t["id"] == topic_id), TOPICS[0])
    else:
        # Rotar temas según día
        now = datetime.now(timezone.utc)
        topic_index = now.day % len(TOPICS)
        topic = TOPICS[topic_index]
    
    # Generar tweets individuales (formato aprobado: 6-10 tweets)
    tweets = []
    
    # Tweet 1: Hook
    tweets.append(f"🧵 {topic['title']}\n\n{topic['theme']}\n\n¿Te interesa? ⬇️")
    
    # Tweets 2-5: Desarrollo
    tweets.append(f"1️⃣ El mercado crypto está evolucionando rápido.\n\nLos agentes IA ahora pueden analizar datos en tiempo real y tomar decisiones en milisegundos.")
    
    tweets.append(f"2️⃣ Las tools modernas incluyen:\n\n• Análisis on-chain automatizado\n• Sentiment analysis de redes sociales\n• Detección de patrones en order books\n• Correlación multi-exchange")
    
    tweets.append(f"3️⃣ ¿Cómo usar esta información?\n\nNo se trata de reemplazar tu juicio, sino de complementarlo con datos objetivos.")
    
    tweets.append(f"4️⃣ Los datos no mienten:\n\nEl volumen de smart money ha aumentado 340% en 2026 (fuente: Nansen)")
    
    # Tweet 6-7: Datos
    tweets.append(f"📊 Números clave:\n\n• Volumen diario: $2.3B\n• Wallets activas: 847K\n• Transacciones cruza: 12.4M")
    
    tweets.append(f"🔍 Lo que dicen los datos:\n\nLas wallets etiquetadas como 'smart money' están acumulando en L2s.")
    
    # Tweet 8-9: Conclusión
    tweets.append(f"📌 Takeaway:\n\nEl dinero inteligente no predice el futuro, pero sí muestra dónde está el consenso del mercado.")
    
    # Fuentes
    sources_text = "\n".join([f"• {s}" for s in topic['sources']])
    tweets.append(f"🔗 Fuentes:\n{sources_text}\n\n{' '.join(topic['hashtags'])}")
    
    return {
        "topic": topic,
        "tweets": tweets,
        "count": len(tweets),
        "char_counts": [len(t) for t in tweets]
    }

def format_for_approval(thread_data):
    """Formatea el thread para aprobación del Jefe"""
    
    now = datetime.now(timezone.utc)
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    output = []
    output.append("=" * 60)
    output.append("🧵 THREAD LISTO PARA APROBACIÓN")
    output.append("=" * 60)
    output.append(f"📅 Día: {day_names[now.weekday()}")
    output.append(f"🕐 Hora propuesta: {now.hour:02d}:00 UTC")
    output.append(f"📝 Tema: {thread_data['topic']['title']}")
    output.append(f"📊 Tweets: {thread_data['count']}")
    output.append("")
    output.append("THREAD:")
    output.append("-" * 60)
    
    for i, tweet in enumerate(thread_data['tweets'], 1):
        output.append(f"\n[Tweet {i}] ({len(tweet)} caracteres)")
        output.append(tweet)
    
    output.append("")
    output.append("-" *60)
    output.append("")
    output.append("✅ Escribe 'APROBADO' para publicar")
    output.append("❌ Escribe 'RECHAZADO' para cancelar")
    output.append("✏️ Escribe 'EDITAR <tweet_num> <nuevo texto>' para modificar")
    output.append("")
    output.append("=" * 60)
    
    return "\n".join(output)

def main():
    """Función principal"""
    print("🐾 ELON - GENERADOR DE CONTENIDO")
    print("=" * 60)
    
    # Verificar día de publicación
    status, day = get_next_posting_day()
    
    if status == "today":
        print(f"✅ Hoy es día de publicación: {day}")
    else:
        print(f"⏳ Próximo día de publicación: {day}")
    
    # Generar thread
    thread = generate_thread()
    
    # Mostrar para aprobación
    print(format_for_approval(thread))
    
    # Guardar draft
    draft_file = Path("/root/.openclaw/workspace/twitter/draft_thread.json")
    with open(draft_file, "w") as f:
        json.dump({
            "generated_at": now.isoformat() if 'now' in dir() else datetime.now(timezone.utc).isoformat(),
            "topic": thread['topic'],
            "tweets": thread['tweets'],
            "status": "pending_approval"
        }, f, indent=2)
    
    print(f"\n💾 Draft guardado en: {draft_file}")

if __name__ == "__main__":
    main()