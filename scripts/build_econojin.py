#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Builder Orchestrator
Coordinates the execution of all builder modules with error handling.
"""
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# حل مشکل import برای اجرای مستقیم اسکریپت
sys.path.insert(0, str(Path(__file__).parent))

from builders.contracts_builder import ContractsBuilder
from builders.i18n_builder import I18nBuilder


def run_builders():
    logger.info("=" * 70)
    logger.info("🚀 Econojin Builder Orchestrator")
    logger.info("=" * 70)

    builders = [
        ("i18n", I18nBuilder),
        ("contracts", ContractsBuilder),
    ]

    results = {}
    for name, builder_class in builders:
        try:
            logger.info(f"\n▶️  Running {name} builder...")
            builder = builder_class()
            stats = builder.build()
            results[name] = stats
            logger.info(f"✅ {name}: {stats['files_created']} files created")
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}", exc_info=True)
            results[name] = {"error": str(e)}

    return results


def main():
    try:
        results = run_builders()
        failed = [n for n, r in results.items() if isinstance(r, dict) and "error" in r]

        if failed:
            logger.error(f"\n❌ Build failed for: {', '.join(failed)}")
            return 1
        else:
            logger.info("\n" + "=" * 70)
            logger.info("✅ All builders completed successfully!")
            logger.info("=" * 70)
            return 0
    except Exception as e:
        logger.error(f"❌ Fatal error in orchestrator: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
