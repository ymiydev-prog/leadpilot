#!/bin/bash
# Jaime Daily Trading Simulation
# Runs at 09:00 UTC daily

cd /root/.openclaw/workspace
python3 jaime_simulation.py

# Log completion
echo "$(date -u '+%Y-%m-%d %H:%M:%S') - Jaime simulation completed" >> /var/log/jaime_daily.log