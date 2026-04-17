"""
LeadPilot.es - Backend API v1.4
Full JWT Auth + Stripe Checkout + Plan Limits
Database: Insforge (https://nv96hw8d.eu-central.insforge.app)
"""
import os, json, hashlib, time, subprocess, uuid, smtplib, csv, io, re, httpx
import jwt
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://leadpilot.es", "https://www.leadpilot.es"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Insforge Configuration ───
INSFORGE_URL = os.environ.get("INSFORGE_URL")
INSFORGE_API_KEY = os.environ.get("INSFORGE_API_KEY")
if not INSFORGE_URL or not INSFORGE_API_KEY:
    raise RuntimeError("Missing INSFORGE_URL or INSFORGE_API_KEY environment variables")
INSFORGE_HEADERS = {
    "Authorization": f"Bearer {INSFORGE_API_KEY}",
    "Content-Type": "application/json"
}

# JWT & Security
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("Missing JWT_SECRET environment variable")
JWT_ALGO = "HS256"

# Stripe
STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# SMTP
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 465
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

# ─── Insforge Database Helpers (REST API) ───
async def insf_insert(table: str, data: dict) -> dict:
    """Insertar un registro en Insforge"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{INSFORGE_URL}/api/database/records/{table}",
            headers=INSFORGE_HEADERS,
            json=[data],  # Debe ser array
            params={"Prefer": "return=representation"},
            timeout=15
        )
        resp.raise_for_status()
        result = resp.json()
        return result[0] if result else data

async def insf_select(table: str, filters: dict = None, limit: int = 1000) -> list:
    """Consultar registros de Insforge"""
    async with httpx.AsyncClient() as client:
        params = {"limit": limit}
        if filters:
            for k, v in filters.items():
                params[k] = f"eq.{v}"
        resp = await client.get(
            f"{INSFORGE_URL}/api/database/records/{table}",
            headers=INSFORGE_HEADERS,
            params=params,
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()

async def insf_update(table: str, filter_field: str, filter_value: str, data: dict) -> list:
    """Actualizar registros en Insforge"""
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{INSFORGE_URL}/api/database/records/{table}",
            headers=INSFORGE_HEADERS,
            params={filter_field: f"eq.{filter_value}"},
            json=data,
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()

async def insf_delete(table: str, filter_field: str, filter_value: str) -> None:
    """Eliminar registros de Insforge"""
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{INSFORGE_URL}/api/database/records/{table}",
            headers=INSFORGE_HEADERS,
            params={filter_field: f"eq.{filter_value}"},
            timeout=15
        )
        resp.raise_for_status()

# ─── Auth Helpers ───
def hash_pw(pw: str) -> str:
    return hashlib.sha256((pw + JWT_SECRET).encode()).hexdigest()

def make_token(email: str) -> str:
    return jwt.encode(
        {"sub": email, "exp": (datetime.utcnow() + timedelta(days=30)).timestamp()},
        JWT_SECRET, algorithm=JWT_ALGO
    )

def verify_token(token_str: str) -> Optional[str]:
    try:
        return jwt.decode(token_str, JWT_SECRET, algorithms=[JWT_ALGO])["sub"]
    except Exception:
        return None

async def get_user_by_email(email: str) -> Optional[dict]:
    """Obtener usuario desde Insforge por email"""
    rows = await insf_select("users", {"email": email})
    return rows[0] if rows else None

async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Obtener usuario desde Insforge por ID"""
    rows = await insf_select("users", {"id": user_id})
    return rows[0] if rows else None

def get_current_user(req: Request) -> str:
    """Extraer email del JWT token"""
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "No token")
    email = verify_token(auth[7:])
    if not email:
        raise HTTPException(401, "Token inválido")
    return email

