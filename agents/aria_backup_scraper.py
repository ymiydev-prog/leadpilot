#!/usr/bin/env python3
"""
ARIA - Web Scraping Backup para búsqueda de oportunidades
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def search_with_scraping():
    """Busca oportunidades usando web scraping directo"""
    
    # Fuentes confiables para oportunidades de negocio
    sources = [
        {
            "name": "Product Hunt",
            "url": "https://www.producthunt.com/categories/machine-learning",
            "css": ".post-card__title-link"
        },
        {
            "name": "TechCrunch", 
            "url": "https://techcrunch.com/category/artificial-intelligence/",
            "css": ".post-block__title a"
        }
    ]
    
    results = []
    for source in sources:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            }
            r = requests.get(source["url"], headers=headers, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                links = soup.select(source["css"])
                for link in links[:3]:  # Top 3 por fuente
                    results.append({
                        "title": link.text.strip(),
                        "url": link.get("href", ""),
                        "source": source["name"],
                        "scraped_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"Error scraping {source['name']}: {e}")
    
    return results

if __name__ == "__main__":
    trends = search_with_scraping()
    print(json.dumps(trends, indent=2))
