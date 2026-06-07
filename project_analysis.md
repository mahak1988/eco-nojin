# گزارش آنالیز خودکار پروژه

## 📊 آمار کلی
- **تعداد کل فایل‌ها:** 7354
- **تعداد کل خطوط کد:** 1,810,232

## 🛠 تکنولوژی‌ها و وابستگی‌ها
### توزیع فرمت فایل‌ها:
- `.py`: 3589 فایل
- `.json`: 1719 فایل
- `.tsx`: 371 فایل
- `.pyi`: 292 فایل
- `.pyd`: 145 فایل
- `.ts`: 137 فایل
- `.mat`: 110 فایل
- `.a`: 109 فایل
- `.txt`: 103 فایل
- `.f90`: 61 فایل

### وابستگی‌های فرانت‌اند/Node (نمونه):
turbo, pnpm, @fontsource/inter, @fontsource/jetbrains-mono, @fontsource/vazirmatn, @hookform/resolvers, @radix-ui/react-label, @radix-ui/react-slot, @tanstack/react-query, axios, class-variance-authority, clsx, date-fns, date-fns-jalali, framer-motion...

### وابستگی‌های بک‌اند (نمونه):
[project], name = "econojin", version = "1.0.0", description = "Scientific platform for ecological modeling and carbon tracking", requires-python = ">=3.10", authors = [{ name = "Econojin Team" }], license = { text = "MIT" }, readme = "README.md", [tool.black], line-length = 100, target-version = ['py310', 'py311', 'py312'], include = '\.pyi?$', [tool.isort], profile = "black", line_length = 100...

## 🏗 یادداشت‌های معماری
- پروژه فرانت‌اند/Node.js شناسایی شد (package.json).
- پروژه بک‌اند پایتون شناسایی شد.

## ⚠️ نقاط ضعف کد (Code Smells)
### Print Statements (6294 مورد)
- .\add_approval_system.py:21
- .\add_approval_system.py:28
- .\add_approval_system.py:416
- .\add_approval_system.py:1160
- .\add_approval_system.py:1866
- .\add_approval_system.py:1867
- .\add_approval_system.py:1870
- .\add_approval_system.py:1877
- .\add_approval_system.py:1878
- .\add_approval_system.py:1879
- *... و 6284 مورد دیگر*

### TODOs/FIXMEs (1288 مورد)
- .\add_languages.py:347
- .\analyzer.py:66
- .\analyzer.py:67
- .\.venv\Lib\site-packages\sgmllib.py:3
- .\.venv\Lib\site-packages\sgmllib.py:5
- .\.venv\Lib\site-packages\sgmllib.py:210
- .\.venv\Lib\site-packages\sgmllib.py:238
- .\.venv\Lib\site-packages\sgmllib.py:239
- .\.venv\Lib\site-packages\sgmllib.py:240
- .\.venv\Lib\site-packages\sgmllib.py:251
- *... و 1278 مورد دیگر*

### Console Logs (80 مورد)
- .\.pnpm-store\v11\projects\9222c30457a0b11aadb8a0a791789040\src\app\admin\blog\page.tsx:98
- .\.pnpm-store\v11\projects\9222c30457a0b11aadb8a0a791789040\src\components\shared\CitizenDataForm.tsx:140
- .\.pnpm-store\v11\projects\9222c30457a0b11aadb8a0a791789040\src\hooks\useAnalysisWebSocket.ts:15
- .\.pnpm-store\v11\projects\9222c30457a0b11aadb8a0a791789040\src\hooks\useAnalysisWebSocket.ts:36
- .\.pnpm-store\v11\projects\9222c30457a0b11aadb8a0a791789040\src\lib\analytics.ts:19
- .\.pnpm-store\v11\projects\9222c30457a0b11aadb8a0a791789040\src\lib\analytics.ts:23
- .\apps\web\src\app\admin\blog\page.tsx:98
- .\apps\web\src\components\shared\CitizenDataForm.tsx:140
- .\apps\web\src\hooks\useAnalysisWebSocket.ts:15
- .\apps\web\src\hooks\useAnalysisWebSocket.ts:36
- *... و 70 مورد دیگر*

