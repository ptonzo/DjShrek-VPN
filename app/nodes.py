"""Configured node catalog and best-effort server-side health checks.

Replace placeholder hosts and probe ports after provisioning the VPS fleet.
Never put private connection credentials in this public catalog.
"""
from __future__ import annotations
import asyncio
import socket
import time
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

NODES = [
    Node("de-1", "Germany", "Frankfurt", "de-1.example.invalid", 443),
    Node("fi-1", "Finland", "Helsinki", "fi-1.example.invalid", 443),
    Node("nl-1", "Netherlands", "Amsterdam", "nl-1.example.invalid", 443),
    Node("pl-1", "Poland", "Warsaw", "pl-1.example.invalid", 443),
    Node("us-1", "United States", "New York", "us-1.example.invalid", 443),
]

async def probe(node: Node) -> dict:
    start = time.perf_counter()
    try:
        await asyncio.wait_for(
            asyncio.to_thread(_tcp_probe, node.host, node.probe_port),
            timeout=settings.healthcheck_timeout_seconds,
        )
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {**asdict(node), "online": True, "latency_ms": latency}
    except Exception:
        return {**asdict(node), "online": False, "latency_ms": None}

def _tcp_probe(host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=settings.healthcheck_timeout_seconds):
        pass

async def all_node_status() -> list[dict]:
    return await asyncio.gather(*(probe(n) for n in NODES))

async def select_server_side_fallback() -> Optional[dict]:
    """Select lowest measured API-to-node TCP latency; not user's actual ping."""
    statuses = await all_node_status()
    online = [n for n in statuses if n["online"] and n["latency_ms"] is not None]
    return min(online, key=lambda n: n["latency_ms"]) if online else None
