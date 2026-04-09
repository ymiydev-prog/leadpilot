#!/usr/bin/env python3
"""
LeadPilot - Scraper v3
Usa Firecrawl API directamente (sin dependencias de OpenClaw)
"""

import sys
import json
import requests
import re

FIRECRAWL_API_KEY = "fc-7d9a7bd9c81346dfbfba5c7d55743bd5"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/search"

def search_leads(query, location, max_results=10):
    """Buscar leads usando Firecrawl API"""
    leads = []
    search_query = f"{query} {location} empresa contacto email teléfono"
    
    try:
        response = requests.post(
            FIRECRAWL_URL,
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "query": search_query,
                "limit": max_results,
                "lang": "es",
                "country": "es",
                "scrapeOptions": {
                    "formats": ["markdown"]
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", [])
            
            for i, item in enumerate(results[:max_results]):
                title = item.get("title", "").strip()
                url = item.get("url", "")
                desc = item.get("description", item.get("markdown", ""))[:300].strip()
                metadata = item.get("metadata", {})
                
                # Limpiar título
                title = re.sub(r'<[^>]+>', '', title)
                
                # Extraer nombre de empresa
                company = title.split(" - ")[0].split(" | ")[0].split(" – ")[0].strip()
                
                # Extraer dominio
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                domain = domain_match.group(1) if domain_match else ""
                
                # Extraer email
                email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', desc)
                email = email_match.group(0) if email_match else ""
                
                # Si no hay email en desc, intentar en metadata
                if not email:
                    email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', str(metadata))
                    email = email_match.group(0) if email_match else ""
                
                # Extraer teléfono
                phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,18}', desc)
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
                        "source": "Firecrawl",
                        "status": "new"
                    })
        else:
            print(f"Error Firecrawl: {response.status_code} - {response.text[:200]}", file=sys.stderr)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    
    # Eliminar duplicados por dominio
    seen = set()
    unique = []
    for lead in leads:
        d = lead.get("domain", "")
        if d and d not in seen:
            seen.add(d)
            unique.append(lead)
        elif not d:
            unique.append(lead)
    
    # Re-numerar
    for i, lead in enumerate(unique):
        lead["id"] = i + 1
    
    return unique

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "restaurantes"
    location = sys.argv[2] if len(sys.argv) > 2 else "Madrid"
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    leads = search_leads(query, location, max_results)
    print(json.dumps(leads, ensure_ascii=False, indent=2))