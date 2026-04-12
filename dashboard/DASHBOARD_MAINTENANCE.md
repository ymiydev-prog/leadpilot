# Dashboard Maintenance Guide - dev1 & dev2

## Responsabilidades

### dev1 (Frontend)
- Mantener `dashboard.html` actualizado
- Añadir nuevos agentes cuando se creen
- Mejorar diseño y UX
- Asegurar responsive design
- Animaciones y transiciones

### dev2 (Backend)
- Mantener `update_dashboard.sh` ejecutándose
- Actualizar `signals.json` con datos de trading
- Actualizar `data.json` con métricas
- Logs de actualización
- APIs y endpoints

## Archivos Clave

```
/var/www/html/
├── dashboard.html        # UI principal (dev1)
├── signals.json          # Datos de trading (dev2)
├── data.json             # Métricas del sistema (dev2)
├── update_signals.sh     # Script de señales (dev2)
└── update_dashboard.sh   # Script principal (dev2)
```

## Comandos Útiles

### Actualizar manualmente
```bash
/var/www/html/update_dashboard.sh
```

### Ver logs
```bash
tail -f /tmp/dashboard_update.log
tail -f /tmp/signals_log.txt
```

### Verificar crons
```bash
crontab -l
```

## Checklist Diario

- [ ] Dashboard carga correctamente
- [ ] Señales se actualizan cada 30s
- [ ] Todos los agentes aparecen
- [ ] Métricas son correctas
- [ ] Logs sin errores

## Agregar Nuevo Agente

1. Añadir a `data.json`:
```json
{
  "name": "NuevoAgente",
  "role": "Rol del agente",
  "status": "online",
  "color": "#hexcolor"
}
```

2. Actualizar `dashboard.html`:
- Añadir color CSS: `.agent-nuevoagente { border-left-color: #hexcolor; }`
- Añadir badge: `<div class="agent-badge nuevoagente">🆕 NuevoAgente</div>`
- Añadir card con tareas

3. Actualizar memoria en `memory/YYYY-MM-DD.md`

## Contactar

Si hay problemas con el dashboard:
- Frontend/UI → dev1
- Backend/Datos/APIs → dev2
- Coordinación general → YhasClaw