#!/usr/bin/env python3
"""
LeadPilot - Search Queue Processor
Procesa búsquedas pendientes usando web_search real
"""

import json
import os
import sys

QUEUE_FILE = "/root/.openclaw/workspace/leadpilot/data/search_queue.json"

def get_pending_searches():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return {}

def mark_processed(search_id):
    data = get_pending_searches()
    if search_id in data:
        data[search_id]["status"] = "processed"
        with open(QUEUE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    searches = get_pending_searches()
    pending = {k: v for k, v in searches.items() if v.get("status") == "pending"}
    
    if not pending:
        print("No hay búsquedas pendientes")
        sys.exit(0)
    
    for sid, sdata in pending.items():
        print(f"Pendiente: {sdata['query']} en {sdata['location']} (ID: {sid})")