async def check_limit(email: str, resource: str, n: int = 1) -> bool:
    """Verificar límites del plan del usuario"""
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    # Resetear si cambio el mes
    current_month = datetime.now().strftime("%Y-%m")
    if user.get("usage_month") != current_month:
        await insf_update("users", "email", email, {
            "leads_used": 0, "emails_used": 0, "campaigns_used": 0,
            "usage_month": current_month
        })
        user["leads_used"] = 0
        user["emails_used"] = 0
        user["campaigns_used"] = 0
        user["usage_month"] = current_month
    plan_name = user.get("plan", "free")
    # Obtener limites desde la tabla plans
    plans = await insf_select("plans", {"id": plan_name})
    plan = plans[0] if plans else None
    if not plan:
        return True
    limit_field = f"{resource}s_limit" if resource != "emails" else "emails_limit"
    if resource == "campaigns":
        limit_field = "campaigns_limit"
    limit = plan.get(limit_field, -1)
    if limit == -1:
        return True
    return user.get(f"{resource}_used", 0) + n <= limit

async def inc_use(email: str, resource: str, n: int = 1):
    """Incrementar uso del recurso"""
    user = await get_user_by_email(email)
    if user:
        current = user.get(f"{resource}_used", 0) + n
        await insf_update("users", "email", email, {f"{resource}_used": current})

# ─── Models ───
class R(BaseModel): email: str; password: str; name: str = ""
class L(BaseModel): email: str; password: str
class S(BaseModel): query: str; location: str = "España"; max_results: int = 20
class EG(BaseModel): lead_name: str; lead_company: str = ""; lead_website: str = ""; tone: str = "profesional"
class ES(BaseModel): to_email: str; to_name: str; subject: str; body_html: str
class CC(BaseModel): name: str; subject: str; template: str; lead_ids: List[int] = []

# ─── Auth Endpoints ───
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@app.post("/api/register")
async def register(d: R):
    if not EMAIL_REGEX.match(d.email):
        raise HTTPException(400, "Email invalido")
    if len(d.password) < 6:
        raise HTTPException(400, "La contrasena debe tener minimo 6 caracteres")
    if len(d.name) < 2:
        raise HTTPException(400, "El nombre debe tener minimo 2 caracteres")
    existing = await get_user_by_email(d.email)
    if existing:
        raise HTTPException(400, "Email ya registrado")
    month = datetime.now().strftime("%Y-%m")
    user_data = {
        "id": str(uuid.uuid4()),
        "name": d.name,
        "email": d.email,
        "password": hash_pw(d.password),
        "plan": "free",
        "leads_used": 0,
        "emails_used": 0,
        "campaigns_used": 0,
        "usage_month": month,
        "created_at": datetime.utcnow().isoformat()
    }
    await insf_insert("users", user_data)
    return {
        "status": "ok",
        "token": make_token(d.email),
        "user": {"email": d.email, "name": d.name},
        "plan": "free",
        "limits": {"leads": 10, "emails": 50, "campaigns": 1}
    }

@app.post("/api/login")
async def login(d: L):
    user = await get_user_by_email(d.email)
    if not user or user["password"] != hash_pw(d.password):
        raise HTTPException(401, "Credenciales invalidas")
    plan = user.get("plan", "free")
    plans = await insf_select("plans", {"id": plan})
    plan_data = plans[0] if plans else {}
    return {
        "status": "ok",
        "token": make_token(d.email),
        "user": {"email": d.email, "name": user.get("name", "")},
        "plan": plan,
        "limits": {
            "leads": plan_data.get("leads_limit", 10),
            "emails": plan_data.get("emails_limit", 50),
            "campaigns": plan_data.get("campaigns_limit", 1)
        }
    }

@app.get("/api/user/me")
async def me(req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "No encontrado")
    safe_user = {k: v for k, v in user.items() if k != "password"}
    plan = user.get("plan", "free")
    plans = await insf_select("plans", {"id": plan})
    plan_data = plans[0] if plans else {}
    return {
        "user": safe_user,
        "limits": {
            "leads": plan_data.get("leads_limit", 10),
            "emails": plan_data.get("emails_limit", 50),
            "campaigns": plan_data.get("campaigns_limit", 1)
        }
    }

@app.put("/api/profile")
async def update_profile(req: Request, d: dict):
    email = get_current_user(req)
    if "name" in d:
        await insf_update("users", "email", email, {"name": d["name"]})
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "No encontrado")
    return {"status": "ok", "user": {k: v for k, v in user.items() if k != "password"}}

