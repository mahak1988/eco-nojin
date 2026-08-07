# مدیریت نقش‌ها و دسترسی‌ها — CMS (Strapi)

## مدل نقش‌ها

Strapi دو لایه دارد:

| لایه | محل | نقش‌ها |
|------|------|--------|
| **Admin Panel** | Users & Permissions در پنل `/admin` | Super Admin و نقش‌های ادمین داخلی |
| **Users & Permissions (API)** | پلاگین `users-permissions` | `Public`، `Authenticated` (+ نقش سفارشی) |

این سند روی **دسترسی API محتوا** (صفحه، پست، دسته، برچسب) تمرکز دارد.

---

## ماتریس پیشنهادی EcoNojin

| نقش | Page | Blog Post | Category | Tag |
|-----|------|-----------|----------|-----|
| **Public** (بدون لاگین) | خواندن | خواندن | خواندن | خواندن |
| **Authenticated** (JWT کاربر API) | CRUD کامل | CRUD کامل | CRUD کامل | CRUD کامل |
| **Admin Panel** | همیشه از طریق پنل | همیشه | همیشه | همیشه |

- **خواندن** = `find` + `findOne`  
- **CRUD** = create + update + delete + find + findOne  
- محتوای draft فقط با توکن/ادمین دیده می‌شود (رفتار پیش‌فرض draftAndPublish).

---

## اعمال خودکار (Bootstrap)

فایل `src/bootstrap/ensure-permissions.ts` در هر بار بالا آمدن سرور:

1. نقش‌های `public` و `authenticated` را پیدا می‌کند  
2. مجوزهای ماتریس بالا را **idempotent** اضافه می‌کند (تکراری نمی‌سازد)

پس از `pnpm dev` در لاگ باید ببینید:

```text
[cms:permissions] defaults applied — Public: read content; Authenticated: full CRUD
```

---

## مدیریت دستی از Admin UI

1. وارد http://localhost:1337/admin شوید  
2. **Settings → Users & Permissions Plugin → Roles**  
3. نقش **Public** را باز کنید  
4. زیر مجموعه‌های **Page / Blog-post / Category / Tag** تیک‌های `find` و `findOne` را بزنید  
5. ذخیره  
6. نقش **Authenticated** → همه عملیات (find, findOne, create, update, delete)

### نقش سفارشی (مثلاً Editor)

1. Roles → **Add new role** → نام: `Editor`  
2. فقط create/update روی Blog-post و Page؛ delete را محدود کنید  
3. کاربر API را با آن نقش بسازید (Content Manager یا Users)

---

## توکن‌ها

| نوع | کاربرد |
|-----|--------|
| **API Token** (Settings → API Tokens) | سرور به سرور / CI — Full access یا Custom |
| **JWT کاربر** (`/api/auth/local`) | اپ فرانت با نقش Authenticated |
| **Admin JWT** | فقط پنل ادمین — برای API عمومی استفاده نکنید |

مثال خواندن عمومی:

```http
GET /api/pages
GET /api/blog-posts?publicationState=live
```

مثال نوشتن با API Token:

```http
POST /api/blog-posts
Authorization: Bearer <API_TOKEN>
Content-Type: application/json

{ "data": { "title": "پست", "slug": "post", "content": "..." } }
```

---

## سیاست‌های پیشرفته (آینده)

فایل‌های موجود در `src/policies/`:

- `tenant-rbac.ts` — محدودیت tenant  
- `module-access.ts` — دسترسی ماژول  
- `cross-tenant-sharing.ts` — اشتراک بین tenant  

برای استفاده باید در `routes` مربوطه به‌صورت `policies: ['global::tenant-rbac']` ثبت شوند (فاز بعدی).

---

## چک‌لیست پذیرش

- [ ] Public بدون توکن فقط GET می‌گیرد؛ POST بدون توکن → 403  
- [ ] Authenticated / API Token می‌تواند create/update کند  
- [ ] Draft در Public دیده نمی‌شود  
- [ ] Admin Panel همه محتوا را می‌بیند
