"""
LeadPilot.es - Backend API v1.2
Full JWT Auth + Stripe Checkout + Plan Limits
"""
import os, json, hashlib, time, subprocess, uuid, smtplib, csv, io
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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DATA_DIR = "/root/.openclaw/workspace/leadpilot/data"
USERS_FILE = f"{DATA_DIR}/users.json"
LEADS_FILE = f"{DATA_DIR}/leads.json"
CAMPAIGNS_FILE = f"{DATA_DIR}/campaigns.json"
EMAILS_FILE = f"{DATA_DIR}/emails_sent.json"

JWT_SECRET = "leadpilot_jwt_secret_2026"
JWT_ALGO = "HS256"
STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

PLANS = {
    "free":     {"leads": 10,  "emails": 50,  "campaigns": 1,  "price": 0},
    "starter":  {"leads": 100, "emails": 500, "campaigns": 10, "price": 29},
    "pro":      {"leads": 500, "emails": 2000, "campaigns": -1, "price": 79},
    "business": {"leads": -1,  "emails": -1,   "campaigns": -1, "price": 149},
}
STRIPE_PLANS = {
    "free":     {"price_id": "price_1TK3jG2LcCApvvprSS2CixKw"},
    "starter":  {"price_id": "price_1TK3jH2LcCApvvprkwYboITe"},
    "pro":      {"price_id": "price_1TK3jH2LcCApvvprdQubCj0j"},
    "business": {"price_id": "price_1TK3jI2LcCApvvpr81KXv9EH"},
}

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 465
SMTP_USER, SMTP_PASS = "yhasvenezuela@gmail.com", "isrwrzraxlkwrclo"

# ─── Helpers ───
def load_json(f):
    if os.path.exists(f):
        with open(f) as fh: return json.load(fh)
    return {}

def save_json(f, d):
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, 'w') as fh: json.dump(d, fh, indent=2, ensure_ascii=False)

def hash_pw(pw): return hashlib.sha256((pw+JWT_SECRET).encode()).hexdigest()
def make_token(email):
    return jwt.encode({"sub": email, "exp": (datetime.utcnow()+timedelta(days=30)).timestamp()}, JWT_SECRET, algorithm=JWT_ALGO)
def verify_token(t):
    try: return jwt.decode(t, JWT_SECRET, algorithms=[JWT_ALGO])["sub"]
    except: return None
def get_user(email): return load_json(USERS_FILE).get(email)
def get_current_user(req: Request):
    t = req.headers.get("Authorization","")
    if not t.startswith("Bearer "): raise HTTPException(401, "No token")
    e = verify_token(t[7:]); 
    if not e: raise HTTPException(401, "Token inválido")
    return e

def check_limit(email, res, n=1):
    u = get_user(email)
    if not u: raise HTTPException(404, "Usuario no encontrado")
    p = PLANS.get(u.get("plan","free"), PLANS["free"])
    lim = p.get(res, 0)
    if lim == -1: return True
    return u.get(f"{res}_used", 0) + n <= lim

def inc_use(email, res, n=1):
    u = load_json(USERS_FILE)
    if email in u:
        u[email][f"{res}_used"] = u[email].get(f"{res}_used", 0) + n
        save_json(USERS_FILE, u)

# ─── Models ───
class R(BaseModel): email: str; password: str; name: str = ""
class L(BaseModel): email: str; password: str
class S(BaseModel): query: str; location: str = "España"; max_results: int = 20
class EG(BaseModel): lead_name: str; lead_company: str = ""; lead_website: str = ""; tone: str = "profesional"
class ES(BaseModel): to_email: str; to_name: str; subject: str; body_html: str
class CC(BaseModel): name: str; subject: str; template: str; lead_ids: List[int]

# ─── Auth ───
@app.post("/api/register")
async def register(d: R):
    if len(d.password) < 6: raise HTTPException(400, "La contrasena debe tener minimo 6 caracteres")
    if len(d.name) < 2: raise HTTPException(400, "El nombre debe tener minimo 2 caracteres")
    u = load_json(USERS_FILE)
    if d.email in u: raise HTTPException(400, "Email ya registrado")
    month = datetime.now().strftime("%Y-%m")
    u[d.email] = {"name": d.name, "email": d.email, "password": hash_pw(d.password),
        "plan": "free", "leads_used": 0, "emails_used": 0, "campaigns_used": 0,
        "usage_month": month, "created": datetime.utcnow().isoformat()}
    save_json(USERS_FILE, u)
    return {"status": "ok", "token": make_token(d.email), "user": d.email, "plan": "free", "limits": PLANS["free"]}