@app.post("/api/profile/password")
async def change_password(req: Request, d: dict):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "No encontrado")
    old = d.get("old_password", "")
    new_p = d.get("new_password", "")
    if not old or not new_p:
        raise HTTPException(400, "Faltan datos")
    if hash_pw(old) != user["password"]:
        raise HTTPException(400, "Contrasena actual incorrecta")
    if len(new_p) < 6:
        raise HTTPException(400, "Minimo 6 caracteres")
    await insf_update("users", "email", email, {"password": hash_pw(new_p)})
    return {"status": "ok"}

@app.get("/api/plans")
async def plans_endpoint():
    rows = await insf_select("plans")
    return {"plans": {r["id"]: r for r in rows}}

@app.post("/api/plans/upgrade")
async def upgrade(body: dict, req: Request):
    email = get_current_user(req)
    plan = body.get("plan")
    if not plan:
        raise HTTPException(400, "Plan invalido")
    plans = await insf_select("plans", {"id": plan})
    if not plans:
        raise HTTPException(400, "Plan no existe")
    await insf_update("users", "email", email, {"plan": plan})
    plan_data = plans[0]
    return {
        "status": "ok",
        "success": True,
        "plan": plan,
        "limits": {
            "leads": plan_data.get("leads_limit", -1),
            "emails": plan_data.get("emails_limit", -1),
            "campaigns": plan_data.get("campaigns_limit", -1)
        }
    }

