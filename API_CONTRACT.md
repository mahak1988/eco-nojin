# API_CONTRACT.md (Generated)
## هدف
هم‌ترازی قراردادهای فرانت و بک‌اند برای مسیرهای کلیدی Econojin.

> این سند بر اساس فایل‌های خوانده‌شده در بک‌اند `apps/api/app/api/v1/api_router.py` و `apps/api/app/api/v1/endpoints/auth.py` تولید شده است. برای کامل شدن ۱۰۰٪ باید همه endpointهای دیگر در `apps/api/app/api/v1/endpoints/*` نیز خوانده شود.

---

## 1) پایه API
- Base path: `/api/v1` (در `apps/api/app/main.py` با `settings.API_V1_STR` و همچنین `include_router(..., prefix=settings.API_V1_STR)`)

- Health endpoints:
  - `GET /api/v1/health` (از `api_router.include_router(health.router, prefix="/health")`)
  - همچنین در main app:
    - `GET /health` (در ریشه FastAPI)

---

## 2) Authentication
### 2.1 Register
- **POST** `/api/v1/auth/register`
- Request body:
  - طبق `app.schemas.user.UserCreate` (هنوز schema کامل خوانده نشده)
  - انتظار عمومی: `{ email, password, full_name? }` (باید از `UserCreate` استخراج شود)
- Response:
  - `201 Created`
  - مدل: `RegisterResponse` شامل:
    - `message`
    - `user_id`
    - `email`

- Error:
  - `400` اگر email تکراری باشد.

### 2.2 Login
- **POST** `/api/v1/auth/login`
- Request body: `LoginRequest` (هنوز schema کامل خوانده نشده)
  - انتظار عمومی: `{ email, password }`
- Response:
  - `200 OK`
  - مدل: `Token`
    - `access_token`
    - `token_type` (bearer)
    - `expires_in` (ثانیه/محاسبه شده از settings)

- Logic:
  - اگر account suspended باشد: `403`
  - اگر credentials غلط: `401` با `WWW-Authenticate: Bearer`

### 2.3 Me
- **GET** `/api/v1/auth/me`
- Auth:
  - از JWT در header `Authorization: Bearer <token>` با `OAuth2PasswordBearer`
- Response:
  - مدل: `UserResponse` (هنوز schema کامل خوانده نشده)

---

## 3) Users/Projects/DataPoints/KPIs/Modules (در router وجود دارد)
مسیرها در `apps/api/app/api/v1/api_router.py` ثبت شده‌اند اما contract request/response دقیق هنوز از فایل endpoints مربوطه خوانده نشده است:

- `GET/POST/... /api/v1/users` (router: users.router, prefix="/users")
- `GET/POST/... /api/v1/projects` (router: projects.router, prefix="/projects")
- `GET/POST/... /api/v1/data-points` (router: data_points.router, prefix="/data-points")
- `GET/POST/... /api/v1/kpis` (router: kpis.router, prefix="/kpis")
- `GET/POST/... /api/v1/models` (router: models.router, prefix="/models")
- `GET/POST/... /api/v1/scientific-models` (router: scientific_models.router)
- `GET/POST/... /api/v1/modules` (router: modules.router)
- `GET/POST/... /api/v1/soil-water` (router: soil_water.router)

---

## 4) امنیت در سطح درخواست
- CORS در `apps/api/app/main.py`:
  - `allow_origins=settings.BACKEND_CORS_ORIGINS`
  - `allow_methods=["*"]`, `allow_headers=["*"]`
- Auth:
  - JWT با `HS256` و `SECRET_KEY` از `apps/api/app/core/config.py`
  - استخراج user از claim `sub` (email) و سپس lookup در DB
- Role:
  - helper `require_role(allowed_roles)` در `apps/api/app/core/security.py` وجود دارد.

---

## وضعیت این سند
- Authentication contract به طور نسبی مشخص است.
- بقیه endpointها نیازمند مطالعه فایل‌های:
  - `apps/api/app/api/v1/endpoints/users.py`
  - `.../projects.py`
  - `.../data_points.py`
  - `.../kpis.py`
  - `.../models.py`
  - `.../scientific_models.py`
  - `.../modules.py`
  - `.../soil_water.py`

(در مرحله بعد تولید می‌شود.)
