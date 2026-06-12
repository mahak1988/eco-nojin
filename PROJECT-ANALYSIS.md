# 📊 گزارش تحلیل جامع پروژه Econojin

**تاریخ تحلیل:** 2026-06-12T03:11:07.317317

## 📈 خلاصه آماری

| شاخص | تعداد |
|------|-------|
| backend_modules | 36 |
| frontend_pages | 65 |
| api_endpoints | 225 |
| database_models | 124 |
| user_roles | 0 |
| audiences_identified | 5 |

## 🧩 ماژول‌های Backend

### 📦 academy
- **مسیر:** `api\modules\academy`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** Course, Lesson, Enrollment, Certificate
- **Endpoints:** 5 عدد
  - `GET /statistics` 🔓
  - `GET /courses` 🔓
  - `GET /courses/{course_id}` 🔓
  - `GET /categories` 🔓
  - `GET /standards` 🔓

### 📦 accounting
- **مسیر:** `api\modules\accounting`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** AccountType, JournalEntryType, AssetType, BankAccount, BankTransaction
- **Endpoints:** 17 عدد
  - `GET /bank-accounts` 🔓
  - `POST /bank-accounts` 🔓
  - `GET /bank-accounts/{account_id}` 🔓
  - `POST /bank-transactions` 🔓
  - `GET /chart-of-accounts` 🔓

### 📦 ai
- **مسیر:** `api\modules\ai`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 5 عدد
  - `POST /analyze/soil` 🔓
  - `POST /analyze/weather` 🔓
  - `POST /analyze/vegetation` 🔓
  - `POST /analyze/farm-plan` 🔓
  - `POST /chat` 🔓

### 📦 analytics
- **مسیر:** `api\modules\analytics`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 auth
- **مسیر:** `api\modules\auth`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ✅, Service: ❌
- **مدل‌ها:** UserAccount
- **Endpoints:** 5 عدد
  - `POST /otp/request` 🔓
  - `POST /otp/verify` 🔓
  - `POST /login` 🔓
  - `GET /profile` 🔓
  - `POST /profile/wallet` 🔓

### 📦 calendar
- **مسیر:** `api\modules\calendar`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ✅, Service: ❌
- **مدل‌ها:** CalendarEvent, EventReminder
- **Endpoints:** 6 عدد
  - `GET /` 🔓
  - `GET /{event_id}` 🔒
  - `POST /` 🔒
  - `PUT /{event_id}` 🔒
  - `DELETE /{event_id}` 🔒

### 📦 community
- **مسیر:** `api\modules\community`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** UserRole, PostType, Post, Comment, UserReputation
- **Endpoints:** 6 عدد
  - `GET /feed` 🔓
  - `POST /posts` 🔓
  - `POST /posts/{post_id}/comments` 🔓
  - `POST /posts/{post_id}/upvote` 🔓
  - `GET /events` 🔓

### 📦 compliance
- **مسیر:** `api\modules\compliance`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 dashboard
- **مسیر:** `api\modules\dashboard`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 1 عدد
  - `GET /stats` 🔓

### 📦 desktop
- **مسیر:** `api\modules\desktop`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 5 عدد
  - `GET /` 🔓
  - `GET /{id}` 🔓
  - `POST /` 🔓
  - `PUT /{id}` 🔓
  - `DELETE /{id}` 🔓

### 📦 drought
- **مسیر:** `api\modules\drought`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 18 عدد
  - `GET /indices` 🔓
  - `POST /spi` 🔓
  - `POST /spei` 🔓
  - `POST /pdsi` 🔓
  - `POST /vhi` 🔓

### 📦 ecocoin
- **مسیر:** `api\modules\ecocoin`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** TokenType, TxType, TxStatus, EcoActionType, RewardStatus
- **Endpoints:** 8 عدد
  - `GET /tokens` 🔓
  - `GET /reward-rates` 🔓
  - `GET /stats` 🔓
  - `GET /wallets/{wallet_id}` 🔓
  - `GET /wallets/me` 🔓

### 📦 ecomining
- **مسیر:** `api\modules\ecomining`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 7 عدد
  - `GET /balance` 🔓
  - `POST /mine` 🔓
  - `GET /` 🔓
  - `GET /{id}` 🔓
  - `POST /` 🔓

### 📦 eco_token
- **مسیر:** `api\modules\eco_token`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 education
- **مسیر:** `api\modules\education`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 5 عدد
  - `GET /` 🔓
  - `GET /{id}` 🔓
  - `POST /` 🔓
  - `PUT /{id}` 🔓
  - `DELETE /{id}` 🔓

### 📦 farmer
- **مسیر:** `api\modules\farmer`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ✅, Service: ❌
- **مدل‌ها:** Farmer
- **Endpoints:** 6 عدد
  - `GET /` 🔒
  - `POST /` 🔒
  - `GET /{farmer_id}` 🔒
  - `PUT /{farmer_id}` 🔒
  - `DELETE /{farmer_id}` 🔒

