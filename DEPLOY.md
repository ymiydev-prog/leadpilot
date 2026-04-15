# LeadPilot - Guía de Despliegue VPS

## Archivos modificados/creados

### Backend
- `backend/main_insforge.py` - API keys en variables de entorno, CORS fijo, endpoints corregidos
- `backend/scraper.py` - FIRECRAWL_API_KEY en entorno
- `backend/chat_bridge.py` - NUEVO: Puente entre Insforge y Telegram

### Frontend
- `index.html` - Widget chat con polling
- `dashboard.html` - Widget chat con polling
- `chat.html` - Widget chat con polling

### Config
- `.env` - Variables de entorno (creado)
- `.agents/skills/leadpilot/SKILL.md` - Skill para OpenClaw

### Database (Insforge)
- Tabla `chat_messages` - NUEVA

---

## Pasos de Despliegue

### 1. Sube los archivos al VPS

Desde tu máquina local:
```bash
rsync -avz --exclude='.git' --exclude='node_modules' \
  /home/yhas/Documents/YhasClaw/leadpilot/ \
  root@TU_IP_VPS:/root/.openclaw/workspace/leadpilot/
```

### 2. Configura el archivo .env en el VPS

En el VPS, edita `/root/.openclaw/workspace/leadpilot/.env`:
```bash
cd /root/.openclaw/workspace/leadpilot
nano .env
```

Contenido:
```env
INSFORGE_URL=https://nv96hw8d.eu-central.insforge.app
INSFORGE_API_KEY=ik_35c9fe063dc416d6bb3a636dc44b067c
JWT_SECRET=leadpilot_jwt_secret_2026_change_this
SMTP_USER=yhasvenezuela@gmail.com
SMTP_PASS=ificahhweilgwfjb
STRIPE_SECRET_KEY=mk_1TK3iM2LcCApvvprJwCjna0Y
STRIPE_PUBLISHABLE_KEY=pk_live_51RQYF72LcCApvvprRWBYh3wt0wmio98z6ufWgcBSED16Mgjhq3Jt3XBEsWEfpaDVDiBQOZplXA4d54nVcq3IuaPU00yD6wvlOZ
STRIPE_WEBHOOK_SECRET=whsec_C722s0MbWQudSGqDBf53vaWhn15HKDNd
FIRECRAWL_API_KEY=fc-7d9a7bd9c81346dfbfba5c7d55743bd5
TELEGRAM_BOT_TOKEN=8457045397:AAES3i_PyzqaAy68SmUkrLZelWJoYSW5ZnA
TELEGRAM_ADMIN_CHAT_ID=TU_TELEGRAM_USER_ID
```

### 3. Obtén tu Telegram Chat ID

1. Habla con @userinfobot en Telegram
2. Te dirá tu ID (número)

### 4. Instala dependencias del backend

```bash
cd /root/.openclaw/workspace/leadpilot/backend
pip install fastapi uvicorn httpx pyjwt python-dotenv
```

### 5. Reinicia el backend

```bash
cd /root/.openclaw/workspace/leadpilot/backend
pkill -f main_insforge.py
nohup python main_insforge.py > /var/log/leadpilot.log 2>&1 &
```

Verifica que está corriendo:
```bash
curl http://localhost:8083/
```

### 6. Configura OpenClaw con el segundo bot

```bash
# Verifica que OpenClaw está instalado
openclaw --version

# Configura Telegram
openclaw config set channels.telegram.enabled true
openclaw config set channels.telegram.botToken "8457045397:AAES3i_PyzqaAy68SmUkrLZelWJoYSW5ZnA"
openclaw config set channels.telegram.dmPolicy "open"
openclaw config set channels.telegram.allowFrom '["*"]'

# Copia el skill de LeadPilot
cp -r /root/.openclaw/workspace/leadpilot/.agents/skills/leadpilot ~/.openclaw/skills/

# Reinicia el gateway de OpenClaw
openclaw gateway restart
```

### 7. Verifica OpenClaw

```bash
openclaw channels status
openclaw logs --follow
```

Envía un mensaje de prueba al bot `@TuBotLeadPilot` en Telegram.

### 8. Inicia el chat bridge (opcional, para web → Telegram)

```bash
cd /root/.openclaw/workspace/leadpilot/backend
nohup python chat_bridge.py > /var/log/chat_bridge.log 2>&1 &
```

---

## Estructura de Mensajes

### Flujo Web → Telegram
1. Usuario escribe en widget web
2. `/api/contact` guarda en `chat_messages` (status=pending)
3. `chat_bridge.py` detecta mensaje pendiente
4. Envía notificación a Telegram (admin)
5. OpenClaw procesa y responde
6. Widget polls `/api/contact/responses` cada 3s
7. Respuesta se muestra al usuario

### Flujo Telegram Directo
1. Usuario envía mensaje a bot de Telegram
2. OpenClaw recibe y procesa con el skill de LeadPilot
3. Responde directamente en Telegram

---

## Verificación

### Test API
```bash
curl -X POST http://localhost:8083/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","message":"Hola","source":"test"}'
```

### Test Logs
```bash
tail -f /var/log/leadpilot.log
tail -f /var/log/chat_bridge.log
```

### Test OpenClaw
```bash
openclaw channels status
openclaw message send --channel telegram --target TU_CHAT_ID --message "Test"
```

---

## Troubleshooting

### OpenClaw no responde en Telegram
1. Verifica el token: `openclaw config get channels.telegram.botToken`
2. Revisa logs: `openclaw logs --follow`
3. Prueba el bot directamente en Telegram

### Widget no recibe respuestas
1. Verifica que el backend está corriendo: `curl http://localhost:8083/api/contact/responses`
2. Revisa que `chat_messages` tiene registros: `npx @insforge/cli db query "SELECT * FROM chat_messages LIMIT 5;"`

### CORS errors
Verifica que el backend tiene las URLs correctas en `allow_origins`:
```python
allow_origins=["https://leadpilot.es", "https://www.leadpilot.es"]
```

---

## Comandos Rápidos

```bash
# Reiniciar backend
pkill -f main_insforge.py && cd /root/.openclaw/workspace/leadpilot/backend && nohup python main_insforge.py &

# Ver logs backend
tail -100 /var/log/leadpilot.log

# Reiniciar OpenClaw
openclaw gateway restart

# Ver estado OpenClaw
openclaw channels status

# Test API
curl http://localhost:8083/
```
