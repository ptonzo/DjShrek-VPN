# Deployment checklist

## Before deployment
- [ ] Provision five paid VPS instances in Germany, Finland, Netherlands, Poland, and the United States.
- [ ] Apply OS updates, firewall rules, SSH key-only access, and least-privilege administration.
- [ ] Install and configure Xray on each server.
- [ ] Configure VLESS Reality parameters securely; keep private keys outside Git.
- [ ] Configure unique per-customer UUIDs on all five Xray servers.
- [ ] Set node hostnames and probe ports in private `NODE_CONFIG_JSON` deployment configuration.
- [ ] Put the API behind HTTPS reverse proxy and configure backups/monitoring.

## Customer provisioning
For every customer, generate a distinct UUID/client identity per node, apply it to each Xray server, and submit the five resulting VLESS URIs to the admin subscription API. Store the subscription URL as a secret. On cancellation or expiry, revoke the subscription and remove/disable the matching client identities on all nodes. The current application revokes its subscription token but does not yet automate Xray-side client removal.

## Node health and latency
The current health endpoint checks TCP reachability from the API container. It is not ICMP ping and does not represent latency experienced by all users. Production selection should be client-side: test candidate server endpoints from each client device, then choose the lowest-latency healthy node. Consider packet loss and sustained measurements, not a single sample.

## Billing and subscriptions
Payment is intentionally disabled. Select a supported provider, verify signed webhooks, handle refunds and chargebacks, and only then activate entitlements. Never trust a success redirect from the browser as proof of payment.
