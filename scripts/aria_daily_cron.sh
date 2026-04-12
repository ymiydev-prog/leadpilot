#!/bin/bash
# ARIA - Daily Research Cron Job
# Ejecutar a las 07:00 UTC cada dia

cd /root/.openclaw/workspace/agents
python3 aria_real_research.py >> /root/.openclaw/workspace/logs/aria_daily.log 2>&1
