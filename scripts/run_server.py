# -*- coding: utf-8 -*-
"""
Econojin API Server Runner
"""

import sys
from pathlib import Path

import uvicorn

# Add project root to path
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from scripts.core.logger import UnifiedLogger

    logger = UnifiedLogger.get_logger(__name__)
except Exception:
    import logging

    logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    """Load config from Python file safely"""
    if not config_path.exists():
        # Return default config if file doesn't exist
        return {
            "HOST": "0.0.0.0",
            "PORT": 8000,
            "RELOAD": True,
        }

    import importlib.util

    spec = importlib.util.spec_from_file_location("config", config_path)
    if spec is None or spec.loader is None:
        return {"HOST": "0.0.0.0", "PORT": 8000, "RELOAD": True}

    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    return {
        key: value
        for key, value in vars(config_module).items()
        if not key.startswith("_") and not callable(value)
    }


def main():
    """Main entry point"""
    logger.info("🚀 Starting Econojin API server...")

    config_path = Path(__file__).parent / "config.py"
    config = load_config(config_path)

    host = config.get("HOST", "0.0.0.0")
    port = config.get("PORT", 8000)
    reload = config.get("RELOAD", True)

    logger.info(f"📡 Server: http://{host}:{port}")
    logger.info(f"📚 API Docs: http://{host}:{port}/docs")
    logger.info(f"🔄 Reload: {reload}")

    try:
        uvicorn.run(
            "scripts.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
