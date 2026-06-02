# Headscale Security Stack

This folder contains configuration and deployment notes for self-hosted WireGuard identity management using Headscale.

## Purpose
- Manage WireGuard keys and authorization centrally.
- Support multi-tenant VPN access for developer/admin teams.
- Enable secure mesh networking for distributed services.

## Files
- `docker-compose.yml`: Container deployment for Headscale and Postgres.
- `config.yaml`: Headscale server configuration.
- `env.example`: Example environment variables.
- `README.md`: Quickstart and usage notes.

## Startup

1. Copy `env.example` to `.env` and fill in secrets.
2. Create local directories:
   - `data/`
3. Run:

```bash
docker compose up -d
```

4. Initialize Headscale users and nodes using the Headscale CLI or API.

## Notes

- The database is exposed on port `5433` locally.
- The Headscale web interface listens on port `9000`.
- Keep secrets out of version control and use strong, random values.
