#!/usr/bin/env python3
"""
LeadPilot.es - Lead Scraper
Busca empresas usando Firecrawl Search API
"""
import sys
import json
import requests
from urllib.parse import urlparse

FIRECRAWL_API_KEY = "fc-7d9a7bd9c81346dfbfba5c7d55743bd5"

def extract_domain(url):
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        return domain.replace('www.', '')
    except:
        return url.split('/')[0].replace('www.', '')

def search_leads(query, location="Madrid", max_results=20):
    """Busca leads con Firecrawl Search"""
    search_query = f"{query} {location}"
    
    try:
        response = requests.post(
            "https://api.firecrawl.dev/v0/search",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
            json={"query": search_query, "limit": max_results},
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"Error Firecrawl: {response.status_code}", file=sys.stderr)
            return []
        
        data = response.json()
        results = data.get('data', [])
        
        leads = []
        seen_domains = set()
        
        for item in results:
            metadata = item.get('metadata', {})
            url = metadata.get('sourceURL', '')
            
            if not url:
                continue
            
            # Filtrar sitios no deseados
            if any(bad in url for bad in ['google', 'bing', 'yahoo', 'linkedin', 'twitter', 'facebook', 'instagram', 'youtube', 'pinterest', 'tiktok', 'tripadvisor', 'michelin', 'tripadvisor']):
                continue
            
            domain = extract_domain(url)
            if not domain or 'www.' + domain == domain or domain in seen_domains:
                continue
            if not domain or '.' not in domain:
                continue
            
            seen_domains.add(domain)
            
            # Extraer nombre del dominio
            company_name = domain.split('.')[0].replace('-', ' ').replace('_', ' ').title()
            
            title = metadata.get('title', '')
            if title and len(title) > 2:
                clean_title = title.split('|')[0].split(' - ')[0].split('—')[0].strip()[:50]
                if clean_title and len(clean_title) > 3:
                    company_name = clean_title
            
            lead = {
                "name": company_name,
                "domain": domain,
                "url": url,
                "email": f"info@{domain}" if domain else "",
                "phone": "",
                "company": company_name,
                "source": "firecrawl",
                "location": location
            }
            leads.append(lead)
        
        return leads[:max_results]
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='LeadPilot Scraper')
    parser.add_argument('query', nargs='?', default='restaurantes')
    parser.add_argument('location', nargs='?', default='Madrid')
    parser.add_argument('max_results', nargs='?', type=int, default=20)
    args = parser.parse_args()
    
    leads = search_leads(args.query, args.location, args.max_results)
    print(json.dumps(leads, ensure_ascii=False, indent=2))