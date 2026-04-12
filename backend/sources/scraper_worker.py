#!/usr/bin/env python3
"""LeadPilot Scraper - Firecrawl + SerpAPI fallback"""
import json
import sys
import subprocess
from urllib.parse import urlparse

# API Keys
FIRECRAWL_API_KEY = "fc-24b19712e51b417d95e99c533c759d59"
SERPAPI_KEY = "fdb59e0e13b4d187de300abcf36969d0889d6abe8696f8fa1225f5d691234035"

def search_firecrawl(query, location, max_results):
    """Search using Firecrawl"""
    sys.path.insert(0, '/root/.openclaw/workspace/leadpilot/venv/lib/python3.12/site-packages')
    try:
        from firecrawl import FirecrawlApp
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        result = app.search(f"{query} {location}", limit=max_results)
        
        leads = []
        seen = []
        
        for item in result.web:
            url = item.url
            title = item.title or ""
            
            # Skip aggregators
            skip = ['glassdoor', 'linkedin', 'twitter', 'facebook', 'instagram',
                    'pinterest', 'youtube', 'bing', 'yahoo', 'google', 
                    'builtin.com', 'wellfound.com', 'getlatka.com', 'goodfirms.co',
                    'tripadvisor', 'vogue.es', 'michelin', 'guiarepsol']
            
            if any(s in url.lower() for s in skip):
                continue
            
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.replace('www.', '') if parsed.netloc else parsed.path.split('/')[0]
            except:
                domain = url.split('/')[2] if '://' in url else url
            
            if not domain or domain in seen or len(domain) < 3:
                continue
            seen.append(domain)
            
            name = title.split('|')[0].split(' - ')[0].strip() if title else ""
            if not name or len(name) < 3:
                name = domain.split('.')[0].replace('-', ' ').title()
            
            leads.append({
                "name": name[:60],
                "domain": domain,
                "url": url,
                "email": f"info@{domain}" if '.' in domain else "",
                "phone": "",
                "company": name[:60],
                "source": "firecrawl",
                "location": location
            })
        
        return leads
        
    except Exception as e:
        print(f"Firecrawl error: {e}", file=sys.stderr)
        return []

def search_serpapi(query, location, max_results):
    """Search using SerpAPI as fallback"""
    import requests
    
    try:
        params = {
            "q": f"{query} {location}",
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "num": min(max_results, 10)
        }
        
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("organic_results", [])
            
            leads = []
            seen = []
            
            for result in results:
                link = result.get("link", "")
                title = result.get("title", "")
                
                # Skip aggregators
                skip = ['glassdoor', 'linkedin', 'twitter', 'facebook', 'instagram',
                        'pinterest', 'youtube', 'bing', 'yahoo', 'google', 
                        'builtin.com', 'wellfound.com', 'getlatka.com', 'goodfirms.co',
                        'tripadvisor', 'vogue', 'michelin', 'guiarepsol']
                
                if any(s in link.lower() for s in skip):
                    continue
                
                try:
                    parsed = urlparse(link)
                    domain = parsed.netloc.replace('www.', '') if parsed.netloc else parsed.path.split('/')[0]
                except:
                    domain = link.split('/')[2] if '://' in link else link
                
                if not domain or domain in seen or len(domain) < 3:
                    continue
                seen.append(domain)
                
                name = title.split('|')[0].split(' - ')[0].strip() if title else ""
                if not name or len(name) < 3:
                    name = domain.split('.')[0].replace('-', ' ').title()
                
                leads.append({
                    "name": name[:60],
                    "domain": domain,
                    "url": link,
                    "email": f"info@{domain}" if '.' in domain else "",
                    "phone": "",
                    "company": name[:60],
                    "source": "serpapi",
                    "location": location
                })
            
            return leads
            
    except Exception as e:
        print(f"SerpAPI error: {e}", file=sys.stderr)
        return []
    
    return []

def run_search(query="software", location="Madrid", max_results=20):
    """Run search and return leads list"""
    # Try Firecrawl first
    leads = search_firecrawl(query, location, max_results)
    
    # Fallback to SerpAPI if Firecrawl fails
    if not leads:
        print("Firecrawl failed, trying SerpAPI...", file=sys.stderr)
        leads = search_serpapi(query, location, max_results)
    
    return leads

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "software"
    location = sys.argv[2] if len(sys.argv) > 2 else "Madrid"
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    leads = run_search(query, location, max_results)
    print(json.dumps(leads, ensure_ascii=False))
    
    leads = run_search(query, location, max_results)
    print(json.dumps(leads, ensure_ascii=False))

if __name__ == "__main__":
    main()
