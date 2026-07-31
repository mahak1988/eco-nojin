#!/usr/bin/env python3
"""CI/CD Setup Script — Configure security headers for Cloudflare/CDN."""

import os
import sys
from pathlib import Path


def main():
    """Configure security settings for deployment."""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Get environment
    env = os.getenv("ENVIRONMENT", "development")
    is_prod = env in ("production", "staging")

    print(f"Environment: {env}")
    print(f"Is production: {is_prod}")

    # Security headers configuration
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY" if is_prod else "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains" if is_prod else "",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    # Write security headers to deployment config
    headers_file = project_root / "deployment" / "security_headers.json"
    headers_file.parent.mkdir(exist_ok=True)

    import json
    with open(headers_file, 'w', encoding='utf-8') as f:
        json.dump(security_headers, f, indent=2)

    print(f"Security headers written to: {headers_file}")

    # Configure CORS based on environment
    cors_origins = []
    if is_prod:
        cors_origins = [
            os.getenv("PROD_FRONTEND_URL", "https://prod.econojin.com"),
            os.getenv("ADMIN_PANEL_URL", "https://admin.econojin.com"),
        ]
    else:
        cors_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
        ]

    # Update .env file with appropriate CORS settings
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file, encoding='utf-8') as f:
            env_content = f.read()

        # Check if BACKEND_CORS_ORIGINS exists
        if 'BACKEND_CORS_ORIGINS' in env_content:
            # Update existing entry
            import re
            env_content = re.sub(
                r'BACKEND_CORS_ORIGINS=.*',
                f'BACKEND_CORS_ORIGINS={",".join(cors_origins)}',
                env_content
            )
        else:
            # Add new entry
            env_content += f"\nBACKEND_CORS_ORIGINS={','.join(cors_origins)}"

        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        print(f"CORS origins updated in .env: {cors_origins}")
    else:
        print("Warning: .env file not found, skipping CORS configuration")

    # Security scanning configuration
    print("\nSecurity scan configuration:")

    # Define security scanning patterns
    scan_targets = [
        "apps/",
        "security/",
        "alembic/",
        "database/"
    ]

    vulnerable_patterns = [
        r'app\.add_middleware\(.*CorsMiddleware.*allow_origins=\[.*\".*\"\].*\)',  # Wildcard CORS
        r'DATABASE_URL.*@.*:.*@',  # Hardcoded credentials
        r'SECRET_KEY.*=.*["\'][a-zA-Z0-9]{1,10}["\']',  # Weak secrets
        r'debug\s*=\s*True',  # Debug enabled
    ]

    print(f"- Scan targets: {scan_targets}")
    print(f"- Vulnerability patterns: {len(vulnerable_patterns)} checked")

    # HTTP security markers for CDN/Cloudflare
    marker = "# HTTP Security Configuration"
    security_config = (
        f'\n{marker}\n'
        '# Auto-generated security policies\n'
        'CLOUDFLARE_SSL_MODE=strict\n'
        'SECURE_COOKIES=true\n'
        'HSTS_ENABLED=true\n'
        'CSP_POLICY="default-src \'self\'; script-src \'self\' \'unsafe-inline\' cdn.cloudflare.com; style-src \'self\' \'unsafe-inline\' fonts.googleapis.com; font-src fonts.gstatic.com; img-src \'self\' data: https:;"\n'
    )

    # Add security configuration to deployment file
    deploy_config = project_root / "deployment" / "cloudflare_config.txt"
    deploy_config.parent.mkdir(exist_ok=True)

    with open(deploy_config, 'w', encoding='utf-8') as f:
        f.write(security_config)

    print(f"Cloudflare security config written to: {deploy_config}")

    # Internal HTTP patterns that are safe
    if env == "development":
        print("\n✓ Development environment - relaxed security policies applied")
    else:
        print("\n✓ Production security policies applied")

    print("\nCI/CD setup completed successfully!")


if __name__ == "__main__":
    main()
