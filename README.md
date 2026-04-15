# LeadPilot

B2B lead generation SaaS for the Spanish market.

## Stack
- Frontend: HTML/CSS/JS
- Backend: FastAPI (Python)
- Database: **Insforge** (https://nv96hw8d.eu-central.insforge.app)
- Scraper: Firecrawl API

## Setup
```bash
pip install fastapi uvicorn httpx pyjwt
cp .env.example .env  # completa las credenciales
python backend/main_insforge.py
```

## API
- http://localhost:8083/docs (Swagger)
- http://localhost:8083/ (health check)

## Database
Inicializar tablas en Insforge:
```bash
python backend/init_insforge.py
```
