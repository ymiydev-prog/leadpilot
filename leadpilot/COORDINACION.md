# Hermes ↔️ YhasClaw - Coordinación LeadPilot

**Creado:** 2026-04-17 17:42

---

## Sistema de Comunicación

### Archivos Compartidos
| Dirección | Archivo |
|-----------|---------|
| Hermes → YhasClaw | `/root/.shared/hermes_to_openclaw.json` |
| YhasClaw → Hermes | `/root/.shared/openclaw_to_hermes.json` |
| YhasClaw → Hermes (legacy) | `/root/.shared/yhastohermes.json` |
| Hermes → YhasClaw (legacy) | `/root/.shared/hermes_message.json` |

### Dashboard
http://88.223.95.118:8080/team_conversation.html

### Scripts Activos
- `yhas_check.sh`: Watcher inbox Hermes (cada 5s)
- `watch_shared.sh`: Watcher multi-archivo (cada 3s)

---

## División de Trabajo

### Hermes 🔮 (Estrategia)
- Análisis de código
- Definir soluciones exactas
- Revisar código implementado
- Dar líneas de código específicas

### YhasClaw 🐾 (Ejecución)
- Implementar fixes en filesystem
- Ejecutar comandos
- Hacer deploy de cambios
- Tests y validación

---

## Prioridad Actual

1. **Stripe Webhook** - CRÍTICO (bloquea pagos)
2. **verify_pw()** - Fix o eliminar
3. **Credenciales** - Mover a .env
4. **URLs Frontend** - Corregir

---

## Comandos Útiles

```bash
# Pull latest from GitHub
cd /root/.openclaw/workspace/leadpilot && git fetch origin && git pull

# Deploy backend
cd /root/.openclaw/workspace/leadpilot && ./backend/start.sh

# Check logs
tail -f /root/.openclaw/workspace/leadpilot/logs/*.log
```

---

## Repositorios

- **LeadPilot:** https://github.com/ymiydev-prog/leadpilot.git
- **Vault:** https://github.com/ymiydev-prog/VaultYhasClaw.git
