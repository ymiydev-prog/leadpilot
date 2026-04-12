# LeadPilot - Outreach Script

## Secuencia Cold Email (3 emails por prospect)

### Día 1 - Email Inicial
**Objetivo:** Generar curiosidad, crear valor
**Timing:** Martes o miércoles (evitar lunes)
**Expectativa:** 5-10% respuesta

Ver email_template.md para versiones.

### Día 3 - Follow Up (si no hay respuesta)
**Asunto:** Re: [asunto email 1]

Hola [Nombre],

Just following up on my previous email. I know you're busy - just wanted to make sure you saw it.

If now is not a good time, just let me know and I'll stop following up. But if you're curious about saving time on prospecting, happy to show you how it works in 10 minutes.

No pressure.

Saludos,
Carlos

### Día 7 - Último intento
**Asunto:** [Empresa] - quick question

Hola [Nombre],

Last email from me (I promise). 

I've been helping agencies like [competitor or similar company] find 50-100 new leads per month without spending hours on research.

If you're interested, here's a quick demo: https://leadpilot.es/dashboard

If not, totally understand. Just want to make sure you had the option.

Best,
Carlos

---

## Objection Handling

### "No tengo tiempo"
> Entiendo. ¿Cuánto tiempo te toma actualmente encontrar prospectos? probablemente podemos en 5 minutos mostrarte algo que te ahorre horas.

### "Ya tengo un sistema"
> Genial! Cuéntame qué estás usando. Si ya tienes algo funcionando, puede que LeadPilot complemente tu proceso actual. ¿Podemos hacer una prueba?

### "No creo que funcione para mi"
> Entiendo tu escepticismo. Por eso ofrecemos prueba gratuita. Sin compromiso. Si no funciona, no pierdes nada.

### "Envíame más información"
> Por supuesto! El mejor lugar es nuestro dashboard: https://leadpilot.es/dashboard. Ahí puedes ver cómo funciona sin hablar conmigo. ¿Te parece?

---

## Tracking - Métricas a Medir

- Emails enviados
- Emails abiertos (open tracking)
- Respuestas
- Citas agendadas
- Conversiones a paid

## Scripts de Envío

Los scripts de envío masivo están en:
- /root/.openclaw/workspace/leadpilot/campaigns/send_campaign.py (pendiente crear)
- Usar API: POST /api/emails/send con {to_email, to_name, subject, body_html}

## Checklist antes de enviar

- [ ] Verificar que lista de prospectos esté limpia
- [ ] Personalizar cada email con nombre empresa
- [ ] Verificar tracking de opens activo
- [ ] Probar en 5 emails de test primero
- [ ] Revisar que no haya spam trigger words