### 📦 financial
- **مسیر:** `api\modules\financial`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** TransactionType, InvoiceStatus, InventoryMethod, MovementType, ContractStatus
- **Endpoints:** 39 عدد
  - `GET /dashboard` 🔓
  - `GET /units` 🔓
  - `POST /units` 🔓
  - `GET /employees` 🔓
  - `POST /employees` 🔓

### 📦 games
- **مسیر:** `api\modules\games`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** GameCategory, EducationalGame, GameProgress
- **Endpoints:** 5 عدد
  - `GET /list` 🔓
  - `GET /categories` 🔓
  - `GET /stats` 🔓
  - `GET /{game_id}` 🔓
  - `POST /progress` 🔓

### 📦 gis
- **مسیر:** `api\modules\gis`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 3 عدد
  - `POST /calculate/area` 🔓
  - `GET /ndvi` 🔓
  - `GET /layers` 🔓

### 📦 iot
- **مسیر:** `api\modules\iot`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** Sensor, SensorReading, SensorAlert
- **Endpoints:** 6 عدد
  - `GET /sensors` 🔓
  - `GET /sensors/{sensor_code}/latest` 🔓
  - `GET /stats` 🔓
  - `POST /ingest` 🔓
  - `POST /citizen/submit` 🔓

### 📦 library
- **مسیر:** `api\modules\library`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** PublicationType, PublicationStatus, ApprovalStatus, UserRole, User
- **Endpoints:** 19 عدد
  - `GET /research-locations` 🔓
  - `POST /research-locations` 🔓
  - `PUT /research-locations/{location_id}/approve` 🔓
  - `PUT /research-locations/{location_id}/reject` 🔓
  - `GET /research-groups` 🔓

### 📦 maintenance
- **مسیر:** `api\modules\maintenance`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** AlertSeverity, WorkOrderStatus, WorkOrderPriority, EarlyWarningAlert, MaintenanceWorkOrder
- **Endpoints:** 5 عدد
  - `GET /alerts` 🔓
  - `POST /alerts/{alert_id}/acknowledge` 🔓
  - `GET /work-orders` 🔓
  - `PUT /work-orders/{work_order_id}` 🔓
  - `GET /stats` 🔓

### 📦 mrv
- **مسیر:** `api\modules\mrv`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** CarbonProject, CarbonMeasurement, FinancialAnalysis, EcoCoinTransaction, AuditReport
- **Endpoints:** 6 عدد
  - `POST /calculate` 🔓
  - `POST /financial-analysis` 🔓
  - `POST /projects` 🔓
  - `GET /projects` 🔓
  - `GET /projects/{project_id}` 🔓

### 📦 newsletter
- **مسیر:** `api\modules\newsletter`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** NewsletterSubscriber, NewsSource, NewsArticle, NewsletterCampaign
- **Endpoints:** 6 عدد
  - `POST /subscribe` 🔓
  - `POST /unsubscribe` 🔓
  - `GET /news` 🔓
  - `GET /sources` 🔓
  - `GET /categories` 🔓

### 📦 nojin
- **مسیر:** `api\modules\nojin`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 psychology
- **مسیر:** `api\modules\psychology`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ❌, Service: ❌
- **مدل‌ها:** TestCategory, ScoringType, PsychTest, PsychQuestion, PsychOption
- **Endpoints:** 4 عدد
  - `GET /tests` 🔓
  - `GET /tests/{test_code}` 🔓
  - `POST /submit` 🔓
  - `GET /profile/{user_id}` 🔓

### 📦 saas
- **مسیر:** `api\modules\saas`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 sentinel
- **مسیر:** `api\modules\sentinel`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 settings
- **مسیر:** `api\modules\settings`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 5 عدد
  - `GET /` 🔓
  - `GET /{id}` 🔓
  - `POST /` 🔓
  - `PUT /{id}` 🔓
  - `DELETE /{id}` 🔓

### 📦 simulation
- **مسیر:** `api\modules\simulation`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 3 عدد
  - `POST /rothc` 🔓
  - `POST /aquacrop` 🔓
  - `POST /coupling` 🔓

### 📦 soil
- **مسیر:** `api\modules\soil`
- **فایل‌ها:** Router: ❌, Models: ✅, Schemas: ✅, Service: ❌
- **مدل‌ها:** SoilProfile, SoilLayer

### 📦 soil_water
- **مسیر:** `api\modules\soil_water`
- **توضیحات:** Soil & Water Service - Complete with CRUD and Calculations
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ✅, Service: ✅
- **مدل‌ها:** Scenario, WaterBalance, SoilWaterAnalysis, IrrigationSchedule, DroughtIndex
- **Endpoints:** 19 عدد
  - `GET /stats` 🔓
  - `POST /comprehensive-analysis` 🔓
  - `GET /projects` 🔓
  - `POST /projects` 🔓
  - `GET /projects/{project_id}` 🔓