@app.post("/api/login")
async def login(d: L):
    u = get_user(d.email)
    if not u or u["password"] != hash_pw(d.password): raise HTTPException(401, "Credenciales inválidas")
    p = u.get("plan","free")
    return {"status": "ok", "token": make_token(d.email), "user": d.email, "plan": p, "limits": PLANS.get(p, PLANS["free"])}

@app.get("/api/user/me")
async def me(req: Request):
    e = get_current_user(req)
    u = get_user(e)
    if not u: raise HTTPException(404, "No encontrado")
    p = u.get("plan","free")
    return {"user": {k: v for k, v in u.items() if k != "password"}, "limits": PLANS.get(p, PLANS["free"])}


@app.put("/api/profile")
async def update_profile(req: Request, d: dict):
    e = get_current_user(req)
    u = load_json(USERS_FILE)
    if e not in u: raise HTTPException(404, "No encontrado")
    if "name" in d: u[e]["name"] = d["name"]
    save_json(USERS_FILE, u)
    return {"status": "ok", "user": {k: v for k, v in u[e].items() if k != "password"}}

@app.post("/api/profile/password")
async def change_password(req: Request, d: dict):
    e = get_current_user(req)
    u = load_json(USERS_FILE)
    if e not in u: raise HTTPException(404, "No encontrado")
    old = d.get("old_password", "")
    new_p = d.get("new_password", "")
    if not old or not new_p: raise HTTPException(400, "Faltan datos")
    if not verify_pw(old, u[e]["password"]): raise HTTPException(400, "Contrasena actual incorrecta")
    if len(new_p) < 6: raise HTTPException(400, "Minimo 6 caracteres")
    u[e]["password"] = hash_pw(new_p)
    save_json(USERS_FILE, u)
    return {"status": "ok"}


@app.get("/api/plans")
async def plans(): return {"plans": PLANS}

@app.post("/api/plans/upgrade")
async def upgrade(body: dict, req: Request):
    e = get_current_user(req)
    plan = body.get("plan")
    if not plan or plan not in PLANS: raise HTTPException(400, "Plan inválido")
    u = load_json(USERS_FILE)
    if e in u: u[e]["plan"] = plan; save_json(USERS_FILE, u)
    return {"status": "ok", "plan": plan, "limits": PLANS[plan]}

