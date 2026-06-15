# راهنمای استقرار Production - هیدروما نوژین

**تاریخ:** 2026-06-15
**نسخه:** 1.0.0

## فهرست مطالب

1. پیش‌نیازها
2. نصب و پیکربندی
3. استقرار با Docker Compose
4. استقرار با Kubernetes
5. مانیتورینگ و لاگینگ
6. پشتیبان‌گیری و بازیابی
7. عیب‌یابی

---

## پیش‌نیازها

### سخت‌افزار
- **CPU:** حداقل 8 هسته (توصیه: 16 هسته)
- **RAM:** حداقل 16 گیگابایت (توصیه: 32 گیگابایت)
- **Storage:** حداقل 100 گیگابایت SSD
- **Network:** اتصال پایدار با پهنای باند حداقل 100 Mbps

### نرم‌افزار
- Docker Engine 20.10+
- Docker Compose 2.0+
- Kubernetes 1.25+ (برای استقرار K8s)
- Git 2.30+

---

## نصب و پیکربندی

### 1. Clone Repository

```bash
git clone https://github.com/econojin/econojin-platform.git
cd econojin-platform
```

### 2. تنظیم متغیرهای محیطی

```bash
cp .env.example .env
nano .env
```

متغیرهای ضروری:

```env
DB_PASSWORD=your_secure_password
BLOCKCHAIN_RPC_URL=https://your-blockchain-rpc.com
GRAFANA_PASSWORD=your_grafana_password
```

---

## استقرار با Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml ps
```

---

## پایش و مانیتورینگ

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000
- **API Health:** http://localhost:8000/health

---

## پایلوت‌های جهانی

پلتفرم اکو نوژین در ۱۲ پایلوت از ۴ قاره فعال است:

- **ایران:** دیشموک، بهبهان، رودبار/تالش، کوهستان برفی
- **مراکش:** واززازت
- **اردن:** وادی رم
- **سنگال:** ساحل
- **اتیوپی:** ارتفاعات
- **هند:** راجستان
- **استرالیا:** اوت‌بک
- **شیلی:** آتاکاما
- **مغولستان:** استپ

---

## پشتیبانی

برای پشتیبانی فنی:
- Email: support@econojin.com
- Documentation: https://docs.econojin.com
- Community: https://community.econojin.com