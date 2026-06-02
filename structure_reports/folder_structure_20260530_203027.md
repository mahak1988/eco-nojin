# 📊 گزارش تحلیل ساختار پوشه‌های پروژه
**پروژه:** `econojin.com`
**زمان اجرا:** 2026-05-30 20:30:26

======================================================================
## 📈 آمار کلی ساختار
======================================================================
| معیار | مقدار |
|---|---|
| 📁 تعداد کل پوشه‌ها (بدون node_modules و...) | **190** |
| 📄 تعداد کل فایل‌ها | **518** |
| 📏 حداکثر عمق درخت پوشه‌ها | **5** لایه |
| 📂 عمیق‌ترین پوشه | `apps\web\app\(auth)\login` |
| ⚠️ تعداد پوشه‌های خالی | **20** |

======================================================================
## 🏷️ دسته‌بندی پوشه‌ها بر اساس نوع
======================================================================

### 📦 Core/Source
- **تعداد پوشه‌ها:** 75
- **تعداد کل فایل‌ها در این دسته:** 150
- **نمونه پوشه‌ها:**
  - `apps`
  - `apps\admin\app`
  - `apps\web\app`
  - `apps\web\lib`
  - `backend\core`
  - *... و 16 پوشه دیگر*

### 🎨 Frontend/Assets
- **تعداد پوشه‌ها:** 19
- **تعداد کل فایل‌ها در این دسته:** 64
- **نمونه پوشه‌ها:**
  - `apps\web\components`
  - `apps\web\components\ui`
  - `econojin-library\frontend`
  - `econojin-library\frontend\components`
  - `econojin-library\frontend\public`
  - *... و 5 پوشه دیگر*

### 🗄️ Database
- **تعداد پوشه‌ها:** 17
- **تعداد کل فایل‌ها در این دسته:** 33
- **نمونه پوشه‌ها:**
  - `backend\models`
  - `core\gaia\models`
  - `database`
  - `database\migrations`
  - `docker\db`
  - *... و 6 پوشه دیگر*

### 🔐 Security
- **تعداد پوشه‌ها:** 11
- **تعداد کل فایل‌ها در این دسته:** 21
- **نمونه پوشه‌ها:**
  - `apps\web\app\(auth)`
  - `frontend\app\[locale]\security`
  - `frontend\src\app\auth`
  - `frontend\src\lib\auth`
  - `infrastructure\security`
  - *... و 1 پوشه دیگر*

### 🔧 Scripts
- **تعداد پوشه‌ها:** 8
- **تعداد کل فایل‌ها در این دسته:** 52
- **نمونه پوشه‌ها:**
  - `contracts\script`
  - `contracts\scripts`
  - `econojin-library\contracts\scripts`
  - `frontend\scripts`
  - `scripts`
  - *... و 1 پوشه دیگر*

### 🚀 DevOps/Deployment
- **تعداد پوشه‌ها:** 8
- **تعداد کل فایل‌ها در این دسته:** 7
- **نمونه پوشه‌ها:**
  - `infra`
  - `infra\k8s`
  - `infrastructure`

### 🌐 API
- **تعداد پوشه‌ها:** 7
- **تعداد کل فایل‌ها در این دسته:** 14
- **نمونه پوشه‌ها:**
  - `apps\web\app\api`
  - `backend\api`
  - `econojin-library\backend\api`
  - `econojin-library\backend\api\routes`
  - `scripts\api`

### 📝 Logs
- **تعداد پوشه‌ها:** 6
- **تعداد کل فایل‌ها در این دسته:** 9
- **نمونه پوشه‌ها:**
  - `apps\web\app\(auth)\login`
  - `backend\models\hydrology`
  - `frontend\app\[locale]\hydrology`
  - `frontend\app\[locale]\login`
  - `frontend\src\app\auth\login`
  - *... و 1 پوشه دیگر*

### ⚙️ Config
- **تعداد پوشه‌ها:** 4
- **تعداد کل فایل‌ها در این دسته:** 11
- **نمونه پوشه‌ها:**
  - `apps\cms\config`
  - `packages\config-eslint`
  - `packages\config-typescript`
  - `scripts\fetchers`

### 🧪 Tests
- **تعداد پوشه‌ها:** 4
- **تعداد کل فایل‌ها در این دسته:** 27
- **نمونه پوشه‌ها:**
  - `apps\web\__tests__`
  - `contracts\test`
  - `scripts\testing`
  - `tests`

