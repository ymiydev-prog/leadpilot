#!/bin/bash
cd /root/.openclaw/workspace/leadpilot/backend
export $(cat .env | xargs)
exec python3 main.py >> /tmp/lp_service.log 2>&1