# 🚀 راهنمای نصب و راه‌اندازی

## پیش‌نیازها

- Node.js 18+
- Python 3.10+
- npm یا yarn

## نصب کامل

### Frontend
```bash
cd frontend
npm install
```

### Backend
```bash
cd backend
python -m venv venv

# Windows:
venv/Scripts/activate

# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### Smart Contracts
```bash
cd contracts
npm install
```

## اجرا

### Frontend (ترمینال 1)
```bash
cd frontend
npm run dev
```
باز کردن: http://localhost:3000

### Backend (ترمینال 2)
```bash
cd backend
# Windows: venv/Scripts/activate
# Linux/Mac: source venv/bin/activate
python -m uvicorn api.main:app --reload
```
API: http://localhost:8000

### Smart Contracts (اختیاری)
```bash
cd contracts
npx hardhat node
npx hardhat run scripts/deploy.js --network localhost
```

## ساختار پروژه

```
econojin-library/
├── frontend/          # Next.js 15.0.5
├── backend/           # FastAPI backend
├── contracts/         # Solidity contracts
├── database/          # SQL schema
└── docs/              # Documentation
```

## ویژگی‌ها

- ✅ 20 زبان با RTL/LTR
- ✅ Next.js 15.0.5 (امن)
- ✅ FastAPI backend
- ✅ EcoToken blockchain
- ✅ Database schema
- ✅ i18n کامل

## پشتیبانی

- Email: support@econojin.com
- Docs: ./docs/