# ─── Leads Endpoints ───
@app.post("/api/leads/search")
async def search_leads(d: S, req: Request):
    email = get_current_user(req)
    if not await check_limit(email, "leads"):
        raise HTTPException(403, "Limite de leads alcanzado. Upgrade tu plan.")
    try:
        r = subprocess.run(
            ["python3", "/root/.openclaw/workspace/leadpilot/backend/scraper.py",
             d.query, d.location, str(d.max_results)],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode == 0:
            leads = json.loads(r.stdout)
            filtered = [l for l in leads if l.get("email") or l.get("phone")]
            user = await get_user_by_email(email)
            search_data = {
                "user_id": user["id"],
                "query": d.query,
                "location": d.location,
                "leads": filtered,
                "created_at": datetime.utcnow().isoformat()
            }
            await insf_insert("searches", search_data)
            await inc_use(email, "leads", len(filtered))
            return {"status": "ok", "leads": filtered, "count": len(filtered)}
        raise HTTPException(500, f"Error: {r.stderr[:200]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(508, "Timeout")

@app.get("/api/leads")
async def list_leads(req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    searches = await insf_select("searches", {"user_id": user["id"]})
    all_leads = []
    for s in searches:
        all_leads.extend(s.get("leads", []))
    return {"leads": all_leads, "count": len(all_leads)}

@app.get("/api/leads/export")
async def export_leads(req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    searches = await insf_select("searches", {"user_id": user["id"]})
    all_leads = []
    for s in searches:
        all_leads.extend(s.get("leads", []))
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["name","website","domain","email","phone","description","source"])
    w.writeheader()
    for l in all_leads:
        w.writerow({k: l.get(k, "") for k in ["name","website","domain","email","phone","description","source"]})
    return Response(content=out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=leads.csv"})

@app.delete("/api/leads/{search_id}")
async def delete_lead(search_id: str, req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    searches = await insf_select("searches", {"id": search_id, "user_id": user["id"]})
    if not searches:
        raise HTTPException(404, "Busqueda no encontrada")
    await insf_delete("searches", "id", search_id)
    return {"status": "ok"}

# ─── Email Endpoints ───
@app.post("/api/emails/generate")
async def gen_email(d: EG):
    tpls = {
        "profesional": f"Hola {d.lead_name},\n\nHe visto el trabajo de {d.lead_company or d.lead_name} y creo que podriamos ayudaros a conseguir mas clientes.\n\nNuestro sistema automatiza la captacion de leads, ahorrando tiempo y aumentando ventas.\n\nTe gustaria una llamada de 15 minutos?\n\nUn saludo,\nEquipo LeadPilot",
        "casual": f"Hola {d.lead_name}!\n\nVi {d.lead_company or d.lead_name} y me parecio genial. Tenemos algo que podria ayudaros a crecer mas rapido.\n\nHablamos 15 min?\n\nUn saludo!",
        "directo": f"{d.lead_name},\n\nAyudamos a empresas como {d.lead_company or d.lead_name} a conseguir mas clientes con automatizacion.\n\n3 beneficios: leads cualificados, emails personalizados, resultados en 2-3 semanas.\n\nHablamos?\n\nLeadPilot"
    }
    return {"email": tpls.get(d.tone, tpls["profesional"]), "tone": d.tone}

@app.post("/api/emails/send")
async def send_email(d: ES, req: Request):
    email = get_current_user(req)
    if not await check_limit(email, "emails"):
        raise HTTPException(403, "Limite de emails alcanzado. Upgrade tu plan.")
    tid = str(uuid.uuid4())[:8]
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"LeadPilot <{SMTP_USER}>"
        msg["To"] = f"{d.to_name} <{d.to_email}>"
        msg["Subject"] = d.subject
        tracking_url = f"{INSFORGE_URL}/api/track/{tid}" if False else f"https://leadpilot.es/api/track/{tid}"
        msg.attach(MIMEText(d.body_html + f'<img src="{tracking_url}" width="1"/>', "html"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, d.to_email, msg.as_string())
        email_record = {
            "id": str(uuid.uuid4()),
            "user_id": (await get_user_by_email(email))["id"],
            "to_email": d.to_email,
            "subject": d.subject,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        await insf_insert("emails", email_record)
        await inc_use(email, "emails")
        return {"status": "ok", "success": True, "tracking_id": tid}
    except Exception as ex:
        raise HTTPException(500, f"Error: {ex}")

@app.get("/api/emails/sent")
async def list_sent(req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    sent = await insf_select("emails", {"user_id": user["id"]})
    return {
        "emails": {e["id"]: e for e in sent},
        "count": len(sent)
    }

@app.get("/api/track/{tid}")
async def track(tid: str):
    # Pixel tracking - marcar email como abierto
    try:
        await insf_update("emails", "id", tid, {"status": "opened"})
    except Exception:
        pass
    px = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    return Response(content=px, media_type="image/gif")

# ─── Campaigns Endpoints ───
@app.post("/api/campaigns/create")
async def create_campaign(d: CC, req: Request):
    email = get_current_user(req)
    if not await check_limit(email, "campaigns"):
        raise HTTPException(403, "Limite de campanas alcanzado")
    user = await get_user_by_email(email)
    # Obtener leads seleccionados
    searches = await insf_select("searches", {"user_id": user["id"]})
    selected = []
    for s in searches:
        for i, lead in enumerate(s.get("leads", [])):
            if i in d.lead_ids:
                selected.append(lead)
    campaign_data = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "name": d.name,
        "subject": d.subject,
        "template": d.template,
        "status": "draft",
        "sent_count": 0,
        "opened_count": 0,
        "clicked_count": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    await insf_insert("campaigns", campaign_data)
    await inc_use(email, "campaigns")
    return {"status": "ok", "success": True, "campaign_id": campaign_data["id"], "total_leads": len(selected)}

@app.get("/api/campaigns")
async def list_campaigns(req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    campaigns = await insf_select("campaigns", {"user_id": user["id"]})
    return {"campaigns": {c["id"]: c for c in campaigns}}

@app.post("/api/campaigns/{cid}/send")
async def send_campaign(cid: str, req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    campaigns = await insf_select("campaigns", {"id": cid, "user_id": user["id"]})
    if not campaigns:
        raise HTTPException(404, "Campana no encontrada")
    campaign = campaigns[0]
    # Obtener leads del usuario
    searches = await insf_select("searches", {"user_id": user["id"]})
    all_leads = []
    for s in searches:
        all_leads.extend(s.get("leads", []))
    sent = 0
    errors = 0
    for lead in all_leads:
        if not lead.get("email") or not await check_limit(email, "emails"):
            break
        try:
            template = campaign.get("template", "Hola {{nombre}},")
            body = template\
                .replace("{{nombre}}", lead.get("name", ""))\
                .replace("{{empresa}}", lead.get("company", ""))\
                .replace("{{web}}", lead.get("website", ""))
            msg = MIMEMultipart("alternative")
            msg["From"] = f"LeadPilot <{SMTP_USER}>"
            msg["To"] = lead.get("email", "")
            msg["Subject"] = campaign.get("subject", "LeadPilot")
            tracking_url = f"https://leadpilot.es/api/track/{str(uuid.uuid4())[:8]}"
            msg.attach(MIMEText(body + f'<img src="{tracking_url}" width="1"/>', "html"))
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(SMTP_USER, lead.get("email", ""), msg.as_string())
            await insf_insert("emails", {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "to_email": lead.get("email", ""),
                "subject": campaign.get("subject", ""),
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            })
            await inc_use(email, "emails")
            sent += 1
        except Exception:
            errors += 1
    await insf_update("campaigns", "id", cid, {"status": "sent", "sent_count": sent, "sent_at": datetime.utcnow().isoformat()})
    return {"status": "ok", "sent": sent, "errors": errors}

# ─── Stats Endpoint ───
@app.get("/api/analytics/stats")
async def analytics_stats(req: Request):
    return await stats(req)

@app.get("/api/stats")
async def stats(req: Request):
    email = get_current_user(req)
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    searches = await insf_select("searches", {"user_id": user["id"]})
    emails_sent = await insf_select("emails", {"user_id": user["id"]})
    campaigns = await insf_select("campaigns", {"user_id": user["id"]})
    total_leads = sum(len(s.get("leads", [])) for s in searches)
    total_emails = len(emails_sent)
    opened = sum(1 for e in emails_sent if e.get("status") == "opened")
    plan = user.get("plan", "free")
    return {
        "leads": total_leads,
        "emails_sent": total_emails,
        "open_rate": round(opened / total_emails * 100, 1) if total_emails else 0,
        "campaigns": len(campaigns),
        "plan": plan,
        "leads_used": user.get("leads_used", 0),
        "emails_used": user.get("emails_used", 0),
        "campaigns_used": user.get("campaigns_used", 0),
        "month": datetime.now().strftime("%Y-%m")
    }

# ─── Stripe Endpoints ───
@app.get("/api/stripe/config")
async def stripe_config():
    return {"publishableKey": STRIPE_PUBLISHABLE}

@app.post("/api/stripe/create-checkout")
async def create_checkout(body: dict, req: Request):
    email = get_current_user(req)
    plan = body.get("plan", "starter")
    if not STRIPE_SECRET:
        return {"error": "Stripe no configurado"}
    import stripe
    stripe.api_key = STRIPE_SECRET
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": f"price_{plan}", "quantity": 1}],
            mode="subscription",
            success_url="https://leadpilot.es/dashboard.html?checkout=success",
            cancel_url="https://leadpilot.es/dashboard.html?checkout=cancel",
            customer_email=email,
            metadata={"user_email": email, "plan": plan}
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as ex:
        return {"error": str(ex)}

# ─── Contact Form ───
class ContactForm(BaseModel):
    name: str
    email: str
    company: str = ""
    message: str
    source: str = "contact_form"

@app.post("/api/contact")
async def contact_form(d: ContactForm):
    """Recibe mensajes del formulario de contacto y los guarda en Insforge"""
    contact_data = {
        "id": str(uuid.uuid4()),
        "name": d.name,
        "email": d.email,
        "company": d.company,
        "message": d.message,
        "source": d.source,
        "status": "new",
        "received_at": datetime.utcnow().isoformat()
    }
    await insf_insert("contacts", contact_data)
    
    session_id = str(uuid.uuid4())
    chat_msg = {
        "session_id": session_id,
        "user_name": d.name,
        "user_email": d.email,
        "user_message": d.message,
        "source": d.source,
        "status": "pending",
        "language": "es"
    }
    await insf_insert("chat_messages", chat_msg)
    
    if SMTP_PASS:
        try:
            msg = MIMEMultipart()
            msg["From"] = f"LeadPilot <{SMTP_USER}>"
            msg["To"] = SMTP_USER
            msg["Subject"] = f"Nuevo contacto desde {d.source}"
            body = f"Nombre: {d.name}\nEmail: {d.email}\nEmpresa: {d.company}\nFuente: {d.source}\n\nMensaje:\n{d.message}"
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(SMTP_USER, SMTP_USER, msg.as_string())
        except Exception:
            pass
    return {"status": "ok", "session_id": session_id, "message": "Mensaje recibido"}

@app.get("/api/contact/responses")
async def get_chat_responses(session_id: str = None):
    """Obtener respuestas del bot para el widget de chat"""
    if session_id:
        rows = await insf_select("chat_messages", {"session_id": session_id})
    else:
        rows = await insf_select("chat_messages", limit=50)
    responses = []
    for r in rows:
        if r.get("bot_response"):
            responses.append({
                "session_id": r.get("session_id"),
                "user_message": r.get("user_message"),
                "bot_response": r.get("bot_response"),
                "status": r.get("status"),
                "created_at": r.get("created_at")
            })
    return {"responses": responses}

# ─── Analytics ───
@app.post("/api/analytics/ping")
async def analytics_ping(req: Request):
    return {"status": "ok"}

# ─── Stripe Webhook ───
@app.post("/api/stripe/webhook")
async def stripe_webhook(req: Request):
    import stripe
    stripe.api_key = STRIPE_SECRET
    payload = await req.body()
    sig = req.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return {"error": "invalid signature"}
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email") or session.get("customer_details", {}).get("email")
        plan = session.get("metadata", {}).get("plan", "starter")
        if email:
            await insf_update("users", "email", email, {"plan": plan})
        return {"received": True}
    return {"received": True}

@app.post("/api/stripe/portal")
async def customer_portal(req: Request):
    email = get_current_user(req)
    if not STRIPE_SECRET:
        return {"error": "Stripe no configurado"}
    import stripe
    stripe.api_key = STRIPE_SECRET
    try:
        cust = stripe.Customer.list(email=email, limit=1)
        if cust.data:
            s = stripe.billing_portal.Session.create(customer=cust.data[0].id)
            return {"url": s.url}
        return {"error": "No se encontro cliente"}
    except Exception as ex:
        return {"error": str(ex)}

# ─── Auth Extra (Forgot/Reset) ───
RESET_CODES = {}

@app.post("/api/auth/forgot")
async def forgot(body: dict):
    email = body.get("email", "")
    if not email:
        raise HTTPException(400, "Email requerido")
    user = await get_user_by_email(email)
    if not user:
        return {"status": "ok", "message": "Si el email existe, se envio enlace"}
    code = str(uuid.uuid4())[:8]
    RESET_CODES[code] = {"email": email, "expires": time.time() + 3600}
    try:
        msg = MIMEMultipart()
        msg["From"] = f"LeadPilot <{SMTP_USER}>"
        msg["To"] = email
        msg["Subject"] = "Recupera tu contrasena - LeadPilot"
        msg.attach(MIMEText(f"Hola {user.get('name','')},\n\nUsa este codigo para restablecer tu contrasena: {code}\n\nEste codigo expira en 1 hora.\n\nLeadPilot", "plain"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, email, msg.as_string())
        return {"status": "ok", "message": "Email enviado"}
    except Exception:
        return {"status": "ok", "message": "Si el email existe, se envio enlace"}

@app.post("/api/auth/reset")
async def reset(body: dict):
    code = body.get("code", "")
    new_password = body.get("new_password", "")
    if not code or not new_password:
        raise HTTPException(400, "Codigo y nueva contrasena requeridos")
    if code not in RESET_CODES:
        raise HTTPException(400, "Codigo invalido")
    info = RESET_CODES[code]
    if time.time() > info["expires"]:
        raise HTTPException(400, "Codigo expirado")
    user = await get_user_by_email(info["email"])
    if not user:
        raise HTTPException(400, "Usuario no encontrado")
    await insf_update("users", "email", info["email"], {"password": hash_pw(new_password)})
    del RESET_CODES[code]
    return {"status": "ok", "message": "Contrasena actualizada"}

# ─── Webhooks (Zapier/Make) ───
@app.post("/api/webhook/lead")
async def webhook_lead(body: dict, req: Request):
    email = get_current_user(req)
    url = body.get("url", "")
    if url:
        try:
            import requests
            requests.post(url, json={"event": "new_lead", "user": email, "timestamp": datetime.utcnow().isoformat()}, timeout=10)
            return {"status": "ok", "sent": True}
        except Exception:
            return {"status": "ok", "sent": False}
    return {"status": "ok"}

@app.post("/api/webhook/email")
async def webhook_email(body: dict, req: Request):
    email = get_current_user(req)
    url = body.get("url", "")
    if url:
        try:
            import requests
            requests.post(url, json={"event": "email_sent", "user": email, "timestamp": datetime.utcnow().isoformat()}, timeout=10)
            return {"status": "ok", "sent": True}
        except Exception:
            return {"status": "ok", "sent": False}
    return {"status": "ok"}

@app.post("/api/webhook/campaign")
async def webhook_campaign(body: dict, req: Request):
    email = get_current_user(req)
    url = body.get("url", "")
    if url:
        try:
            import requests
            requests.post(url, json={"event": "campaign_sent", "user": email, "timestamp": datetime.utcnow().isoformat()}, timeout=10)
            return {"status": "ok", "sent": True}
        except Exception:
            return {"status": "ok", "sent": False}
    return {"status": "ok"}

# ─── Root ───
@app.get("/")
async def root():
    return {"message": "LeadPilot API v1.4 (Insforge)", "status": "running", "database": "Insforge PostgreSQL"}

# ─── Swagger Docs ───
@app.get("/docs")
async def docs():
    return {
        "message": "Swagger docs en construccion",
        "database": "Insforge",
        "endpoints": [
            {"method": "POST", "path": "/api/register", "body": {"email": "str", "password": "str", "name": "str"}},
            {"method": "POST", "path": "/api/login", "body": {"email": "str", "password": "str"}},
            {"method": "GET", "path": "/api/user/me", "auth": True},
            {"method": "PUT", "path": "/api/profile", "auth": True},
            {"method": "POST", "path": "/api/profile/password", "auth": True},
            {"method": "POST", "path": "/api/leads/search", "body": {"query": "str", "location": "str", "max_results": "int"}, "auth": True},
            {"method": "GET", "path": "/api/leads", "auth": True},
            {"method": "GET", "path": "/api/leads/export", "auth": True},
            {"method": "DELETE", "path": "/api/leads/{id}", "auth": True},
            {"method": "POST", "path": "/api/emails/generate", "body": {"lead_name": "str", "tone": "str"}},
            {"method": "POST", "path": "/api/emails/send", "body": {"to_email": "str", "subject": "str", "body_html": "str"}, "auth": True},
            {"method": "GET", "path": "/api/emails/sent", "auth": True},
            {"method": "POST", "path": "/api/campaigns/create", "body": {"name": "str", "subject": "str", "template": "str", "lead_ids": "[]"}, "auth": True},
            {"method": "GET", "path": "/api/campaigns", "auth": True},
            {"method": "POST", "path": "/api/campaigns/{id}/send", "auth": True},
            {"method": "GET", "path": "/api/stats", "auth": True},
            {"method": "POST", "path": "/api/stripe/create-checkout", "body": {"plan": "str"}, "auth": True},
            {"method": "POST", "path": "/api/contact", "body": {"name": "str", "email": "str", "message": "str"}},
            {"method": "POST", "path": "/api/auth/forgot", "body": {"email": "str"}},
            {"method": "POST", "path": "/api/auth/reset", "body": {"code": "str", "new_password": "str"}},
            {"method": "POST", "path": "/api/webhook/lead", "body": {"url": "str"}, "auth": True},
            {"method": "POST", "path": "/api/webhook/email", "body": {"url": "str"}, "auth": True},
            {"method": "POST", "path": "/api/webhook/campaign", "body": {"url": "str"}, "auth": True},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
