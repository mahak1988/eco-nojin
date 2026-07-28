#!/bin/bash
# ==========================================
# Production Environment Setup Script
# ==========================================
# This script generates secure configuration for production deployment

set -e

echo "🔐 Econojin Production Environment Setup"
echo "========================================="

# Check if running in production
if [ "$ENV_STATE" != "production" ]; then
    echo "⚠️  Warning: ENV_STATE is not set to 'production'"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Generate SECRET_KEY
echo "🔑 Generating SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)
echo "✅ SECRET_KEY generated"

# Generate STRAPI_TOKEN
echo "🔑 Generating STRAPI_TOKEN..."
STRAPI_TOKEN=$(openssl rand -hex 16)
echo "✅ STRAPI_TOKEN generated"

# Generate ADMIN_JWT_SECRET
echo "🔑 Generating ADMIN_JWT_SECRET..."
ADMIN_JWT_SECRET=$(openssl rand -hex 16)
echo "✅ ADMIN_JWT_SECRET generated"

# Create .env.production
echo "📝 Creating .env.production..."
cat > .env.production << ENVOF
# ==========================================
# Production Configuration
# Generated: $(date -Iseconds)
# ==========================================

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/econojin

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Update with your actual domains)
ALLOWED_ORIGINS=https://econojin.com,https://api.econojin.com

# Rate Limiting (Production values)
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Environment
ENV_STATE=production
DEBUG=false

# Strapi CMS
STRAPI_TOKEN=${STRAPI_TOKEN}
ADMIN_JWT_SECRET=${ADMIN_JWT_SECRET}

# LLM Provider (Set your production key)
LLM_PROVIDER=groq
GROQ_API_KEY=your-production-key-here

# Add other production-specific settings below
ENVOF

echo "✅ .env.production created"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "1. Review and edit .env.production"
echo "2. Update DATABASE_URL with production credentials"
echo "3. Set actual API keys (GROQ_API_KEY, etc.)"
echo "4. Update ALLOWED_ORIGINS with your domains"
echo "5. NEVER commit .env.production to git!"
echo "6. Set permissions: chmod 600 .env.production"
echo ""
echo "🔒 Setting secure permissions..."
chmod 600 .env.production
echo "✅ Permissions set"
echo ""
echo "🎉 Production environment setup complete!"
