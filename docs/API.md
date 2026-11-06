# API overview

Base URL: `http://localhost:8000`

- `GET /api/health` — health check.
- `GET /api/nodes` — TCP health checks from the API host.
- `GET /api/nodes/recommended` — API-host latency fallback only.
- `POST /api/auth/register` — create a user account.
- `POST /api/auth/login` — obtain a 24-hour bearer access token.
- `GET /api/me` — current account and subscription metadata.
- `POST /api/admin/subscriptions` — admin-key protected subscription issuance.
- `GET /s/{subscription_token}` — base64-encoded VLESS URI list for supported clients.

## Register

```json
{"email":"user@example.com","password":"use-a-long-unique-password"}
```

## Login

```json
{"email":"user@example.com","password":"use-a-long-unique-password"}
```

## Admin subscription issuance

Send `X-Admin-Key: <DJSHREK_ADMIN_API_KEY>` and JSON:

```json
{"email":"user@example.com","days":30}
```

The one-time response contains a secret subscription URL. Store it securely; do not publish it or place it in logs. The current implementation can issue an account entitlement, but actual VLESS links are returned only for nodes whose private connection settings have been configured in deployment environment. Payment is not yet connected.
