#!/usr/bin/env python3
"""Generate prospect list for LeadPilot outreach"""
import sys
import json
sys.path.insert(0, '/root/.openclaw/workspace/leadpilot/backend/sources')
from scraper_worker import run_search

queries = [
    ("agencia marketing digital", "Madrid España"),
    ("consultora marketing", "Barcelona España"),
    ("agencia publicidad digital", "Madrid España"),
    ("empresa servicios B2B", "España"),
    ("digital agency Spain", "Madrid Barcelona"),
]

prospects = []
seen = set()

for query, location in queries:
    try:
        leads = run_search(query, location, 12)
        for lead in leads:
            domain = lead.get('domain', '')
            if domain and domain not in seen:
                seen.add(domain)
                prospects.append({
                    "name": lead.get('name', '')[:100],
                    "domain": domain,
                    "url": lead.get('url', ''),
                    "email": lead.get('email', ''),
                    "phone": lead.get('phone', ''),
                    "location": location,
                    "status": "cold"
                })
        print(f"Query '{query[:30]}...': {len(leads)} leads")
    except Exception as e:
        print(f"Error '{query[:20]}': {e}")

# Limit to 50
prospects = prospects[:50]

with open('/root/.openclaw/workspace/leadpilot/campaigns/prospects_2026-04-12.json', 'w') as f:
    json.dump(prospects, f, indent=2, ensure_ascii=False)

print(f"\nTotal unique prospects: {len(prospects)}")
for p in prospects[:5]:
    print(f"  - {p['name'][:50]} | {p['domain']}")