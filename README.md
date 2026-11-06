# DjShrek VPN

Global VPN subscription platform with five paid, globally reachable exit nodes.

> **Status: development scaffold (v0.3).** Account registration/login, token-based subscription delivery, per-subscription VLESS credential storage, a landing page, and node health API are implemented. This is not yet a production VPN: real VPS nodes, Xray inbounds, payment webhooks, and deployment credentials must still be configured and tested.

## Product scope

- Public landing page and account API
- Five global VPN nodes: Germany, Finland, Netherlands, Poland, United States
- Server-side node health checks and latency fallback
- Customer accounts and bearer-token authentication
- Admin-issued subscriptions with individual five-node VLESS credential sets
- Base64 VLESS subscription response for compatible clients such as Happ
- Admin subscription revocation
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

Set `NODE_CONFIG_JSON` privately at deployment with hostnames and probe ports for node IDs `de-1`, `fi-1`, `nl-1`, `pl-1`, and `us-1`. Never put VLESS URIs or private credentials in the public node catalog or Git.

For each customer, provision five unique VLESS client identities in Xray (one per node), then pass those five URIs to the admin subscription issuance endpoint. The application stores the five URIs against that customer's subscription, not as a shared fleet-wide credential. Actual Xray provisioning/revocation automation is still to be implemented and must be validated before production.

The server-side probe measures TCP reachability and latency from the API host. It is not the customer's real ping. For global users, configure client-side latency testing in the client or app and select the lowest-latency healthy endpoint from the device.

## Accounts and subscriptions

See [API documentation](docs/API.md). Registration and login return short-lived bearer tokens. Admin subscription issuance is protected by `DJSHREK_ADMIN_API_KEY`. Subscription URLs are bearer secrets: do not expose them in logs, screenshots, analytics, or public issue trackers.

## Billing status

Payment is intentionally disabled. A production payment provider must be selected and its signed webhook implemented before money is accepted or paid subscriptions are activated. Never grant access based only on a browser redirect.

## Production checklist

- [ ] Provision and harden five paid VPS instances.
- [ ] Install and configure Xray on each node; validate inbound reachability.
- [ ] Automate unique per-user UUID provisioning and removal across all five Xray nodes.
- [ ] Set strong secrets through the hosting provider's secret manager.
- [ ] Use PostgreSQL, automated backups, TLS, firewalling, rate limits, and monitoring.
- [ ] Implement password reset, email verification, account deletion, and audit logging.
- [ ] Implement payment provider signed webhooks, refunds, cancellations, and reconciliation.
- [ ] Test Happ import, expiry, revocation, failover, and latency from multiple continents.
- [ ] Publish privacy policy, terms, support process, and applicable legal notices.
