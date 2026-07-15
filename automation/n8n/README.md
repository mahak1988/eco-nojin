# Eco Nojin - n8n اتوماسیون

## اجرا
```bash
cd automation/n8n
pnpm start
```
n8n روی `http://localhost:5678` در دسترس قرار می‌گیرد.

## بارگذاری workflow نمونه
- به `http://localhost:5678` بروید
- از منوی Workflows → Import from File، فایل `workflows/welcome-email.json` را انتخاب کنید.
- آدرس Webhook را یادداشت کرده و در بک‌اند (ثبت‌نام) فراخوانی کنید.

## نیازمندی‌ها
- Node.js 18+
- pnpm
