#!/bin/bash
cd /root/.openclaw/workspace/leadpilot/backend
set -a
source ../.env 2>/dev/null || true
set +a
exec python3 main_insforge.py >> /tmp/lp_service.log 2>&1