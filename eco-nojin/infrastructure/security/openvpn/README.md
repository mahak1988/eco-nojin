# OpenVPN Security Stack

This folder contains configuration for an OpenVPN-based access gateway.

## Purpose
- Provide an audited VPN gateway for remote access.
- Support site-to-site or user-based VPN connectivity.
- Complement Cloudflare Tunnel and Headscale for multi-layer security.

## Files
- `docker-compose.yml`: Container deployment for OpenVPN.
- `server.conf`: Server configuration template.
- `env.example`: Example environment variables.
- `README.md`: Startup and provisioning notes.

## Startup

1. Copy `env.example` to `.env` and update values as needed.
2. Initialize the OpenVPN PKI and generate server files:

```bash
docker compose run --rm openvpn ovpn_genconfig -u $OVPN_SERVER

docker compose run --rm openvpn ovpn_initpki
```

3. Start the service:

```bash
docker compose up -d
```

4. Generate a client profile:

```bash
docker compose run --rm openvpn easyrsa build-client-full CLIENTNAME nopass

docker compose run --rm openvpn ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn
```

## Notes

- The OpenVPN UDP port is exposed on `1194`.
- The generated client profile is stored locally when using `ovpn_getclient`.
- Do not commit `ovpn-data/` or generated certificates.