### 📦 store
- **مسیر:** `api\modules\store`
- **فایل‌ها:** Router: ✅, Models: ✅, Schemas: ✅, Service: ❌
- **مدل‌ها:** OrderStatus, TransactionType, Product, Order, StoreWallet
- **Endpoints:** 4 عدد
  - `GET /products` 🔓
  - `GET /StoreWallet/{user_id}` 🔓
  - `POST /StoreWallet/deposit` 🔓
  - `POST /orders` 🔓

### 📦 structures
- **مسیر:** `api\modules\structures`
- **فایل‌ها:** Router: ❌, Models: ❌, Schemas: ❌, Service: ❌

### 📦 water
- **مسیر:** `api\modules\water`
- **توضیحات:** Application service for soil–water balance simulations.

    Responsibilities:
    - Load soil domain entities
    - Call scientific core
    - Persist results into WaterBalance
    - Emit structured 
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ✅, Service: ✅
- **Endpoints:** 2 عدد
  - `GET /balance` 🔓
  - `POST /simulate` 🔓

### 📦 weather
- **مسیر:** `api\modules\weather`
- **فایل‌ها:** Router: ✅, Models: ❌, Schemas: ❌, Service: ❌
- **Endpoints:** 5 عدد
  - `GET /cities` 🔓
  - `GET /forecast/{city_key}` 🔓
  - `GET /forecast/coordinates` 🔓
  - `GET /historical/{city_key}` 🔓
  - `GET /compare` 🔓

## 👥 مخاطبان شناسایی‌شده

### 👤 کشاورز
**ماژول‌های مرتبط:** soil_water, weather, academy

### 👤 مدیر مزرعه
**ماژول‌های مرتبط:** iot, drought

### 👤 کارشناس کشاورزی
**ماژول‌های مرتبط:** soil_water, gis, iot, weather, academy, drought

### 👤 حسابدار
**ماژول‌های مرتبط:** accounting, financial

### 👤 مدیر ارشد
**ماژول‌های مرتبط:** accounting, financial

## 🎨 صفحات Frontend

| مسیر | داینامیک | کامپوننت‌ها |
|------|----------|-------------|
| `.` | ❌ | Leaf, Link |
| `about` | ❌ | ArrowRight, Link |
| `academy` | ❌ | Badge, GraduationCap, Input |
| `accounting` | ❌ | ArrowRight, Link |
| `admin` | ❌ | LayoutDashboard, Link |
| `ai` | ❌ | Card, Brain, Button |
| `blog` | ❌ | ArrowRight, Link |
| `carbon` | ❌ | ResponsiveContainer, TreePine, ScientificModuleLayout |
| `community` | ❌ | ArrowRight, Link |
| `contact` | ❌ | ArrowRight, Link |
| `crop` | ❌ | ResponsiveContainer, Sprout, ScientificModuleLayout |
| `desktop` | ❌ | ArrowRight, Link |
| `drought` | ❌ | Card, AlertTriangle, DroughtDashboard |
| `ecocoin` | ❌ | Coins |
| `ecomining` | ❌ | ArrowRight, Link |
| `education` | ❌ | ArrowRight, Link |
| `erosion` | ❌ | Mountain, ResponsiveContainer, ScientificModuleLayout |
| `financial` | ❌ | ArrowRight, Link |
| `forgot-password` | ❌ | Phone, AuthWelcomePanel, Link |
| `games` | ❌ | ArrowRight, Link |
| `gis` | ❌ | Badge, SpectralAnalysis, SatelliteLayers |
| `hydrology` | ❌ | SimulationControls |
| `inventory` | ❌ | ArrowRight, Link |
| `iot` | ❌ | Card, Badge, Button |
| `library` | ❌ | ArrowRight, Link |
| `login` | ❌ | AuthWelcomePanel, Eye, Link |
| `maintenance` | ❌ | ArrowRight, Link |
| `mrv` | ❌ | Card, TreePine, ForestDashboard |
| `newsletter` | ❌ | ArrowRight, Link |
| `policy` | ❌ | ArrowRight, Link |

*... و 35 صفحه دیگر*

## 🔗 وابستگی‌های بین ماژول‌ها

- **iot** ← library
- **water** ← soil

## 💡 پیشنهادات توسعه

### ماژول‌های با اولویت بالا (بر اساس تعداد endpoints و وابستگی‌ها):
1. **financial** - 39 endpoint
2. **library** - 19 endpoint
3. **soil_water** - 19 endpoint
4. **drought** - 18 endpoint
5. **accounting** - 17 endpoint

