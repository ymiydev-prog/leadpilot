#!/bin/bash
cd /root/.openclaw/workspace/leadpilot
source venv/bin/activate

python3 << 'PYEOF'
import sys
sys.path.insert(0, 'backend/sources')
from scraper_worker import run_search
import json
import requests
import re
import time

EXTRA_PROSPECTS = [
    {"name": "Optimoclick", "domain": "optimoclick.com", "url": "https://www.optimoclick.com"},
    {"name": "Factoría Proyectos", "domain": "factoriadeproyectos.com", "url": "https://www.factoriadeproyectos.com"},
    {"name": "Tresce", "domain": "tresce.com", "url": "https://www.tresce.com"},
    {"name": "Artic Agency", "domain": "articagency.com", "url": "https://articagency.com"},
    {"name": "Karmina", "domain": "agenciakarmina.com", "url": "https://www.agenciakarmina.com"},
    {"name": "Kreaset", "domain": "kreaset.com", "url": "https://kreaset.com"},
    {"name": "Team Lewis", "domain": "teamlewis.com", "url": "https://www.teamlewis.com"},
    {"name": "Digency", "domain": "digency.es", "url": "https://digency.es"},
    {"name": "EYClick", "domain": "eyclick.com", "url": "https://www.eyclick.com"},
    {"name": "N3XTwave", "domain": "n3xtwave.com", "url": "https://www.n3xtwave.com"},
]

def find_email(domain, url):
    emails = set()
    try:
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        for pattern in [r'[\w\.-]+@[\w\.-]+\.\w+']:
            found = re.findall(pattern, r.text, re.IGNORECASE)
            for email in found:
                if '@' in email and 'noreply' not in email.lower() and 'example' not in email.lower():
                    emails.add(email.lower())
    except: pass
    return list(emails)[:3] if emails else []

print("=== Verificando +10 prospects ===")
results = []
for p in EXTRA_PROSPECTS:
    emails = find_email(p["domain"], p["url"])
    if emails:
        print(f"✓ {p['name']}: {emails[0]}")
        results.append({"name": p["name"], "domain": p["domain"], "email": emails[0], "status": "verified"})
    else:
        print(f"✗ {p['name']}: No email")
    
    with open('/root/.openclaw/workspace/leadpilot/campaigns/verified_batch2.json', 'w') as f:
        json.dump(results, f, indent=2)
    time.sleep(1)

print(f"\n=== {len(results)}/{len(EXTRA_PROSPECTS)} verificados ===")
PYEOF