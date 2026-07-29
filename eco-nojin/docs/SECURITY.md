# امنیت چندلایه Econojin

## لایه ۱ — شبکه و هدرها
- `SecurityHeadersMiddleware`: X-Frame-Options, CSP, Referrer-Policy, HSTS (production)
- CORS محدود به originهای مجاز (بدون `*` در production)

## لایه ۲ — کنترل ترافیک
- `RateLimitMiddleware`: محدودیت درخواست per IP (پیش‌فرض ۱۲۰/دقیقه)

## لایه ۳ — احراز هویت
- JWT (HS256) با `JWT_SECRET` قوی در production
- عملیات نوشتن (POST/PUT/DELETE) روی farmers و calendar نیازمند Bearer token وقتی `REQUIRE_AUTH_FOR_WRITES=true`

## لایه ۴ — فرانت‌اند
- Middleware Next.js: محافظت مسیرهای حساس با cookie `econojin_token`
- Interceptor axios: ریدایرکت خودکار به `/login` در 401
- ذخیره session: localStorage + cookie هم‌زمان

## توصیه production
- HTTPS اجباری
- چرخش `JWT_SECRET`
- PostgreSQL + backup
- WAF / Cloudflare در لبه
