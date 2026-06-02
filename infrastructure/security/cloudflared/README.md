# Cloudflared Security Stack

This folder contains configuration and deployment notes for a Cloudflare Tunnel setup.

## Purpose
- Secure access to internal apps without exposing them directly to the public internet.
- Provide zero-trust identity and access control via Cloudflare Access.
- Route SaaS dashboard services through Cloudflare Tunnel.

## Files
- `config.yml`: Tunnel configuration and ingress rules.
- `docker-compose.yml`: Docker Compose service for Cloudflared.
- `credentials.json`: Cloudflare tunnel credentials (must be created separately and not committed).
- `README.md`: Setup and startup instructions.

## Startup

1. Place your Cloudflare tunnel credentials in `credentials.json`.
2. Edit `config.yml` and replace the placeholder tunnel ID and hostnames with your actual values.
3. Run:

```bash
docker compose up -d
```

## Notes

- Adjust service ports to match your local app ports.
- Keep `credentials.json` out of version control.
