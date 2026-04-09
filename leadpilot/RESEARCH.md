# LeadPilot - Research & Roadmap 2026

## Mercado
- TAM: $9B global para 2027
- Crecimiento: 15-20% anual
- España: €200M+ oportunidad

## Competencia Directa
| Herramienta | Precio | Diferenciador |
|-------------|--------|---------------|
| Apollo.io | $39/mo | 200M+ contactos, sequences |
| ZoomInfo | $999/mo | Enterprise, precisión alta |
| Hunter.io | $49/mo | Domain search, verifier |
| Cognism | $200/mo | GDPR compliant |

## Nuestro Posicionamiento
- **Precio:** Más barato que Apollo ($29 vs $39)
- **Nicho:** España + Europa (GDPR compliant)
- **Diferenciador:** 完全 autopiloto (búsqueda + email automático)

## Feature Roadmap Prioridad Alta

### Fase 1 (AHORA)
- [ ] Email warmup system (propio dominio)
- [ ] SPF/DKIM/DMARC para dominios cliente
- [ ] Sequences/automations (enviar follow-ups)
- [ ] Chrome extension

### Fase 2 (Pronta)
- [ ] LinkedIn profile enrichment
- [ ] CRM integrations (HubSpot, Salesforce)
- [ ] API access para developers
- [ ] Email verifier integrado

### Fase 3 (MVP completo)
- [ ] White-label option
- [ ] Multi-user/team features
- [ ] A/B testing emails
- [ ] Predictive analytics

## Nichos Target (orden de potencial)
1. **Agencias marketing digital** - churn alto, necesitan outbound constante
2. **SaaS B2B** - MRR bajo, viven de outbound
3. **Recruitment/Headhunters** - buscan candidatos, no leads
4. **Consultoras IT** - proposals constant
5. **Real estate comercial** - comisiones altas, Leads不值钱

## Deliverability Blueprint
```
1. Dominio propio (no @gmail.com)
2. MX records válidos
3. SPF record: include:sendgrid.net
4. DKIM: TXT record desde provider
5. DMARC: policy=quarantine
6. Warmup: 10 emails/día semana 1, +10/semana
7. Límite frío: 100-200/día máximo
8. Unsubscribe automático
9. No reply-tracking pixels (spam trigger)
```

## Email Templates que Convierten (Gong research)
1. **Short & sweet:** "XYZ me dijo que..."
2. **Pregunta abierta:** "¿Cómo están manejando...?"
3. **Value prop:** "Ayudamos a X a hacer Y"
4. **Mutual connection:** "Vi que trabajamos con Z"

## Pricing Strategy
- Free: 10 leads, 50 emails (probar)
- Starter: $29/mo - 100 leads, 500 emails (principal)
- Pro: $79/mo - 500 leads, 2000 emails
- Business: $199/mo - ilimitado + white-label

## Growth Tactics
1. **LinkedIn organic** - compartir case studies
2. **Cold email outbound** - 100 emails/día
3. **Product Hunt launch**
4. **G2/Capterra reviews**
5. **Partner with agencies**
6. **Content marketing** - blog de outreach

## Success Metrics
- MRR target mes 3: $500
- MRR target mes 6: $3000
- MRR target mes 12: $15000
- Churn target: <5%/mes
