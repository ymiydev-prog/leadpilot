# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## TTS (Text-to-Speech)

### OpenAI TTS Configuration (GRATIS)

- **API Key**: Configured in `~/.openclaw/openclaw.json` (same as Whisper)
- **Default Voice**: `onyx` - Voz masculina profunda
- **Model**: `tts-1` - Rápido y económico

### Voces Disponibles

| Voice | Descripción |
|-------|-------------|
| `onyx` | Masculina profunda (activa) |
| `echo` | Masculina |
| `nova` | Femenina |
| `shimmer` | Femenina suave |
| `fable` | Narrativa |
| `alloy` | Neutral |

### To Generate Audio

```bash
curl -X POST "https://api.openai.com/v1/audio/speech" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "Tu mensaje aquí", "voice": "onyx"}' \
  --output output.mp3
```

## STT (Speech-to-Text)

Uses OpenAI Whisper API. Configured in `~/.openclaw/openclaw.json` under `skills.entries.openai-whisper-api.apiKey`.

### To Transcribe Audio

```bash
curl -sS https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/path/to/audio.ogg" \
  -F "model=whisper-1" \
  -F "language=es"
```

---

Add whatever helps you do your job. This is your cheat sheet.
## Email (LeadPilot SMTP)

### Cuenta principal
- Email: yhasvenezuela@gmail.com
- Contraseña: isrwrzraxlkwrclo (funciona)
- Configurado como: contacto@leadpilot.es

### Configuración SMTP
- Host: smtp.gmail.com
- Puerto: 587 (STARTTLS)
- Usuario: yhasvenezuela@gmail.com

### En el código
- Backend: /root/.openclaw/workspace/leadpilot/backend/main.py
- Función: send_email(to_email, subject, body_html)

### Cuenta principal
- **Email:** yhasvenezuela@gmail.com
- **Contraseña App:** (pendiente - usar con SMTP puerto 587 + STARTTLS)
- **Desde:** contacto@leadpilot.es (configurado en Gmail)

### Configuración SMTP
- Host: smtp.gmail.com
- Puerto: 587 (STARTTLS)
- Usuario: yhasvenezuela@gmail.com
- Usar: STARTTLS (no SSL directo)

### En el código
- Backend: /root/.openclaw/workspace/leadpilot/backend/main.py
- Función: send_email(to_email, subject, body_html)
