# نمونه‌های اتصال ماژول‌ها

## مثال ۱: اتصال ماژول فروشگاه الکترونیک

### مراحل اتصال
۱. ایجاد ماژول فروشگاه الکترونیک با API خاص
۲. ثبت endpoint ماژول در CMS
۳. فعال‌سازی همگام‌سازی محتوا

### کد نمونه

#### ثبت اتصال از ماژول فروشگاه
```javascript
// در ماژول فروشگاه الکترونیک
const response = await fetch('http://cms.econojin.com/api/module-integration/connect', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Module-Token': 'your-module-api-key'
  },
  body: JSON.stringify({
    module: 'ecommerce',
    endpoint: 'https://ecommerce.econojin.com/api'
  })
});
```

#### ایجاد صفحه محصول در زمان ایجاد محصول جدید
```javascript
// در ماژول فروشگاه - زمان ایجاد محصول جدید
const product = await createProductInEcommerce(data);

// ارسال اطلاعات به CMS برای ایجاد صفحه محصول
await fetch('http://cms.econojin.com/api/module-integration/receive-content', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Module-Token': 'your-module-api-key'
  },
  body: JSON.stringify({
    module: 'ecommerce',
    content: {
      type: 'product',
      id: product.id,
      name: product.name,
      description: product.description,
      price: product.price,
      tenant: product.tenant
    }
  })
});
```

## مثال ۲: اتصال ماژول احراز هویت

### مراحل اتصال
۱. ایجاد ماژول احراز هویت
۲. ثبت endpoint در CMS
۳. ایجاد سیاست‌های دسترسی

### کد نمونه

#### ثبت اتصال از ماژول احراز هویت
```javascript
// در ماژول احراز هویت
const response = await fetch('http://cms.econojin.com/api/module-integration/connect', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Module-Token': 'auth-module-api-key'
  },
  body: JSON.stringify({
    module: 'auth',
    endpoint: 'https://auth.econojin.com/api'
  })
});
```

#### دریافت اطلاعات کاربر جدید
```javascript
// زمان ثبت نام کاربر جدید
const newUser = await registerUser(userData);

// ارسال اطلاعات کاربر به CMS
await fetch('http://cms.econojin.com/api/module-integration/receive-content', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Module-Token': 'auth-module-api-key'
  },
  body: JSON.stringify({
    module: 'auth',
    content: {
      type: 'user',
      id: newUser.id,
      username: newUser.username,
      email: newUser.email,
      tenant: newUser.tenant
    }
  })
});
```

## مثال ۳: استفاده از وب‌هوک‌ها

### ثبت وب‌هوک برای دریافت اعلان از CMS

```javascript
// در ماژول جلویی برای دریافت اعلان از CMS
const response = await fetch('http://cms.econojin.com/api/module-integration/register-webhook', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Module-Token': 'frontend-module-api-key'
  },
  body: JSON.stringify({
    endpoint: 'https://frontend.econojin.com/webhook/cms-updates',
    events: ['content.create', 'content.update', 'content.delete']
  })
});
```

### دریافت اعلان از CMS

```javascript
// در ماژول جلویی - endpoint وب‌هوک
app.post('/webhook/cms-updates', async (req, res) => {
  const { event, data } = req.body;
  
  switch (event) {
    case 'content.create':
      // به‌روزرسانی کش یا CDN
      await updateCache(data.id, data.type);
      break;
      
    case 'content.update':
      // به‌روزرسانی محتوای موجود
      await updateExistingContent(data.id, data.type);
      break;
      
    case 'content.delete':
      // حذف محتوای کش شده
      await removeCachedContent(data.id, data.type);
      break;
  }
  
  res.status(200).send('OK');
});
```

## مثال ۴: همگام‌سازی محتوا

### زمان ایجاد محتوای جدید در CMS

```javascript
// این فراخوانی به صورت خودکار از طریق گسترش (extension) انجام می‌شود
// در src/extensions/module-integration/bootstrap.ts

// اما می‌توان به صورت دستی نیز انجام شود
await strapi.service('module-integration-service').syncContentToModules(
  pageData,
  'api::page.page',
  'create'
);
```

## مثال ۵: مدیریت امنیت

### اعتبارسنجی درخواست‌ها

```javascript
// در میان‌افزار module-connection.ts
// تمام درخواست‌ها از ماژول‌های متصل باید شامل توکن معتبر باشند
const moduleToken = ctx.get('X-Module-Token');
if (!moduleToken) {
  ctx.status = 401;
  ctx.body = { error: 'Module token required' };
  return;
}

const isValid = await validateModuleToken(strapi, moduleToken);
if (!isValid) {
  ctx.status = 401;
  ctx.body = { error: 'Invalid module token' };
  return;
}
```

## نکات عملی

### ۱. مدیریت خطا
همیشه درخواست‌ها به ماژول‌های دیگر را درون بلاک try-catch قرار دهید:

```javascript
try {
  await fetch(otherModuleEndpoint, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: { 'Content-Type': 'application/json' }
  });
} catch (error) {
  strapi.log.error(`Error communicating with module: ${error.message}`);
  // ادامه فرآیند بدون وابستگی به ماژول دیگر
}
```

### ۲. زمان‌بندی اتصالات
برای عملکرد بهتر، اتصالات را به صورت async انجام دهید:

```javascript
// انجام درخواست به صورت پس‌زمینه
process.nextTick(async () => {
  try {
    await notifyOtherModules(data);
  } catch (error) {
    strapi.log.error(`Background module notification failed: ${error.message}`);
  }
});
```

### ۳. مدیریت وضعیت اتصال
همیشه وضعیت اتصال به ماژول‌های دیگر را بررسی کنید:

```javascript
const connectionStatus = await getConnectionStatus(moduleName);
if (!connectionStatus.isConnected) {
  // استفاده از حالت پشتیبان یا کش
  return getCachedData();
}
```