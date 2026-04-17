# LeadPilot - Análisis de Bugs y Mejoras

**Fecha:** 2026-04-17  
**Analizado por:** Hermes + YhasClaw

---

## 🔴 Bugs Críticos (Bloquean Monetización)

### 1. Stripe Webhook Roto
**Archivo:** `backend/main_insforge.py`  
**Problema:** Variable `users` indefinida en webhook handler  
**Impacto:** Pagos no se procesan, upgrades no aplican

### 2. verify_pw() No Existe
**Problema:** Se llama `verify_pw()` pero no está definida en el código  
**Impacto:** Login falla

### 3. Credenciales Hardcodeadas
**Archivos:** `backend/main_insforge.py`, `insforge/credentials.json`  
**Problema:** SMTP, JWT_SECRET, API keys en código fuente  
**Impacto:** Security risk

### 4. URLs Frontend Incorrectas
**Problema:** Frontend apunta a URLs de desarrollo en vez de producción  
**Impacto:** Dashboard no conecta con API

---

## ⏳ Pendiente (según Launch Plan)

| Feature | Prioridad |
|---------|-----------|
| Email warmup (SPF/DKIM/DMARC) | 🔴 Alta |
| Email templates (bienvenida/confirmación) | 🔴 Alta |
| Analytics (Umami/Plausible) | 🟡 Media |
| Social proof (testimonios, case studies) | 🟡 Media |
| Demo video | 🟡 Media |
| Customer support email | 🟡 Media |
| Pricing page optimization | 🟢 Baja |

---

## 📁 Estructura Backend (GitHub)
```
backend/
├── main_insforge.py      # API principal (831 líneas)
├── run_server.py         # Server runner
├── scraper.py            # Firecrawl integration
├── chat_bridge.py        # OpenClaw Telegram bridge
├── search_leads.py       # Lead search logic
├── schema.sql            # DB schema
└── start.sh              # Startup script
```

## 🔗 URLs Actuales
- **Frontend:** https://leadpilot.es
- **API:** https://nv96hw8d.functions.insforge.app
- **Dashboard:** https://leadpilot.es/dashboard
- **Database:** https://nv96hw8d.eu-central.insforge.app

## 📊 Stats
- **Usuarios:** 3 (demo@leadpilot.es, y.h.a.s1984@gmail.com, ymiyo2021@gmail.com)
- **Planes:** Free (10 leads/mes), Starter (€29), Pro (€79), Business (€149)

---

## ✅ Completado
- [x] Landing page profesional
- [x] Dashboard con auth
- [x] Stripe payment integration
- [x] Privacy Policy + Terms
- [x] Open Graph tags
- [x] Mobile responsive
- [x] Favicon

## 🔧 Próximos Pasos
1. Fix Stripe webhook (Hermes define, YhasClaw ejecuta)
2. Fix verify_pw()
3. Mover credenciales a .env
4. Corregir URLs frontend
5. Email warmup setup
