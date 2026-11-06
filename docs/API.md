# API overview

Base URL: `http://localhost:8000`

- `GET /api/health` — health check.
- `GET /api/nodes` — TCP health checks from the API host.
- `GET /api/nodes/recommended` — API-host latency fallback only.
- `POST /api/auth/register` — create a user account.
- `POST /api/auth/login` — obtain a 24-hour bearer access token.
- `GET /api/me` — current account and subscription metadata.
- `POST /api/admin/subscriptions` — admin-key protected subscription issuance with five individual VLESS URIs.
- `POST /api/admin/subscriptions/{id}/revoke` — revoke a subscription.
- `GET /s/{subscription_token}` — base64-encoded VLESS URI list for compatible clients such as Happ.

## Register / login

```json
{"email":"user@example.com","password":"use-a-long-unique-password"}
```

Passwords must be at least 12 characters. The response includes a 24-hour bearer token.

## Issue a subscription

Send `X-Admin-Key: <DJSHREK_ADMIN_API_KEY>` and JSON containing the registered customer's email, duration, and five per-customer VLESS URIs:

```json
{
  "email": "user@example.com",
  "days": 30,
  "nodes": [
    {"node_id":"de-1","vless_uri":"vless://CUSTOMER_UUID@de.example:443?..."},
    {"node_id":"fi-1","vless_uri":"vless://CUSTOMER_UUID@fi.example:443?..."},
    {"node_id":"nl-1","vless_uri":"vless://CUSTOMER_UUID@nl.example:443?..."},
    {"node_id":"pl-1","vless_uri":"vless://CUSTOMER_UUID@pl.example:443?..."},
    {"node_id":"us-1","vless_uri":"vless://CUSTOMER_UUID@us.example:443?..."}
  ]
}
```

The five URIs must be generated for that customer and correspond to unique client identities provisioned on the five Xray nodes. The response contains a secret subscription URL. Store and share it securely. Revocation disables that subscription URL, but does not itself remove UUIDs from Xray; automate that server-side action before production.

## Billing

`GET /api/billing/status` reports that billing is disabled. Payment provider credentials and a verified signed webhook handler must be implemented before accepting payments.
