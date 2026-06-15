"""Run seed script from apps/api root"""

import sys
import os

# Ensure current directory is in path
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from scripts.seed_admin import seed_admin
import asyncio

if __name__ == "__main__":
    asyncio.run(seed_admin())
