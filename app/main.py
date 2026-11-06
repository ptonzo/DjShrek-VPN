from __future__ import annotations
import base64, hashlib, json, secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from .config import settings
from .nodes import configured_nodes, all_node_status, select_server_side_fallback
from .store import connect, init_db
from .security import current_user_id, issue_access_token, password_hash, password_verify, require_admin
from .billing import billing_status

app = FastAPI(title=settings.app_name, version="0.2.0")
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.on_event("startup")
def startup():
    if settings.app_env.lower() == "production":
        if len(settings.app_secret) < 32 or settings.app_secret == "development-only-change-me":
            raise RuntimeError("Set a unique APP_SECRET of at least 32 characters in production")
        if not settings.admin_api_key or len(settings.admin_api_key) < 32:
            raise RuntimeError("Set DJSHREK_ADMIN_API_KEY of at least 32 characters in production")
    init_db()

class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class NodeCredential(BaseModel):
    node_id: str
    vless_uri: str = Field(min_length=20, max_length=4096)

class SubscriptionRequest(BaseModel):
    email: EmailStr
    days: int = Field(default=30, ge=1, le=365)
    nodes: list[NodeCredential] = Field(min_length=5, max_length=5)

def utcnow():
    return datetime.now(timezone.utc)

@app.get("/", include_in_schema=False)
async def homepage():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": settings.app_name, "version": "0.2.0"}

@app.get("/api/nodes")
async def nodes():
    return {"nodes": await all_node_status()}

@app.get("/api/nodes/catalog")
async def node_catalog():
    return {"nodes": [n.__dict__ for n in configured_nodes()]}

@app.get("/api/nodes/recommended")
async def recommended_node():
    node = await select_server_side_fallback()
    if node is None:
        return {"status": "unavailable", "node": None,
                "note": "No configured node passed the server-side TCP health check."}
    return {"status": "ok", "node": node,
            "note": "Latency is measured from the API host, not from the customer's device."}

@app.post("/api/auth/register", status_code=201)
def register(data: Credentials):
    email = str(data.email).lower()
    with connect() as db:
        try:
            cur = db.execute("INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",
                             (email, password_hash(data.password), utcnow().isoformat()))
            user_id = cur.lastrowid
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise HTTPException(status_code=409, detail="An account with this email already exists")
            raise
    return {"access_token": issue_access_token(user_id), "token_type": "bearer", "expires_in": 86400}

@app.post("/api/auth/login")
def login(data: Credentials):
    with connect() as db:
        user = db.execute("SELECT id,password_hash FROM users WHERE email=?",
                          (str(data.email).lower(),)).fetchone()
    if not user or not password_verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": issue_access_token(user["id"]), "token_type": "bearer", "expires_in": 86400}

@app.get("/api/me")
def me(user_id: int = Depends(current_user_id)):
    with connect() as db:
        user = db.execute("SELECT id,email,created_at FROM users WHERE id=?", (user_id,)).fetchone()
        if not user: raise HTTPException(status_code=404, detail="Account not found")
        subs = db.execute("SELECT id,expires_at,active FROM subscriptions WHERE user_id=? ORDER BY id DESC",
                          (user_id,)).fetchall()
    return {"user": dict(user), "subscriptions": [dict(s) for s in subs]}

@app.get("/api/billing/status")
def billing():
    return billing_status()

@app.post("/api/admin/subscriptions", dependencies=[Depends(require_admin)], status_code=201)
def issue_subscription(data: SubscriptionRequest):
    email = str(data.email).lower()
    required_ids = {"de-1", "fi-1", "nl-1", "pl-1", "us-1"}
    supplied_ids = {node.node_id for node in data.nodes}
    if supplied_ids != required_ids or len(supplied_ids) != 5:
        raise HTTPException(status_code=422, detail="Exactly one credential for each of the five configured node IDs is required")
    if any(not node.vless_uri.startswith("vless://") for node in data.nodes):
        raise HTTPException(status_code=422, detail="Each node credential must be a VLESS URI")
    with connect() as db:
        user = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User must register before subscription issuance")
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires = (utcnow() + timedelta(days=data.days)).isoformat()
        node_uris = json.dumps([node.vless_uri for node in data.nodes])
        cur = db.execute("INSERT INTO subscriptions(user_id,token_hash,expires_at,active,vless_uris_json,created_at) VALUES(?,?,?,?,?,?)",
                         (user["id"], token_hash, expires, 1, node_uris, utcnow().isoformat()))
        sub_id = cur.lastrowid
    return {"subscription_id": sub_id, "subscription_url": f"{settings.public_base_url.rstrip('/')}/s/{raw_token}",
            "expires_at": expires, "warning": "Treat this URL as a password. Share it only with the customer."}

@app.post("/api/admin/subscriptions/{subscription_id}/revoke", dependencies=[Depends(require_admin)])
def revoke_subscription(subscription_id: int):
    with connect() as db:
        cur = db.execute("UPDATE subscriptions SET active=0 WHERE id=?", (subscription_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "revoked", "subscription_id": subscription_id}

@app.get("/s/{token}", response_class=PlainTextResponse)
def subscription(token: str):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with connect() as db:
        sub = db.execute("""SELECT s.expires_at,s.active,s.vless_uris_json FROM subscriptions s
                            WHERE s.token_hash=? ORDER BY s.id DESC LIMIT 1""", (token_hash,)).fetchone()
    if not sub or not sub["active"] or datetime.fromisoformat(sub["expires_at"]) <= utcnow():
        raise HTTPException(status_code=404, detail="Subscription not found or expired")
    try:
        uris = json.loads(sub["vless_uris_json"])
    except json.JSONDecodeError:
        raise HTTPException(status_code=503, detail="Subscription configuration is invalid")
    if len(uris) != 5 or any(not uri.startswith("vless://") for uri in uris):
        raise HTTPException(status_code=503, detail="Personal VPN credentials have not been provisioned")
    payload = base64.b64encode("\n".join(uris).encode()).decode()
    return PlainTextResponse(payload, media_type="text/plain")
