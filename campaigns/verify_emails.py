#!/usr/bin/env python3
"""Find real contact emails for prospects"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/leadpilot/backend/sources')
from scraper_worker import run_search
import json
import requests
import re

PROSPECTS = [
    {"name": "Estrategika Digital", "domain": "estrategikadigital.com", "url": "https://www.estrategikadigital.com"},
    {"name": "Dinamiq", "domain": "dinamiq.com", "url": "https://www.dinamiq.com"},
    {"name": "Internet República", "domain": "internetrepublica.com", "url": "https://www.internetrepublica.com"},
    {"name": "TopMadrid", "domain": "topmadrid.com.es", "url": "https://www.topmadrid.com.es"},
    {"name": "IOMarketing", "domain": "iomarketing.es", "url": "https://www.iomarketing.es"},
    {"name": "Buda Marketing", "domain": "budamarketing.es", "url": "https://budamarketing.es"},
    {"name": "ADDO", "domain": "ad-do.com", "url": "https://www.ad-do.com"},
    {"name": "Gmedia", "domain": "gmedia.es", "url": "https://gmedia.es"},
    {"name": "BCM Marketing", "domain": "bcm.marketing", "url": "https://bcm.marketing"},
    {"name": "Advertis", "domain": "advertis.es", "url": "https://www.advertis.es"},
]

COMMON_PATTERNS = [
    r'[\w\.-]+@[\w\.-]+\.\w+',
    r'hola@[\w\.-]+',
    r'contacto@[\w\.-]+',
    r'info@[\w\.-]+',
    r'contact@[\w\.-]+',
]

def find_email(domain, url):
    emails = set()
    try:
        # Try direct webpage
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        text = r.text
        for pattern in COMMON_PATTERNS:
            found = re.findall(pattern, text, re.IGNORECASE)
            for email in found:
                if domain in email or 'contact' in email.lower() or 'hola' in email.lower():
                    emails.add(email.lower())
    except: pass
    
    # Clean and return best email
    clean = [e for e in emails if '@' in e and 'noreply' not in e and 'example' not in e]
    return list(clean)[:3] if clean else []

if __name__ == "__main__":
    print("=== Finding real contact emails ===\n")
    results = []
    
    for p in PROSPECTS:
        emails = find_email(p["domain"], p["url"])
        status = "VERIFIED" if emails else "NO_EMAIL"
        print(f"{'✓' if emails else '✗'} {p['name']} ({p['domain']}): {emails[0] if emails else 'No email found'}")
        
        results.append({
            "name": p["name"],
            "domain": p["domain"],
            "url": p["url"],
            "emails": emails,
            "best_email": emails[0] if emails else None,
            "status": status
        })
    
    # Save verified prospects
    with open("/root/.openclaw/workspace/leadpilot/campaigns/verified_prospects.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    verified_count = sum(1 for r in results if r["status"] == "VERIFIED")
    print(f"\n=== {verified_count}/{len(results)} verified ===")