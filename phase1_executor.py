#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Econojin Phase 1 Executor
اجرای خودکار اقدامات فوری مرحله اول (0-1 هفته)
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()

def run_command(cmd: str, cwd: Path = ROOT) -> bool:
    """اجرای دستور shell"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"⚠️ Warning: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_gitignore():
    """به‌روزرسانی فایل .gitignore"""
    print("\n[1/6] Updating .gitignore...")
    gitignore = ROOT / ".gitignore"
    
    additions = """
# === Econojin Security & Optimization ===

# Environment Variables
.env
.env.local
.env.production
*.env

# Large Model Files
*.safetensors
*.bin
*.pt
*.pth
models/all-MiniLM-L6-v2/

# Package Manager Cache
.pnpm-store/
node_modules/
__pycache__/
*.pyc

# IDE and OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Build and Dist
.next/
dist/
build/
*.log

# Backup Files
*_backup_*/
*.bak
*.tmp
"""
    
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if "Econojin Security" not in content:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write(additions)
            print("✅ .gitignore updated")
        else:
            print("ℹ️ .gitignore already updated")
    else:
        gitignore.write_text(additions, encoding="utf-8")
        print("✅ .gitignore created")

def create_model_downloader():
    """ایجاد اسکریپت دانلود مدل"""
    print("\n[2/6] Creating model downloader...")
    script_path = ROOT / "scripts" / "download_model.py"
    script_path.parent.mkdir(exist_ok=True)
    
    content = '''#!/usr/bin/env python3
"""Download ML model from Hugging Face Hub at runtime"""
from huggingface_hub import snapshot_download
from pathlib import Path

def download_model():
    model_dir = Path("models/all-MiniLM-L6-v2")
    if not model_dir.exists():
        print("📥 Downloading model from Hugging Face...")
        snapshot_download(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )
        print("✅ Model downloaded successfully")
    else:
        print("✅ Model already exists")

if __name__ == "__main__":
    download_model()
'''
    
    script_path.write_text(content, encoding="utf-8")
    print(f"✅ Created: {script_path}")

def remove_large_files_from_git():
    """خارج‌سازی فایل‌های بزرگ از Git"""
    print("\n[3/6] Removing large files from Git tracking...")
    
    large_files = [
        "models/all-MiniLM-L6-v2/model.safetensors",
    ]
    
    for file_path in large_files:
        full_path = ROOT / file_path
        if full_path.exists():
            run_command(f'git rm --cached "{file_path}"')
            print(f"✅ Removed from Git: {file_path}")
    
    run_command('git commit -m "chore: remove large model files from Git tracking"')

def cleanup_backup_files():
    """پاک‌سازی فایل‌های بک‌آپ قدیمی"""
    print("\n[4/6] Cleaning up old backup files...")
    
    backup_dirs = list(ROOT.glob("*_backup_*"))
    removed = 0
    
    for backup_dir in backup_dirs:
        if backup_dir.is_dir():
            mtime = datetime.fromtimestamp(backup_dir.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            
            if age_days > 30:
                import shutil
                shutil.rmtree(backup_dir)
                print(f"🗑️ Removed: {backup_dir.name} ({age_days} days old)")
                removed += 1
    
    print(f"✅ Removed {removed} old backup directories")

def cleanup_pnpm_cache():
    """پاک‌سازی کش pnpm"""
    print("\n[5/6] Cleaning pnpm cache...")
    run_command("pnpm store prune")
    print("✅ pnpm cache cleaned")

def create_env_example():
    """ایجاد فایل .env.example"""
    print("\n[6/6] Creating .env.example...")
    env_example = ROOT / ".env.example"
    
    if not env_example.exists():
        content = """# Econojin Environment Variables Template
# Copy this file to .env and fill in your actual values

# === Database ===
DATABASE_URL=sqlite+aiosqlite:///./econojin.db
# PostgreSQL (for production):
# DATABASE_URL=postgresql://user:password@localhost:5432/econojin

# === API Keys ===
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# === Blockchain ===
PRIVATE_KEY=your_private_key_here
RPC_URL=https://mainnet.infura.io/v3/your_project_id

# === Security ===
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here

# === External Services ===
TWILIO_SID=your_twilio_sid_here
TWILIO_TOKEN=your_twilio_token_here

# === Application ===
DEBUG=true
HOST=127.0.0.1
PORT=8000
"""
        env_example.write_text(content, encoding="utf-8")
        print(f"✅ Created: {env_example}")
    else:
        print("ℹ️ .env.example already exists")

def main():
    print("🚀 Econojin Phase 1 Executor")
    print("=" * 60)
    print("This script will execute Phase 1 actions (0-1 week)")
    print("=" * 60)
    
    # تأیید کاربر
    print("\n⚠️ This will modify your project files.")
    print("   Make sure you have committed your current work.")
    confirm = input("\n   Continue? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("\n❌ Cancelled by user")
        return 1
    
    # اجرای اقدامات
    update_gitignore()
    create_model_downloader()
    remove_large_files_from_git()
    cleanup_backup_files()
    cleanup_pnpm_cache()
    create_env_example()
    
    # خلاصه
    print("\n" + "=" * 60)
    print("✅ Phase 1 actions completed!")
    print("\n📝 Next steps:")
    print("   1. Review changes: git status")
    print("   2. Commit changes: git commit -m 'chore: phase 1 security & optimization'")
    print("   3. Create .env from .env.example: copy .env.example .env")
    print("   4. Fill in actual values in .env")
    print("   5. Enable GitHub Secret Scanning in repository settings")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())