# ─── Leads ───
@app.post("/api/leads/search")
async def search_leads(d: S, req: Request):
    e = get_current_user(req)
    if not check_limit(e, "leads"): raise HTTPException(403, "Límite de leads alcanzado. Upgrade tu plan.")
    try:
        r = subprocess.run(["python3", "/root/.openclaw/workspace/leadpilot/backend/scraper.py", d.query, d.location, str(d.max_results)], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            leads = json.loads(r.stdout)
            filtered = [l for l in leads if l.get("email") or l.get("phone")]
            all_l = load_json(LEADS_FILE)
            lid = str(int(time.time()))
            all_l[lid] = {"query": d.query, "location": d.location, "results": filtered, "user_email": e, "created": datetime.utcnow().isoformat()}
            save_json(LEADS_FILE, all_l)
            inc_use(e, "leads", len(filtered))
            return {"status": "ok", "leads": filtered, "count": len(filtered)}
        raise HTTPException(500, f"Error: {r.stderr[:200]}")
    except subprocess.TimeoutExpired: raise HTTPException(508, "Timeout")

@app.get("/api/leads")
async def list_leads(req: Request):
    e = get_current_user(req)
    ld = load_json(LEADS_FILE)
    ml = []
    for k, d in ld.items():
        if d.get("user_email") == e: ml.extend(d.get("results", []))
    return {"leads": ml, "count": len(ml)}

@app.get("/api/leads/export")
async def export_leads(req: Request):
    e = get_current_user(req)
    ld = load_json(LEADS_FILE)
    ml = []
    for k, d in ld.items():
        if d.get("user_email") == e: ml.extend(d.get("results", []))
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["name","website","domain","email","phone","description","source"])
    w.writeheader()
    for l in ml: w.writerow({k: l.get(k,"") for k in ["name","website","domain","email","phone","description","source"]})
    return Response(content=out.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=leads.csv"})

# ─── Email ───
@app.post("/api/emails/generate")
async def gen_email(d: EG):
    tpls = {
        "profesional": f"Hola {d.lead_name},\n\nHe visto el trabajo de {d.lead_company or d.lead_name} y creo que podríamos ayudaros a conseguir más clientes.\n\nNuestro sistema automatiza la captación de leads, ahorrando tiempo y aumentando ventas.\n\n¿Te gustaría una llamada de 15 minutos?\n\nUn saludo,\nEquipo LeadPilot",
        "casual": f"¡Hola {d.lead_name}!\n\nVi {d.lead_company or d.lead_name} y me pareció genial. Tenemos algo que podría ayudaros a crecer más rápido.\n\n¿Hablamos 15 min?\n\n¡Un saludo!",
        "directo": f"{d.lead_name},\n\nAyudamos a empresas como {d.lead_company or d.lead_name} a conseguir más clientes con automatización.\n\n3 beneficios: leads cualificados, emails personalizados, resultados en 2-3 semanas.\n\n¿Hablamos?\n\nLeadPilot"
    }
    return {"email": tpls.get(d.tone, tpls["profesional"]), "tone": d.tone}

@app.post("/api/emails/send")
async def send_email(d: ES, req: Request):
    e = get_current_user(req)
    if not check_limit(e, "emails"): raise HTTPException(403, "Límite de emails alcanzado. Upgrade tu plan.")
    tid = str(uuid.uuid4())[:8]
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"LeadPilot <{SMTP_USER}>"
        msg["To"] = f"{d.to_name} <{d.to_email}>"
        msg["Subject"] = d.subject
        msg.attach(MIMEText(d.body_html + f'<img src="https://leadpilot.es/api/track/{tid}" width="1"/>', "html"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, d.to_email, msg.as_string())
        em = load_json(EMAILS_FILE)
        em[tid] = {"to": d.to_email, "to_name": d.to_name, "subject": d.subject, "user_email": e, "sent_at": datetime.utcnow().isoformat(), "opened": False}
        save_json(EMAILS_FILE, em)
        inc_use(e, "emails")
        return {"status": "ok", "tracking_id": tid}
    except Exception as ex: raise HTTPException(500, f"Error: {ex}")

@app.get("/api/emails/sent")
async def list_sent(req: Request):
    e = get_current_user(req)
    em = load_json(EMAILS_FILE)
    return {"emails": {k: v for k, v in em.items() if v.get("user_email") == e}, "count": sum(1 for v in em.values() if v.get("user_email") == e)}

@app.get("/api/track/{tid}")
async def track(tid: str):
    em = load_json(EMAILS_FILE)
    if tid in em: em[tid]["opened"] = True; save_json(EMAILS_FILE, em)
    px = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    return Response(content=px, media_type="image/gif")

# ─── Campaigns ───
@app.post("/api/campaigns/create")
async def create_campaign(d: CC, req: Request):
    e = get_current_user(req)
    if not check_limit(e, "campaigns"): raise HTTPException(403, "Límite de campañas alcanzado")
    ld = load_json(LEADS_FILE); sel = []
    for k, ldd in ld.items():
        if ldd.get("user_email") == e:
            for i, l in enumerate(ldd.get("results", [])):
                if i in d.lead_ids: sel.append(l)
    cid = str(uuid.uuid4())[:8]
    cp = load_json(CAMPAIGNS_FILE)
    cp[cid] = {"name": d.name, "subject": d.subject, "template": d.template, "leads": sel, "user_email": e, "status": "draft", "sent": 0, "total_leads": len(sel), "created": datetime.utcnow().isoformat()}
    save_json(CAMPAIGNS_FILE, cp)
    inc_use(e, "campaigns")
    return {"status": "ok", "campaign_id": cid, "total_leads": len(sel)}

@app.get("/api/campaigns")
async def list_campaigns(req: Request):
    e = get_current_user(req)
    cp = load_json(CAMPAIGNS_FILE)
    return {"campaigns": {k: v for k, v in cp.items() if v.get("user_email") == e}}

@app.post("/api/campaigns/{cid}/send")
async def send_campaign(cid: str, req: Request):
    e = get_current_user(req)
    cp = load_json(CAMPAIGNS_FILE)
    if cid not in cp or cp[cid].get("user_email") != e: raise HTTPException(404, "No encontrada")
    c = cp[cid]; sent = 0; errors = 0
    for l in c.get("leads", []):
        if not l.get("email") or not check_limit(e, "emails"): break
        try:
            body = c["template"].replace("{{nombre}}", l.get("name","")).replace("{{empresa}}", l.get("name","")).replace("{{web}}", l.get("website",""))
            tid = str(uuid.uuid4())[:8]
            msg = MIMEMultipart("alternative")
            msg["From"] = f"LeadPilot <{SMTP_USER}>"
            msg["To"] = l.get("email","")
            msg["Subject"] = c["subject"]
            msg.attach(MIMEText(body + f'<img src="https://leadpilot.es/api/track/{tid}" width="1"/>', "html"))
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(SMTP_USER, l.get("email",""), msg.as_string())
            em = load_json(EMAILS_FILE)
            em[tid] = {"to": l.get("email",""), "subject": c["subject"], "user_email": e, "campaign_id": cid, "sent_at": datetime.utcnow().isoformat(), "opened": False}
            save_json(EMAILS_FILE, em)
            inc_use(e, "emails"); sent += 1
        except: errors += 1
    cp[cid]["status"] = "sent"; cp[cid]["sent"] = sent; save_json(CAMPAIGNS_FILE, cp)
    return {"status": "ok", "sent": sent, "errors": errors}

# ─── Stats ───
@app.get("/api/stats")
async def stats(req: Request):
    e = get_current_user(req)
    u = get_user(e)
    ld = load_json(LEADS_FILE); em = load_json(EMAILS_FILE); cp = load_json(CAMPAIGNS_FILE)
    ml = sum(len(d.get("results",[])) for d in ld.values() if d.get("user_email") == e)
    me = {k: v for k, v in em.items() if v.get("user_email") == e}
    mc = {k: v for k, v in cp.items() if v.get("user_email") == e}
    total = len(me); opened = sum(1 for v in me.values() if v.get("opened"))
    p = u.get("plan","free") if u else "free"
    return {"leads": ml, "emails_sent": total, "open_rate": round(opened/total*100,1) if total else 0, "campaigns": len(mc), "plan": p, "month": datetime.now().strftime("%Y-%m")}

# ─── Stripe ───
@app.get("/api/stripe/config")
async def stripe_config(): return {"publishableKey": STRIPE_PUBLISHABLE}

@app.post("/api/stripe/create-checkout")
async def create_checkout(body: dict, req: Request):
    e = get_current_user(req)
    plan = body.get("plan", "starter")
    if plan not in STRIPE_PLANS: raise HTTPException(400, "Plan inválido")
    if not STRIPE_SECRET: return {"error": "Stripe no configurado"}
    import stripe; stripe.api_key = STRIPE_SECRET
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": STRIPE_PLANS[plan]["price_id"], "quantity": 1}],
            mode="subscription",
            success_url="https://88.223.95.118:8082/dashboard.html?checkout=success",
            cancel_url="https://88.223.95.118:8082/dashboard.html?checkout=cancel",
            customer_email=e,
            metadata={"user_email": e, "plan": plan}
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as ex: return {"error": str(ex)}





# ─── Analytics ───
@app.post("/api/analytics/ping")
async def analytics_ping(req: Request):
    """Simple page view tracking"""
    # In production, connect to Umami or Plausible
    return {"status": "ok"}

# ─── Stripe Webhook ───
@app.post("/api/stripe/webhook")
async def stripe_webhook(req: Request):
    import stripe
    stripe.api_key = STRIPE_SECRET
    
    payload = await req.body()
    sig = req.headers.get("stripe-signature", "")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except:
        return {"error": "invalid signature"}
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email") or session.get("customer_details", {}).get("email")
        plan = session.get("metadata", {}).get("plan", "starter")
        
        if email:
            for u in users:
                if u["email"] == email:
                    plan_tier = {"starter": "starter", "pro": "pro", "business": "business"}.get(plan, "starter")
                    u["plan"] = plan_tier
                    save_users()
                    break
        
        return {"received": True}
    
    return {"received": True}

@app.post("/api/stripe/portal")
async def customer_portal(req: Request):
    e = get_current_user(req)
    if not STRIPE_SECRET: return {"error": "Stripe no configurado"}
    import stripe; stripe.api_key = STRIPE_SECRET
    try:
        cust = stripe.Customer.list(email=e, limit=1)
        if cust.data:
            s = stripe.billing_portal.Session.create(customer=cust.data[0].id)
            return {"url": s.url}
        return {"error": "No se encontró cliente"}
    except Exception as ex: return {"error": str(ex)}

# ─── Root ───
@app.get("/")
async def root(): return {"message": "LeadPilot API v1.2", "status": "running"}



# ─── Auth Extra ───
RESET_CODES = {}

@app.post("/api/auth/forgot")
async def forgot(body: dict):
    email = body.get("email","")
    if not email: raise HTTPException(400, "Email requerido")
    u = get_user(email)
    if not u: return {"status": "ok", "message": "Si el email existe, se envió enlace"}
    # Generate reset code
    code = str(uuid.uuid4())[:8]
    RESET_CODES[code] = {"email": email, "expires": time.time() + 3600}
    # Send email
    try:
        msg = MIMEMultipart()
        msg["From"] = f"LeadPilot <{SMTP_USER}>"
        msg["To"] = email
        msg["Subject"] = "Recupera tu contraseña - LeadPilot"
        msg.attach(MIMEText(f"Hola {u.get('Name','')},\n\nUsa este código para restablecer tu contraseña: {code}\n\nEste código expira en 1 hora.\n\nLeadPilot", "plain"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, email, msg.as_string())
        return {"status": "ok", "message": "Email enviado"}
    except Exception as e:
        return {"status": "ok", "message": "Si el email existe, se envió enlace"}

@app.post("/api/auth/reset")
async def reset(body: dict):
    code = body.get("code","")
    new_password = body.get("new_password","")
    if not code or not new_password: raise HTTPException(400, "Código y nueva contraseña requeridos")
    if code not in RESET_CODES: raise HTTPException(400, "Código inválido")
    info = RESET_CODES[code]
    if time.time() > info["expires"]: raise HTTPException(400, "Código expirado")
    u = load_json(USERS_FILE)
    if info["email"] in u:
        u[info["email"]]["password"] = hash_pw(new_password)
        save_json(USERS_FILE, u)
        del RESET_CODES[code]
        return {"status": "ok", "message": "Contraseña actualizada"}
    raise HTTPException(400, "Usuario no encontrado")

# ─── Webhooks (Zapier/Make) ───
@app.post("/api/webhook/lead")
async def webhook_lead(body: dict, req: Request):
    e = get_current_user(req)
    ld_url = body.get("url", "")
    if ld_url:
        try:
            import requests
            r = requests.post(ld_url, json={"event": "new_lead", "user": e, "timestamp": datetime.utcnow().isoformat()}, timeout=10)
            return {"status": "ok", "sent": True}
        except: return {"status": "ok", "sent": False}
    return {"status": "ok"}

@app.post("/api/webhook/email")
async def webhook_email(body: dict, req: Request):
    e = get_current_user(req)
    em_url = body.get("url", "")
    if em_url:
        try:
            import requests
            r = requests.post(em_url, json={"event": "email_sent", "user": e, "timestamp": datetime.utcnow().isoformat()}, timeout=10)
            return {"status": "ok", "sent": True}
        except: return {"status": "ok", "sent": False}
    return {"status": "ok"}

@app.post("/api/webhook/campaign")
async def webhook_campaign(body: dict, req: Request):
    e = get_current_user(req)
    cp_url = body.get("url", "")
    if cp_url:
        try:
            import requests
            r = requests.post(cp_url, json={"event": "campaign_sent", "user": e, "timestamp": datetime.utcnow().isoformat()}, timeout=10)
            return {"status": "ok", "sent": True}
        except: return {"status": "ok", "sent": False}
    return {"status": "ok"}

# ─── Swagger Docs ───
@app.get("/docs")
async def docs():
    return {"message": "Swagger docs en construcción", "endpoints": [
        {"method": "POST", "path": "/api/register", "body": {"email": "str", "password": "str", "name": "str"}},
        {"method": "POST", "path": "/api/login", "body": {"email": "str", "password": "str"}},
        {"method": "GET", "path": "/api/user/me", "auth": True},
        {"method": "POST", "path": "/api/leads/search", "body": {"query": "str", "location": "str", "max_results": "int"}, "auth": True},
        {"method": "GET", "path": "/api/leads", "auth": True},
        {"method": "GET", "path": "/api/leads/export", "auth": True},
        {"method": "POST", "path": "/api/emails/generate", "body": {"lead_name": "str", "tone": "str"}, "auth": True},
        {"method": "POST", "path": "/api/emails/send", "body": {"to_email": "str", "subject": "str", "body_html": "str"}, "auth": True},
        {"method": "POST", "path": "/api/campaigns/create", "body": {"name": "str", "subject": "str", "template": "str"}, "auth": True},
        {"method": "GET", "path": "/api/stats", "auth": True},
        {"method": "POST", "path": "/api/stripe/create-checkout", "body": {"plan": "str"}, "auth": True},
        {"method": "POST", "path": "/api/auth/forgot", "body": {"email": "str"}},
        {"method": "POST", "path": "/api/auth/reset", "body": {"code": "str", "new_password": "str"}},
        {"method": "POST", "path": "/api/webhook/lead", "body": {"url": "str"}, "auth": True},
        {"method": "POST", "path": "/api/webhook/email", "body": {"url": "str"}, "auth": True},
        {"method": "POST", "path": "/api/webhook/campaign", "body": {"url": "str"}, "auth": True},
    ]}


if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8083)
