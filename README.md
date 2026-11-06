# DjShrek VPN

Global VPN subscription platform with five paid, globally reachable exit nodes.

> **Status: bootstrap scaffold.** This repository does not contain deployed VPN servers, working credentials, payment-provider credentials, or a production-ready subscription service yet.

## Product scope

- Public landing page and account dashboard
- Telegram bot integration
- VLESS client subscription delivery for compatible clients such as Happ
- Five paid VPN nodes in Germany, Finland, Netherlands, Poland, and the United States
- Server health checks and latency-aware node selection
- Subscription lifecycle and payment-provider integration (provider adapter to be configured)
- QR-code generation for client setup

## Architecture

- **API:** FastAPI, Python 3.12
- **Web:** static responsive landing page (initial scaffold)
- **Database:** PostgreSQL (production); SQLite-friendly local bootstrap can be added
- **Node layer:** Xray/VLESS Reality on separately provisioned VPS instances
- **Operations:** Docker Compose and environment-based configuration

## Important networking note

A server cannot reliably determine the best node for every client by measuring latency from the API host. The API exposes node health and a selection endpoint as a first-pass fallback. The eventual client flow should measure latency from the user's device (or use client-side URL-test features) and choose the best reachable node. No ping values are hard-coded or represented as live measurements.

## Quick start

1. Copy `.env.example` to `.env` and set a strong `APP_SECRET`.
2. Start the API: `docker compose up --build`.
3. Open `http://localhost:8000` and `http://localhost:8000/docs`.

The demo node catalog is configuration only. Set real hostnames, probe ports, and Xray inbounds after provisioning the five VPS nodes.

## Security

- Never commit `.env`, private keys, Reality keys, client UUIDs, payment secrets, bot tokens, or production subscription URLs.
- Public repository visibility is intentional; customer data and server credentials must stay in private infrastructure.
- Before charging customers, implement and test payment webhooks, subscription revocation, abuse handling, privacy policy, terms, and applicable local legal requirements.

## Planned milestones

1. Bootstrap API and public landing page.
2. Provision and harden five paid VPS nodes.
3. Configure Xray and issue per-user VLESS credentials.
4. Implement customer accounts, subscriptions, and payment webhooks.
5. Generate secure Happ-compatible subscription links and QR codes.
6. Add client-side latency testing, monitoring, alerts, and production deployment.
