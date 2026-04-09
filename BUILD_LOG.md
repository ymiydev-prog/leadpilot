# LeadPilot - Build Log
## Cada mejora queda registrada aquí

---

### [2026-04-08 12:17] - API v1.0 completa
**Estado:** ✅ COMPLETADO
**Descripción:** SaaS completo funcional con:
- ✅ Límites por plan (free/starter/pro/business)
- ✅ Sistema de usuarios con autenticación
- ✅ Envío de emails reales vía SMTP Gmail
- ✅ Pixel tracking de aperturas
- ✅ Sistema de campañas (crear/enviar/rastrear)
- ✅ Exportar leads a CSV
- ✅ Analytics con tasa de apertura
- ✅ Upgrade de planes
- ✅ Reset mensual de uso

---

## ENDPOINTS

### Auth
- `POST /api/register` - Registro
- `POST /api/login` - Login
- `GET /api/user/{email}` - Info usuario

### Leads
- `POST /api/leads/search` - Buscar (con límites plan)
- `GET /api/leads/list` - Listar leads
- `GET /api/leads/export` - Exportar CSV
- `DELETE /api/leads/{id}` - Eliminar

### Emails
- `POST /api/emails/generate` - Generar con IA (3 tonos)
- `POST /api/emails/send` - Enviar email real
- `GET /api/track/{id}` - Pixel tracking
- `GET /api/emails/sent` - Lista enviados

### Campañas
- `POST /api/campaigns/create` - Crear campaña
- `GET /api/campaigns` - Listar campañas
- `POST /api/campaigns/{id}/send` - Enviar campaña

### Planes
- `GET /api/plans` - Ver planes
- `POST /api/plans/upgrade` - Upgrade

### Analytics
- `GET /api/stats` - Estadísticas

---

## PLANES

| Plan | Leads/mes | Emails/mes | Campañas | Precio |
|------|-----------|------------|----------|--------|
| Free | 10 | 50 | 1 | €0 |
| Starter | 100 | 500 | 10 | €29 |
| Pro | 500 | 2000 | ∞ | €79 |
| Business | ∞ | ∞ | ∞ | €149 |
