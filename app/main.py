from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .nodes import NODES, all_node_status, select_server_side_fallback

app = FastAPI(title=settings.app_name, version="0.1.0")
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/", include_in_schema=False)
async def homepage():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": settings.app_name}

@app.get("/api/nodes")
async def nodes():
    return {"nodes": await all_node_status()}

@app.get("/api/nodes/catalog")
async def node_catalog():
    return {"nodes": [n.__dict__ for n in NODES]}

@app.get("/api/nodes/recommended")
async def recommended_node():
    node = await select_server_side_fallback()
    if node is None:
        return {"status": "unavailable", "node": None,
                "note": "No configured node passed the server-side TCP health check."}
    return {"status": "ok", "node": node,
            "note": "Latency is measured from the API host, not from the customer's device."}
