# MEMORY.md - Long-Term Memory

## Sistema YhasClaw - Estado Actual

**Última actualización:** 2026-04-13 13:20 UTC

---

## 🖥️ Servicios Activos

| Servicio | Puerto | Estado | Descripción |
|----------|--------|--------|-------------|
| Nginx | 8080 | ✅ | Dashboard v7 |
| LobsterBoard | 8081 | ✅ | Dashboard alternativo |
| LeadPilot Front | 8082 | ✅ | Landing + Dashboard |
| LeadPilot API | 8083 | ✅ | FastAPI (systemd) |
| OpenClaw Gateway | 18789 | ✅ | Core |
| YhasClaw Signals | - | ✅ | systemd |

---

## 💼 LeadPilot.es - PROYECTO PRINCIPAL

**Dominio:** leadpilot.es (pendiente registro €12)
**Estado:** MVP funcionando
**URL:** http://88.223.95.118:8082/

### Stack:
- Frontend: HTML/CSS/JS en `/var/www/html/leadpilot/`
- Backend: FastAPI en `/root/.openclaw/workspace/leadpilot/backend/main.py`
- Scraper: Firecrawl API (datos REALES) en `scraper.py`
- Service: `/etc/systemd/system/leadpilot.service`
- Nginx: `/etc/nginx/sites-available/leadpilot`
- Leads: `/root/.openclaw/workspace/leadpilot/data/leads.json`

### API Key Firecrawl:
`fc-7d9a7bd9c81346dfbfba5c7d55743bd5`

### Endpoints (v1.0):
- Auth: register, login, user info
- Leads: search (con límites), list, export CSV, delete
- Emails: generate (3 tonos), send real, track opens
- Campañas: create, list, send bulk
- Planes: list, upgrade
- Analytics: stats, sent emails list

### Modelo:
- Free: 10 leads/mes (€0)
- Starter: 100 leads/mes (€29)
- Pro: 500 leads/mes (€79)
- Business: ilimitado (€149)

---

## 🤖 ARIA - Investigador

**Script:** `/root/.openclaw/workspace/agents/aria_real_research.py`
**Cron:** 07:00 UTC diario
**Email destino:** ymiy2021@gmail.com
**⚠️ USA web_search REAL - nunca datos simulados**
**Trends:** `/root/.openclaw/workspace/reports/trends_2026-04-08.json`

---

## 🐦 Twitter/Elon

**Cuenta:** @yhas1984
**Horarios:** Lunes 09:00, Miércoles 10:00, Viernes 09:00 UTC
**⚠️ NUNCA publicar sin aprobación del Jefe**
**Reglas:** `/root/.openclaw/workspace/twitter/ELON_RULES.md`
**Auto-aprobación:** ZARA score ≥7/10

---

## 📅 Cron Jobs

| Nombre | Horario | Script |
|--------|---------|--------|
| ARIA Daily | 07:00 UTC | `scripts/aria_daily_cron.sh` |
| Dashboard Report | 09:00 UTC | `scripts/dashboard_report.sh` |
| Status Engine | cada 1 min | `run_status.sh` |
| Jaime Dashboard | cada 15 min | `update_jaime_dashboard_real.py` |

---

## 💹 Trading/Jaime

**Network:** Bybit Mainnet
**Paper:** YhasClawTest en Bybit Testnet
**Skills:** autonomous-trading-system, trading-signal, skill-trading-journal

---

## 🔑 Credenciales

| Servicio | Estado |
|----------|--------|
| OpenAI API | ✅ |
| Bybit API | ✅ Mainnet |
| Twitter OAuth | ✅ Full Access |
| Telegram Bot | ✅ |
| Firecrawl | ✅ |
| Gmail SMTP | ✅ |
| InsForge MCP | ✅ Configurado |

---

## ⚠️ REGLAS CRÍTICAS
### Stripe Webhook
- Endpoint: https://webhook.leadpilot.es/api/stripe/webhook
- Secret: whsec_C722s0MbWQudSGqDBf53vaWhn15HKDNd
- Eventos: checkout.session.completed

### 1. NUNCA SIMULAR DATOS
Todo debe ser real: web_search, fuentes verificables, precios reales.
Si no tengo acceso, buscarlo o indicar que no está disponible.

### 2. NUNCA PUBLICAR SIN APROBACIÓN
Twitter: solo con ZARA score ≥7 o aprobación manual del Jefe.

### 3. Nginx timeout
LeadPilot scraper tarda ~20s. Nginx config: proxy_read_timeout 60s.

### 4. Python scripts en OpenClaw
Usar shell wrappers para scripts complejos:
```
python3 script.py arg1 arg2 → bash wrapper.sh arg1 arg2
```

### 5. Dashboard persistence
Leads se guardan en JSON. API sirve `/api/leads/list`. Dashboard carga automáticamente.

---

## 📁 Archivos Importantes

```
/root/.openclaw/workspace/
├── MEMORY.md                    (este archivo)
├── SOUL.md                      (personalidad)
├── AGENTS.md                    (protocolos)
├── TOOLS.md                     (config herramientas)
├── memory/2026-04-08.md         (log de hoy)
├── leadpilot/                   (proyecto principal)
├── agents/aria_real_research.py (investigador)
├── twitter/                     (Elon rules, threads)
├── scripts/                     (cron scripts)
└── reports/                     (ARIA reports)
```

---

*YhasClaw v2026.4.8 - LeadPilot Edition* 🐾
## InsForge MCP - Base de datos

### Configuración
```json
{
  "mcpServers": {
    "insforge": {
      "command": "npx",
      "args": ["-y", "@insforge/mcp@latest"],
      "env": {
        "API_KEY": "ik_35c9fe063dc416d6bb3a636dc44b067c",
        "API_BASE_URL": "https://nv96hw8d.eu-central.insforge.app"
      }
    }
  }
}
```

### Comandos
```bash
mcporter list insforge --schema   # Ver herramientas
mcporter call insforge.run-raw-sql query="SELECT * FROM plans"
```

### Tablas
- `users`, `leads`, `campaigns`, `emails`, `plans`, `stripe_payments`

## Email Sistema LeadPilot

### Cuenta SMTP
- Email: yhasvenezuela@gmail.com
- Configurado para enviar DESDE: contacto@leadpilot.es
- Puerto: 587 con STARTTLS
- Función: send_email() en main.py

### Base de datos
- InsForge: nv96hw8d.eu-central.insforge.app
- API Key: ik_35c9fe063dc416d6bb3a636dc44b067c
- Tablas: users, leads, campaigns

### Regla CRÍTICA
- NUNCA usar datos simulados
- TODO en InsForge

## GitHub

### Repositorio
- **LeadPilot:** https://github.com/ymiydev-prog/leadpilot.git
- Token guardado en `~/.git-credentials`
