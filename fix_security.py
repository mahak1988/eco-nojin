#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 Econojin Security Fixer
بررسی و رفع مشکلات امنیتی بحرانی
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# فایل‌های بحرانی
CRITICAL_FILES = [
    "scripts/build_phase4_mega.py",
    "contracts/scripts/deploy.js",
    "contracts/scripts/deploy_local.js",
    ".github/workflows/deploy.yml"
]

# الگوهای مشکوک
SECRET_PATTERNS = [
    r'(token|password|secret|api_key)\s*[:=]\s*["\']([^"\']{8,})["\']',
    r'(token|password|secret|api_key)\s*[:=]\s*[a-zA-Z0-9]{20,}'
]

def scan_file(file_path: Path) -> list:
    """اسکن یک فایل برای secrets"""
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            for pattern in SECRET_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # بررسی اینکه این یک متغیر محیطی نیست
                    if "process.env" not in line and "os.getenv" not in line:
                        findings.append({
                            "line": i,
                            "content": line.strip(),
                            "type": match.group(1),
                            "value": match.group(2) if len(match.groups()) > 1 else "HIDDEN"
                        })
    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")
    
    return findings

def create_env_example():
    """ایجاد فایل .env.example"""
    env_example = ROOT / ".env.example"
    if not env_example.exists():
        content = """# Econojin Environment Variables
# این فایل را به .env کپی کنید و مقادیر واقعی را وارد کنید

# Database
DATABASE_URL=sqlite+aiosqlite:///./econojin.db

# API Keys (هرگز مقادیر واقعی را commit نکنید)
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Blockchain
PRIVATE_KEY=your_private_key_here
RPC_URL=https://mainnet.infura.io/v3/your_project_id

# Security
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here

# External Services
TWILIO_SID=your_twilio_sid_here
TWILIO_TOKEN=your_twilio_token_here
"""
        env_example.write_text(content, encoding="utf-8")
        print(f"✅ Created: {env_example}")

def add_to_gitignore():
    """افزودن فایل‌های حساس به .gitignore"""
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        additions = [
            "\n# Security - Secrets",
            ".env",
            ".env.local",
            ".env.production",
            "*.pem",
            "*.key",
            "secrets.json",
        ]
        
        new_additions = [a for a in additions if a not in content]
        if new_additions:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(new_additions))
            print(f"✅ Updated .gitignore with {len(new_additions)} entries")

def main():
    print("🔒 Econojin Security Fixer")
    print("=" * 60)
    
    total_findings = 0
    
    # اسکن فایل‌های بحرانی
    print("\n[1/3] Scanning critical files...")
    for file_rel in CRITICAL_FILES:
        file_path = ROOT / file_rel
        if file_path.exists():
            findings = scan_file(file_path)
            if findings:
                print(f"\n🔴 {file_rel}:")
                for f in findings:
                    print(f"   Line {f['line']}: {f['type']} = {f['value'][:20]}...")
                    print(f"   → {f['content'][:80]}")
                total_findings += len(findings)
            else:
                print(f"✅ {file_rel}: No secrets found")
        else:
            print(f"⚠️ File not found: {file_rel}")
    
    # ایجاد .env.example
    print("\n[2/3] Creating .env.example...")
    create_env_example()
    
    # به‌روزرسانی .gitignore
    print("\n[3/3] Updating .gitignore...")
    add_to_gitignore()
    
    # خلاصه
    print("\n" + "=" * 60)
    if total_findings > 0:
        print(f"⚠️ Found {total_findings} potential secrets")
        print("\n📝 Recommended actions:")
        print("   1. Replace hardcoded secrets with environment variables")
        print("   2. Use process.env.VARIABLE_NAME (Node.js) or os.getenv('VARIABLE_NAME') (Python)")
        print("   3. Never commit .env files to version control")
        print("   4. Rotate any exposed secrets immediately")
    else:
        print("✅ No critical security issues found!")
    print("=" * 60)

if __name__ == "__main__":
    main()