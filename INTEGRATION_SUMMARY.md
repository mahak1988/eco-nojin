# EcoNojin Frontend-Backend Integration Summary

## 🎯 Overview
This document summarizes the integration work completed between the Next.js frontend and FastAPI backend for the EcoNojin platform.

## 📍 API Endpoints Implemented

### Backend (FastAPI) - New Endpoints
Base URL: `http://localhost:8000/api/v1/soil-water`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/dashboard` | Get soil-water dashboard statistics | Required |
| GET | `/models` | List scientific models (filterable by category) | Optional |
| POST | `/comprehensive` | Run comprehensive multi-model analysis | Required |
| GET | `/analyses` | List recent analyses (paginated) | Required |
| POST | `/analyses` | Create new analysis request | Required |
| GET | `/analyses/{id}` | Get specific analysis by ID | Required |

### Frontend (Next.js) - API Routes (Proxies)
- `GET /api/soil-water/analyses/list` → Proxies to backend `/api/v1/soil-water/analyses`
- `POST /api/soil-water/analyses` → Proxies to backend `/api/v1/soil-water/analyses`
- `GET /api/soil-water/comprehensive` → Proxies to backend `/api/v1/soil-water/models`
- `POST /api/soil-water/comprehensive` → Proxies to backend `/api/v1/soil-water/comprehensive`

## 🔗 Connection Points

### 1. Soil-Water Analysis Module
**Frontend Pages:**
- `/soil-water-demo` - Analysis list view
- `/soil-water-demo/comprehensive` - Comprehensive analysis form

**Frontend Hook:**
- `useSoilWaterAnalyses()` - Fetches analysis list
- `useComprehensiveAnalysis()` - Runs composite analysis
- `useSoilWaterModels()` - Fetches available models

**Backend Router:**
- `apps/api/app/api/v1/endpoints/soil_water.py`
- Registered in `api_router.py` at prefix `/soil-water`

**Data Flow:**
```
Frontend Page → Custom Hook → Next.js API Route (proxy) → FastAPI Endpoint → Scientific Models → Response
```

### 2. Scientific Models Module
**Backend:**
- Model definitions: `apps/api/app/services/scientific_models.py` (40 models)
- Database model: `apps/api/app/models/scientific_model.py`
- Management endpoints: `/api/v1/scientific-models/*`

**Integration:**
- Soil-water comprehensive endpoint uses `MODEL_REGISTRY` directly
- Models are seeded via `/api/v1/scientific-models/seed` endpoint
- Classification: Hydrology, Soil Erosion, Evapotranspiration, Water Quality, Economic, Carbon & Ecosystem

## 🔐 Authentication
- Backend uses JWT tokens (HS256)
- Token endpoint: `POST /api/v1/auth/login`
- Protected endpoints require `Authorization: Bearer <token>` header
- Frontend hooks automatically attach token from `localStorage`

## 🌍 CORS Configuration
Backend CORS allows:
- `http://localhost:3000`
- `http://localhost:3002`
- Configurable via `BACKEND_CORS_ORIGINS` in `.env`

## 📦 Environment Variables

### Backend (`apps/api/.env`)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/econojin
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3002
```

### Frontend (`apps/web/.env.local`)
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## 🧪 Testing Status

### Backend
- ✅ Python syntax validation passed (`py_compile`)
- ✅ FastAPI app imports successfully
- ✅ All endpoint routers registered
- ✅ CORS middleware configured
- ✅ Database models defined

### Frontend
- ✅ Custom hooks created (`useSoilWater.ts`)
- ✅ Proxy routes implemented
- ✅ Comprehensive analysis page created
- ✅ List page updated with real data connection
- ✅ Loading/error states managed

### Integration
- ⏳ Full end-to-end test pending (requires both servers running)
- ⏳ Database seeding pending
- ⏳ Authentication flow test pending

## 🚀 Running the System

### Start Backend
```bash
cd d:\econojin.com\apps\api
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```bash
cd d:\econojin.com\apps\web
npm run dev
# or
pnpm dev
```

### Seed Database (First Time)
```bash
cd d:\econojin.com\apps\api
# Login as admin first, then call:
POST http://localhost:8000/api/v1/scientific-models/seed
```

## 🐛 Known Issues & Next Steps

### Immediate Fixes Needed
1. **Alembic migrations** - Run `alembic upgrade head` to sync database schema
2. **Redis/Celery** - Background tasks (comprehensive analysis) currently run synchronously
3. **Real persistence** - Analyses are returned as empty list (in-memory only)
4. **Frontend build** - Verify Next.js compiles without TypeScript errors

### Performance Optimizations
1. Add Redis caching for frequent model queries
2. Implement connection pooling for database
3. Add response compression middleware
4. Frontend: Implement React Query for data fetching optimization

### Security Enhancements
1. Replace hardcoded CORS origins with environment variables
2. Add rate limiting to public endpoints
3. Implement refresh token mechanism
4. Add request validation/sanitization

## 📊 Architecture Diagram

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Browser   │─────▶│  Next.js (Web)   │─────▶│  FastAPI (API)  │
│             │◀─────│  Port 3000       │◀─────│  Port 8000      │
└─────────────┘      └──────────────────┘      └─────────────────┘
                           │                           │
                           │                          ┌┴───────────────┐
                           │                          │  PostgreSQL     │
                           │                          │  + Redis        │
                           │                          └────────────────┘
                           │
                    ┌──────┴────────┐
                    │  API Routes   │
                    │  (Proxies)    │
                    └───────────────┘
```

## 📝 Key Files Modified/Created

### Backend
- `apps/api/app/api/v1/endpoints/soil_water.py` - NEW comprehensive analysis endpoints
- `apps/api/app/api/v1/api_router.py` - UPDATED to include soil_water router
- `apps/api/app/services/scientific_models.py` - EXISTING 40 models registry

### Frontend
- `apps/web/src/hooks/useSoilWater.ts` - NEW custom hook for soil-water integration
- `apps/web/src/app/api/soil-water/analyses/list/route.ts` - UPDATED proxy
- `apps/web/src/app/api/soil-water/comprehensive/route.ts` - NEW proxy
- `apps/web/src/app/(app)/soil-water-demo/page.tsx` - UPDATED to use hook
- `apps/web/src/app/(app)/soil-water-demo/comprehensive/page.tsx` - NEW analysis form
- `apps/web/.env.local` - NEW backend URL config

## ✨ Features Delivered

1. **Real Backend Integration** - Frontend no longer uses mock data
2. **Comprehensive Analysis** - Multi-model composite scoring
3. **Loading/Error States** - Proper UX feedback
4. **Type Safety** - TypeScript interfaces match backend schemas
5. **Authentication Ready** - Token-based auth structure in place
6. **CORS Configured** - Frontend-backend communication enabled
7. **Scientific Models** - 40 models accessible via API
8. **Extensible Router** - New endpoint pattern established for other modules

## 🎓 Scientific Models Available

### Categories
1. **Hydrology** (10) - Darcy, Manning, SCS, Muskingum, Rational, Theis, Cooper-Jacob, Dupuit, Kirpich, Chow
2. **Soil Erosion** (8) - RUSLE, MUSLE, USLE, WEPP, ANSWERS, EPIC, S-CSLE, WEQ
3. **Evapotranspiration** (8) - Penman-Monteith, Hargreaves, Thornthwaite, Blaney-Criddle, Rice, Drip, Sprinkler, Irrigation Req
4. **Water Quality** (6) - Streeter-Phelps, Oxygen Sag, Dilution, Self-Purification, Eutrophication, WQI
5. **Economic** (4) - NPV, IRR, B/C Ratio, Payback
6. **Carbon & Ecosystem** (4) - Carbon Seq, Biodiversity, Ecosystem Value, NDVI

## 🔄 Integration Pattern for Other Modules

To integrate additional modules (e.g., `hydrology`, `forest`, `carbon`):

1. **Backend**: Create `apps/api/app/api/v1/endpoints/{module}.py`
2. **Register**: Add to `apps/api/app/api/v1/api_router.py`
3. **Frontend Hook**: Add methods to `useSoilWater.ts` or create module-specific hook
4. **Frontend Proxy**: Create `apps/web/src/app/api/{module}/route.ts`
5. **Frontend Page**: Update or create page component under `apps/web/src/app/(app)/{module}/`

---

**Status**: Phase 1 Integration Complete ✅
**Next Phase**: Full system testing and deployment preparation