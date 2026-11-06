# Deployment checklist

## Before deployment
- [ ] Provision five paid VPS instances in the target regions.
- [ ] Apply OS updates, firewall rules, SSH key-only access, and least-privilege administration.
- [ ] Install and configure Xray on each server.
- [ ] Configure TLS/Reality parameters securely; keep private keys outside Git.
- [ ] Set unique per-customer UUIDs and subscription expiry/revocation logic.
- [ ] Set real node FQDNs and probe ports in a private deployment configuration.
- [ ] Put the API behind HTTPS reverse proxy and configure backups/monitoring.

## Node health and latency
The current health endpoint checks TCP reachability from the API container. It is not an ICMP ping and does not represent latency experienced by all users. Production selection should be client-side: test candidate server endpoints from each client device, then choose the lowest-latency healthy node. Consider packet loss and sustained measurements, not a single sample.

## Billing and subscriptions
The repository intentionally has no payment processing yet. Choose a payment provider available in the operator's jurisdictions, verify signed webhooks, handle refunds and chargebacks, and only then activate/deactivate entitlements. Never trust a success redirect from the browser as proof of payment.
