import os
import re
from pathlib import Path

def scan_for_secrets(root_dir="."):
    """Deep scans codebase for hardcoded secrets and API keys."""
    root_path = Path(root_dir).resolve()
    
    # High-confidence patterns for common secrets
    patterns = {
        "AWS Access Key": r"AKIA[0-9A-Z]{16}",
        "AWS Secret Key": r"(?i)aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]",
        "Generic API Key": r"(?i)(api_key|apikey|openai_api_key)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
        "Generic Secret": r"(?i)(secret|password|passwd|pwd)\s*=\s*['\"][^\s'\"]{8,}['\"]",
        "Private Key Block": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,255}",
        "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        "Google API Key": r"AIza[0-9A-Za-z_\-]{35}",
        "JWT Secret": r"(?i)(jwt_secret|secret_key)\s*=\s*['\"][^'\"]{16,}['\"]"
    }
    
    # Extensions to scan
    scan_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.env', '.json', '.yml', '.yaml', '.config', '.cfg', '.ini', '.sh'}
    skip_dirs = {'.git', 'node_modules', '.venv', '__pycache__', '.next', 'dist', 'build'}
    
    findings = []
    
    print(f"[*] Initiating deep security scan on {root_path}...")
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            
            # Skip binary files and non-code files
            if file_path.suffix.lower() not in scan_extensions and not file_path.name.startswith('.env'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for secret_type, pattern in patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Self-exclusion to prevent false positives from this script itself
                            if 'deep_secret_scanner.py' in str(file_path):
                                continue
                                
                            findings.append({
                                "type": secret_type,
                                "file": str(file_path.relative_to(root_path)),
                                "match": match.group(0)[:15] + "..." # Truncate for safety
                            })
            except Exception:
                pass
                
    # Report
    print("\n" + "="*70)
    print(f"🔒 SECURITY AUDIT REPORT: {len(findings)} potential secrets detected")
    print("="*70)
    
    if not findings:
        print("✅ CLEAN: No obvious hardcoded secrets were found.")
    else:
        # Group by file for better readability
        grouped = {}
        for f in findings:
            grouped.setdefault(f['file'], []).append(f)
            
        for file_path, secrets in grouped.items():
            print(f"\n📁 File: {file_path}")
            for s in secrets:
                print(f"   ⚠️  [{s['type']}] -> {s['match']}")
                
        print("\n🚨 CRITICAL ACTION PLAN:")
        print("  1. ROTATE: Immediately revoke these keys in their respective dashboards.")
        print("  2. REFRESH: Generate new keys and store them in environment variables (.env).")
        print("  3. PROTECT: Ensure .env is in your .gitignore and NEVER commit it.")
        
    print("="*70 + "\n")

if __name__ == "__main__":
    scan_for_secrets()