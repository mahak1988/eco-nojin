# فاز A — پایدارسازی Content Types

**وضعیت:** پیاده‌سازی‌شده روی `main`

## Content Types

| API UID | Admin | REST (نمونه) | Draft/Publish |
|---------|-------|--------------|---------------|
| `api::page.page` | Page | `/api/pages` | بله |
| `api::blog-post.blog-post` | Blog Post | `/api/blog-posts` | بله |
| `api::category.category` | Category | `/api/categories` | خیر |
| `api::tag.tag` | Tag | `/api/tags` | خیر |

هر کدام دارای `controllers` / `services` / `routes` استاندارد Strapi (`createCore*`) هستند.

## تغییرات schema

- حذف وابستگی به پلاگین **i18n** (فعلاً نصب نیست)
- `tenant` اختیاری با پیش‌فرض `main`
- حذف relation نویسنده به users-permissions (جایگزین: فیلد `authorName`)
- relation دوطرفه blog ↔ category/tag حفظ شد

## راه‌اندازی Admin

```bash
cd apps/cms
cp .env.example .env   # اگر هنوز ندارید
pnpm install
pnpm dev
```

1. مرورگر: http://localhost:1337/admin  
2. ساخت اولین کاربر Admin  
3. **Settings → Users & Permissions → Roles → Public**  
   - برای خواندن عمومی (اختیاری): `find` / `findOne` روی Page و Blog-post  
4. نقش Authenticated یا Admin برای create/update/delete کامل است

## تست سریع CRUD (با API Token یا cookie ادمین)

```http
POST /api/categories
{ "data": { "name": "کشاورزی", "slug": "agriculture" } }

POST /api/tags
{ "data": { "name": "آبیاری", "slug": "irrigation" } }

POST /api/blog-posts
{ "data": { "title": "اولین پست", "slug": "first-post", "content": "متن نمونه" } }

POST /api/pages
{ "data": { "title": "درباره ما", "slug": "about", "content": "محتوا" } }

GET /api/pages
GET /api/blog-posts
```

## بعد از فاز A

- فاز B: مصرف API در `apps/web` + webhook به FastAPI  
- تنظیم دقیق Public permissions  
- Media library در Admin برای تصاویر
