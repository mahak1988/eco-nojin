# EcoNojin API

Backend API for EcoNojin - Digital Twin of Hydroma Nojin

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
cd apps/api
pip install -r requirements.txt
```

2. Run the API:
```bash
uvicorn app.main:app --reload
```

3. Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🗄️ Database

Uses SQLite with async support. Database file: `data/econojin.db`

## 📝 License

Proprietary - Narvan Co.
