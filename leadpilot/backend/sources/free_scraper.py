#!/usr/bin/env python3
"""LeadPilot scraper wrapper"""
import subprocess
import sys
import json

WORKER = "/root/.openclaw/workspace/leadpilot/backend/sources/scraper_worker.py"

def search_leads(query, location="Madrid", max_results=20):
    try:
        result = subprocess.run(
            ["python3", WORKER, query, location, str(max_results)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        return []
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('query', default='restaurantes')
    parser.add_argument('location', default='Madrid')
    parser.add_argument('max_results', type=int, default=20)
    args = parser.parse_args()
    
    leads = search_leads(args.query, args.location, args.max_results)
    print(json.dumps(leads, ensure_ascii=False, indent=2))
