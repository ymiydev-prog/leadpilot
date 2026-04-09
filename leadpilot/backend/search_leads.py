#!/usr/bin/env python3
"""
LeadPilot - Lead Search Engine
Usa web_search real via Firecrawl (OpenClaw)
"""

import sys
import json
import subprocess
import re
import urllib.parse

def search_with_firecrawl(query, location, max_results=20):
    """Buscar leads usando Firecrawl via OpenClaw gateway"""
    leads = []
    search_query = f"{query} {location} empresa contacto"
    
    try:
        encoded = urllib.parse.quote(search_query)
        # Llamar al gateway de OpenClaw
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30",
             f"http://127.0.0.1:18789/web_search?query={encoded}&count={max_results}"],
            capture_output=True, text=True, timeout=35
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            results = data.get("results", [])
            
            for i, item in enumerate(results[:max_results]):
                title = item.get("title", "").strip()
                url = item.get("url", "")
                desc = item.get("description", item.get("snippet", "")).strip()
                
                # Limpiar título
                title = re.sub(r'<[^>]+>', '', title)
                
                # Extraer nombre de empresa
                company = title.split(" - ")[0].split(" | ")[0].split(" – ")[0].strip()
                
                # Extraer dominio
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                domain = domain_match.group(1) if domain_match else ""
                
                # Extraer email del snippet
                email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', desc)
                email = email_match.group(0) if email_match else ""
                
                # Extraer teléfono del snippet
                phone_match = re.search(r'[\+\d\s\-\(\)]{9,20}', desc)
                phone = phone_match.group(0).strip() if phone_match else ""
                
                if company and url:
                    leads.append({
                        "id": i + 1,
                        "name": company[:100],
                        "website": url,
                        "domain": domain,
                        "email": email,
                        "phone": phone,
                        "description": desc[:200],
                        "source": "web_search",
                        "status": "new"
                    })
            
            return leads
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    
    return []

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "restaurantes"
    location = sys.argv[2] if len(sys.argv) > 2 else "Madrid"
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    leads = search_with_firecrawl(query, location, max_results)
    
    # Eliminar duplicados por dominio
    seen = set()
    unique = []
    for lead in leads:
        d = lead.get("domain", "")
        if d and d not in seen:
            seen.add(d)
            unique.append(lead)
    
    print(json.dumps(unique, ensure_ascii=False, indent=2))