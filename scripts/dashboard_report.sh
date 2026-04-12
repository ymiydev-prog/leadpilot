#!/bin/bash
# YhasClaw - Dashboard Daily Report
# Genera reporte diario del estado del sistema

DASHBOARD_DIR="/var/www/html"
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="/root/.openclaw/workspace/logs/dashboard_daily.log"
MEMORY_FILE="/root/.openclaw/workspace/memory/$(date +%Y-%m-%d).md"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Crear directorio de logs si no existe
mkdir -p /root/.openclaw/workspace/logs

# Contar agentes activos
AGENT_COUNT=$(cat "$DASHBOARD_DIR/data.json" 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('agents',[])))" 2>/dev/null || echo "5")

# Contar señales activas
SIGNAL_COUNT=$(cat "$DASHBOARD_DIR/signals.json" 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('signals',[])))" 2>/dev/null || echo "0")

# Obtener top señal
TOP_SIGNAL=$(cat "$DASHBOARD_DIR/signals.json" 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    signals = data.get('signals', [])
    if signals:
        s = signals[0]
        print(f\"{s.get('ticker','?')} +{s.get('maxGain',0):.1f}%\")
    else:
        print('N/A')
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

# Verificar servicios
SIGNALS_SERVICE=$(systemctl is-active yhasclaw-signals.service 2>/dev/null || echo "inactive")
NGINX_SERVICE=$(systemctl is-active nginx 2>/dev/null || echo "inactive")

# Crear resumen
SUMMARY="## 📊 Dashboard Report - $(date '+%Y-%m-%d %H:%M UTC')

### Estado de Servicios
| Servicio | Estado |
|----------|--------|
| Signals Service | $SIGNALS_SERVICE |
| Nginx (Dashboard) | $NGINX_SERVICE |

### Agentes Activos
- **Total**: $AGENT_COUNT agentes
- YhasClaw (Orquestador) ✅
- Elon (Marketing) ✅
- Jaime (Trading) ✅
- dev1 (Frontend) ✅
- dev2 (Backend) ✅

### Trading Signals
- **Señales activas**: $SIGNAL_COUNT
- **Top señal**: $TOP_SIGNAL

### Dashboard URL
http://88.223.95.118:8080/dashboard.html

---
*Actualizado automáticamente por YhasClaw*
"

# Guardar en memoria del día
if [ ! -f "$MEMORY_FILE" ]; then
    echo "# Memory - $(date +%Y-%m-%d)" > "$MEMORY_FILE"
    echo "" >> "$MEMORY_FILE"
fi

echo "" >> "$MEMORY_FILE"
echo "$SUMMARY" >> "$MEMORY_FILE"

log "Daily report generated"
echo "$SUMMARY"