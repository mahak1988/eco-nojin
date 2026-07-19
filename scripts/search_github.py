#!/usr/bin/env python3
"""Search GitHub for high-quality reference repositories matching our project structure."""
import urllib.request
import json
import sys
import os

QUERIES = [
    "FastAPI+React+PostgreSQL+monorepo+production",
    "FastAPI+SQLAlchemy+async+postgres+boilerplate",
    "React+Vite+Tailwind+TypeScript+dashboard+agriculture",
    "FastAPI+agriculture+farming+api",
    "FastAPI+supabase+react+template",
    "React+Vite+FastAPI+full-stack+monorepo+production",
    "FastAPI+JWT+OTP+authentication+boilerplate",
    "FastAPI+alembic+migrations+postgres+production",
    "React+TypeScript+TanStack+Query+dashboard+template",
    "Vite+React+i18n+multi-language+dashboard"
]

for query in QUERIES:
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page=5"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "econojin-research"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            print(f"\n{'='*80}")
            print(f"QUERY: {query}")
            print(f"{'='*80}")
            for r in data.get("items", []):
                desc = (r["description"] or "N/A")[:100]
                print(f"  ⭐ {r['stargazers_count']:>5} | {r['full_name']:<45} | {desc}")
                print(f"     {r['html_url']}")
            if not data.get("items"):
                print("  (no results)")
    except Exception as e:
        print(f"  Error: {e}")

# Now clone/search for specific high-value repos
print("\n\n" + "="*80)
print("TOP REPOSITORIES TO EXPLORE FOR FILE INTEGRATION")
print("="*80)

TARGETS = [
    {
        "repo": "tobymao/sqlglot",
        "reason": "SQL parser/transpiler - useful for query standardization",
        "files": []
    },
    {
        "repo": "fastapi/full-stack-fastapi-template",
        "reason": "Official FastAPI full-stack template with PostgreSQL, Celery, Traefik",
        "files": [
            "backend/app/core/config.py",
            "backend/app/core/security.py",
            "backend/app/core/database.py",
            "backend/app/crud/base.py",
            "backend/app/schemas/",
            "backend/app/models/",
            "backend/app/api/deps.py",
            "backend/alembic/env.py",
            "docker-compose.yml",
            ".env.example"
        ]
    },
    {
        "repo": "zhanymkanov/fastapi-best-practices",
        "reason": "FastAPI best practices guide - project structure, error handling, testing",
        "files": []
    },
    {
        "repo": "AbdullahAlfaraj/Auto-README",
        "reason": "README generation template",
        "files": []
    },
    {
        "repo": "RealToughCandy/fastapi-production-setup",
        "reason": "Production-ready FastAPI setup with testing, CI/CD",
        "files": [
            "app/config.py",
            "app/database.py",
            "tests/"
        ]
    },
    {
        "repo": "goldbergyoni/nodebestpractices",
        "reason": "Node.js best practices - applicable to frontend structure",
        "files": []
    },
    {
        "repo": "microsoft/TypeScript-React-Starter",
        "reason": "TypeScript React patterns",
        "files": []
    },
    {
        "repo": "alan2207/bulletproof-react",
        "reason": "React architecture best practices",
        "files": [
            "src/api/",
            "src/components/",
            "src/config/",
            "src/hooks/",
            "src/lib/",
            "src/providers/",
            "src/routes/",
            "src/test/",
            "src/types/"
        ]
    },
    {
        "repo": "appwrite/appwrite",
        "reason": "Backend-as-a-service - reference for auth, storage, database structure",
        "files": []
    },
    {
        "repo": "withastro/astro",
        "reason": "Web framework - reference for multi-language support",
        "files": []
    },
    {
        "repo": "n8n-io/n8n",
        "reason": "Workflow automation - reference for AI agent workflows",
        "files": []
    }
]

for t in TARGETS:
    print(f"\n{'─'*80}")
    print(f"📦 {t['repo']}")
    print(f"   📝 {t['reason']}")
    if t['files']:
        print(f"   📋 Key files to examine:")
        for f in t['files']:
            print(f"      - {f}")

print("\n\nTo clone a repo for file analysis:")
print("  git clone --depth 1 https://github.com/ORGANIZATION/REPO.git repos/REPO")
print("  # Then compare files between repos/REPO and your project")