"""Payment integration boundary.

Do not activate subscriptions from browser redirects. A payment provider adapter must
verify the provider's signed webhook before granting or extending an entitlement.
No payment provider is enabled in this bootstrap.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class BillingStatus:
    enabled: bool = False
    provider: str = "not_configured"

def billing_status() -> dict:
    return {"enabled": False, "provider": "not_configured",
            "message": "Payment provider credentials and signed webhook handler are required."}
