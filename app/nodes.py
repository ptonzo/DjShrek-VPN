"""Five-node catalog and server-side TCP health checks.

Set NODE_CONFIG_JSON privately at deployment. Example shape:
[{"id":"de-1","host":"vpn-de.example.com","probe_port":443,"vless_uri":"vless://..."}]
Never commit actual hostnames or client credentials to this public repository.
"""
from __future__ import annotations
import asyncio, json, socket, time
from dataclasses import asdict, dataclass
from typing import Optional
from .config import settings

@dataclass(frozen=True)
class Node:
    id: str
    country: str
    city: str
    host: str
    probe_port: int
    protocol: str = "vless-reality"

DEFAULT_NODES = [
    Node("de-1", "Germany", "Frankfurt", "de-1.example.invalid", 443),
    Node("fi-1", "Finland", "Helsinki", "fi-1.example.invalid", 443),
    Node("nl-1", "Netherlands", "Amsterdam", "nl-1.example.invalid", 443),
    Node("pl-1", "Poland", "Warsaw", "pl-1.example.invalid", 443),
    Node("us-1", "United States", "New York", "us-1.example.invalid", 443),
]

def configured_nodes() -> list[Node]:
    try:
        configs = json.loads(settings.node_config_json)
        if not isinstance(configs, list): return DEFAULT_NODES
        by_id = {x.get("id"): x for x in configs if isinstance(x, dict)}
        return [Node(n.id, n.country, n.city,
                     str(by_id.get(n.id, {}).get("host", n.host)),
                     int(by_id.get(n.id, {}).get("probe_port", n.probe_port)))
                for n in DEFAULT_NODES]
    except (ValueError, TypeError):
        return DEFAULT_NODES

NODES = DEFAULT_NODES

async def probe(node: Node) -> dict:
    start = time.perf_counter()
    configured = not node.host.endswith(".example.invalid")
    if not configured:
        return {**asdict(node), "online": False, "configured": False, "latency_ms": None}
    try:
        await asyncio.wait_for(asyncio.to_thread(_tcp_probe, node.host, node.probe_port),
                               timeout=settings.healthcheck_timeout_seconds)
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {**asdict(node), "online": True, "configured": True, "latency_ms": latency}
    except Exception:
        return {**asdict(node), "online": False, "configured": True, "latency_ms": None}

def _tcp_probe(host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=settings.healthcheck_timeout_seconds):
        pass

async def all_node_status() -> list[dict]:
    nodes = configured_nodes()
    return await asyncio.gather(*(probe(n) for n in nodes))

async def select_server_side_fallback() -> Optional[dict]:
    """API-to-node TCP latency fallback; client-side testing is needed for true user ping."""
    statuses = await all_node_status()
    online = [n for n in statuses if n["online"] and n["latency_ms"] is not None]
    return min(online, key=lambda n: n["latency_ms"]) if online else None