### 🤖 Integrations
- **تعداد پوشه‌ها:** 4
- **تعداد کل فایل‌ها در این دسته:** 7
- **نمونه پوشه‌ها:**
  - `backend\integrations`
  - `backend\services`
  - `econojin-library\backend\services`
  - `scripts\api\services`

### 📊 Analytics/Research
- **تعداد پوشه‌ها:** 4
- **تعداد کل فایل‌ها در این دسته:** 17
- **نمونه پوشه‌ها:**
  - `core\gaia`
  - `frontend\lib\ai`
  - `scripts\blockchain`
  - `scripts\research`

### 📚 Documentation
- **تعداد پوشه‌ها:** 3
- **تعداد کل فایل‌ها در این دسته:** 6
- **نمونه پوشه‌ها:**
  - `docker`
  - `docs`
  - `econojin-library\docs`

### ❓ پوشه‌های دسته‌بندی نشده (20 پوشه)
- `backend` (1 فایل)
- `contracts` (8 فایل)
- `contracts\contracts` (3 فایل)
- `data` (0 فایل)
- `data\processed` (12 فایل)
- `data\raw` (0 فایل)
- `data\raw\era5` (4 فایل)
- `data\raw\sentinel2` (0 فایل)
- `data\shp` (0 فایل)
- `legal` (2 فایل)

======================================================================
## 📊 توزیع عمق پوشه‌ها
======================================================================
- عمق 0: 1 پوشه █
- عمق 1: 21 پوشه █████████████████████
- عمق 2: 57 پوشه ██████████████████████████████████████████████████
- عمق 3: 56 پوشه ██████████████████████████████████████████████████
- عمق 4: 44 پوشه ████████████████████████████████████████████
- عمق 5: 12 پوشه ████████████

======================================================================
## ⚠️ پوشه‌های خالی (نیاز به بررسی)
======================================================================
- `contracts\script`
- `data\raw\sentinel2`
- `data\shp`
- `econojin-library\backend\api\routes`
- `econojin-library\contracts\contracts`
- `econojin-library\contracts\scripts`
- `econojin-library\frontend\app\[locale]\advisors`
- `econojin-library\frontend\app\[locale]\desk`
- `econojin-library\frontend\app\[locale]\halls`
- `econojin-library\frontend\app\[locale]\library`
- `econojin-library\frontend\app\[locale]\wallet`
- `econojin-library\frontend\app\[locale]\webinars`
- `econojin-library\frontend\components`
- `econojin-library\frontend\public`
- `frontend\scripts`
- *... و 5 پوشه خالی دیگر*

======================================================================
## 📦 پوشه‌های با تعداد فایل زیاد (> 20 فایل)
======================================================================
- `.` - **59 فایل**
- `scripts` - **45 فایل**
- `tests` - **23 فایل**
- `econojin-library\frontend\lib\i18n` - **21 فایل**
- `frontend\lib\i18n` - **21 فایل**

======================================================================
## 📋 توزیع انواع فایل‌ها در پروژه
======================================================================
- `.py` : **179** فایل (34.6%) █████████████████
- `.json` : **87** فایل (16.8%) ████████
- `.tsx` : **84** فایل (16.2%) ████████
- `.ts` : **41** فایل (7.9%) ███
- `.md` : **19** فایل (3.7%) █
- `.js` : **15** فایل (2.9%) █
- `(no extension)` : **14** فایل (2.7%) █
- `.example` : **10** فایل (1.9%) 
- `.yml` : **9** فایل (1.7%) 
- `.sol` : **9** فایل (1.7%) 
- `.txt` : **7** فایل (1.4%) 
- `.sql` : **6** فایل (1.2%) 
- `.yaml` : **5** فایل (1.0%) 
- `.css` : **5** فایل (1.0%) 
- `.nc` : **4** فایل (0.8%) 

======================================================================
## 💡 توصیه‌های ساختاری
======================================================================
- 🧹 **پاکسازی:** 20 پوشه خالی وجود دارد که می‌توان حذف کرد.
- 🏷️ **سازماندهی:** 20 پوشه بدون دسته‌بندی مشخص وجود دارد. بررسی ساختار نام‌گذاری توصیه می‌شود.
- 📦 **تفکیک:** 1 پوشه با بیش از ۵۰ فایل وجود دارد. پیشنهاد می‌شود آن‌ها را به زیرپوشه‌های کوچک‌تر تقسیم کنید.