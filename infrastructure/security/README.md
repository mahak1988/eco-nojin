# Infrastructure Security Stack

This folder contains the repository's multi-layer security infrastructure for secure access and network isolation.

## Security components

- `cloudflared/`: Cloudflare Tunnel gateway for secure perimeter access and Zero Trust ingress.
- `headscale/`: Self-hosted WireGuard identity management and mesh VPN.
- `openvpn/`: Containerized OpenVPN gateway for legacy VPN access.

## Goals

- Provide secure remote access without exposing internal services publicly.
- Support multi-tenant SaaS access for admin, developer, and tenant dashboards.
- Offer multiple secure transport layers so teams can choose the best fit.

## Usage

1. Review and customize each stack's environment variables and domain names.
2. Start services from the relevant subfolder using `docker compose up -d`.
3. Keep credentials and secrets outside source control.

## Important

- Do not commit Cloudflare credentials, VPN keys, or database passwords.
- Use `.gitignore` or secret management for `*.json`, `*.key`, and `*.env` files.
