#!/bin/bash
cd /root/.openclaw/workspace/leadpilot/backend
python3 main.py >> /tmp/lp_server.log 2>&1 &
echo "Started PID: $!"
sleep 3
ss -tlnp | grep 8083