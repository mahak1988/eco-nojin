#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
راه‌اندازی Hardhat Local Network و Deploy قراردادها
r"""

import subprocess
import sys
import time
import threading
from pathlib import Path

PROJECT_ROOT = Path(r"D:\econojin.com")
CONTRACTS_DIR = PROJECT_ROOT / "contracts"

def run_node():
    """اجرای hardhat node در پس‌زمینه"""
    print("🚀 Starting Hardhat local network...")
    subprocess.run(
        ["npx", "hardhat", "node"],
        cwd=CONTRACTS_DIR,
    # SECURITY WARNING: Consider shell=False for better security
        shell=True,
    )

def main():
    print("="*70)
    print("⛓️ Hardhat Local Deployment")
    print("="*70)
    
    # Start node in background
    node_thread = threading.Thread(target=run_node, daemon=True)
    node_thread.start()
    
    # Wait for node to start
    print("\n⏳ Waiting for node to start...")
    time.sleep(5)
    
    # Deploy contracts
    print("\n📦 Deploying contracts...")
    result = subprocess.run(
        ["npx", "hardhat", "run", "scripts/deploy_local.js", "--network", "localhost"],
        cwd=CONTRACTS_DIR,
    # SECURITY WARNING: Consider shell=False for better security
        shell=True,
    )
    
    if result.returncode == 0:
        print("\n✅ Deployment successful!")
        print("\n🎯 Next steps:")
        print("   1. Keep this terminal open (Hardhat node running)")
        print("   2. Open frontend: cd frontend && npm run dev")
        print("   3. Connect MetaMask to http://127.0.0.1:8545 (Chain ID: 31337)")
        input("\nPress Ctrl+C to stop the node...")
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
