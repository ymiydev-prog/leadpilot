#!/bin/bash
# Elon - Script de Cron para Twitter
# Ejecutar: Lunes 9:00, Miércoles 10:00, Viernes 9:00 UTC

cd /root/.openclaw/workspace/twitter
python3 auto_publisher.py >> /root/.openclaw/workspace/twitter/elon_cron.log 2>&1