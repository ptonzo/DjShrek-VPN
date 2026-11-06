# DjShrek VPN

Global VPN subscription platform with five paid, globally reachable exit nodes.

> **Status: development scaffold (v0.2).** Account registration/login, token-based subscription delivery endpoints, a landing page, and node health API are implemented. This is not yet a production VPN: real VPS nodes, Xray inbounds, billing webhooks, and deployment credentials must still be configured and tested.

## Product scope

- Public landing page and account API
- Five global VPN nodes: Germany, Finland, Netherlands, Poland, United States
- Server-side node health checks and latency fallback
- Customer accounts and bearer-token authentication
- Admin-issued subscription entitlements
- Base64 VLESS subscription response for compatible clients such as Happ
- Docker Compose deployment foundation

## Stack

- FastAPI / Python 3.12
- SQLite for bootstrap; use managed PostgreSQL before production scale
- Xray/VLESS Reality on separately provisioned VPS instances
- Docker Compose and environment-based configuration

## Quick start

```bash
cp .env.example .env
# Set APP_SECRET and DJSHREK_ADMIN_API_KEY to unique random values
docker compose up --build
```

Open `http://localhost:8000` and `http://localhost:8000/docs`.

## Provisioning the five nodes

Set `NODE_CONFIG_JSON` as a private environment variable in the deployment environment. It must be a JSON array with entries for the fixed IDs `de-1`, `fi-1`, `nl-1`, `pl-1`, and `us-1`. Each entry needs `host`, `probe_port`, and a complete customer-facing `vless_uri`. Keep this configuration out of Git. The URI must contain valid server-side Xray parameters and must be tested with Happ before customer distribution.

The server-side probe measures TCP reachability and latency from the API host. It is not the customer's real ping. For global users, configure client-side latency testing in the client or app and select the lowest-latency healthy endpoint from the device.

## Accounts and subscriptions

See [API documentation](docs/API.md). Registration and login return short-lived bearer tokens. Admin subscription issuance is protected by `DJSHREK_ADMIN_API_KEY`. Subscription URLs are bearer secrets: do not expose them in logs, screenshots, analytics, or public issue trackers.

## Billing status

Payment is intentionally disabled. A production payment provider must be selected and its signed webhook implemented before money is accepted or paid subscriptions are activated. Never grant access based only on a browser redirect.

## Production checklist

- [ ] Provision and harden five paid VPS instances.
- [ ] Install and configure Xray on each node; validate inbound reachability.
- [ ] Set strong secrets through the hosting provider's secret manager.
- [ ] Use PostgreSQL, automated backups, TLS, firewalling, rate limits, and monitoring.
- [ ] Implement password reset, email verification, account deletion, and audit logging.
- [ ] Implement payment provider signed webhooks, refunds, cancellations, and reconciliation.
- [ ] Add per-user VLESS UUID generation and automated Xray client provisioning/revocation.
- [ ] Test Happ import, expiry, revocation, failover, and latency from multiple continents.
- [ ] Publish privacy policy, terms, support process, and applicable legal notices.
