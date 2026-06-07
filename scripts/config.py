# -*- coding: utf-8 -*-
"""
Configuration for Econojin API
"""

import os
from pathlib import Path

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/econojin")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# API Configuration
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Econojin API"
VERSION = "2.0.0"
DESCRIPTION = "Scientific Carbon Platform powered by Gaia Protocol"

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
    "https://econojin.com",
    "https://staging.econojin.com",
]

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Gaia Protocol Configuration
GAIA_CONTRACT_ADDRESS = os.getenv("GAIA_CONTRACT_ADDRESS", "")
GAIA_ORACLE_PRIVATE_KEY = os.getenv("GAIA_ORACLE_PRIVATE_KEY", "")
POLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")

# Copernicus/Sentinel-2 Configuration
COPERNICUS_CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID", "")
COPERNICUS_CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET", "")

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
