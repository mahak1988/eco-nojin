# 🐳 Economugin - Production Deployment
## Quick Start
```bash
cp .env.production.example .env.production  # Edit passwords & SECRET_KEY
docker-compose -f docker-compose.prod.yml up -d --build
curl http://localhost:8000/health
```
## Monitoring
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/${GRAFANA_PASSWORD})
- Prometheus: http://localhost:9090
## Security Checklist
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Enable HTTPS via reverse proxy
- [ ] Rotate logs regularly
## Backup
```bash
docker exec economugin-db pg_dump -U economugin economugin > backup_$(date +%Y%m%d).sql
```
# 🚀 راهنمای استقرار Econojin

## فهرست مطالب
- [پیش‌نیازها](#پیشنیازها)
- [محیط‌ها](#محیطها)
- [استقرار محلی](#استقرار-محلی)
- [استقرار Staging](#استقرار-staging)
- [استقرار Production](#استقرار-production)
- [Rollback](#rollback)
- [مانیتورینگ](#مانیتورینگ)

---

## پیش‌نیازها

### ابزارهای مورد نیاز
- Docker 24+
- Docker Compose v2
- Git
- Python 3.12+
- PostgreSQL 16
- Redis 7

### Secrets مورد نیاز در GitHub
```bash
# Staging
STAGING_HOST=your-staging-server.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private-key>

# Production
PROD_HOST=your-prod-server.com
PROD_USER=deploy
PROD_SSH_KEY=<private-key>

# AWS (اگر استفاده می‌کنید)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1

# Notifications
SLACK_WEBHOOK=https://hooks.slack.com/xxx
TEAM_EMAIL=team@econojin.com