import { StrapiService } from '@strapi/strapi';

interface PWAService {
  generateManifest(tenant: string): Promise<any>;
  generateServiceWorker(): Promise<string>;
  cacheContentForOffline(contentId: string, contentType: string, userId: string): Promise<void>;
  syncOfflineChanges(userId: string): Promise<void>;
  checkOfflineAvailability(contentId: string, contentType: string): Promise<boolean>;
}

/**
 * سرویس ویژگی‌های PWA
 * امکان ایجاد ویژگی‌های Progressive Web App برای کار بدون اینترنت را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): PWAService => ({
  /**
   * تولید فایل manifest برای PWA
   */
  async generateManifest(tenant: string): Promise<any> {
    try {
      // دریافت تنظیمات tenant برای اطلاعات manifest
      const tenantInfo = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      // ایجاد اطلاعات manifest
      const manifest = {
        name: tenantInfo?.settings?.siteName || 'EconoJin CMS',
        short_name: tenantInfo?.settings?.siteName?.substring(0, 12) || 'EconoJin',
        description: tenantInfo?.settings?.siteDescription || 'Content Management System',
        start_url: '/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#000000',
        orientation: 'portrait',
        icons: [
          {
            src: tenantInfo?.settings?.logo?.url || '/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: tenantInfo?.settings?.logo?.url || '/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ],
        categories: ['productivity', 'utilities'],
        lang: 'fa-IR',
        dir: 'rtl'
      };

      strapi.log.info(`Generated PWA manifest for tenant: ${tenant}`);
      return manifest;
    } catch (error) {
      strapi.log.error(`Error generating PWA manifest: ${error.message}`);
      throw error;
    }
  },

  /**
   * تولید فایل سرویس ورکر
   */
  async generateServiceWorker(): Promise<string> {
    try {
      // تولید کد سرویس ورکر
      const serviceWorkerCode = `
// EconoJin CMS Service Worker
const CACHE_NAME = 'econojin-cms-v1';
const urlsToCache = [
  '/',
  '/css/app.css',
  '/js/app.js',
  '/fonts/',
  '/images/logo.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_CONTENT') {
    cacheContentForOffline(event.data.payload);
  }
  
  if (event.data && event.data.type === 'SYNC_CHANGES') {
    syncOfflineChanges(event.data.userId);
  }
});

async function cacheContentForOffline(payload) {
  const { contentId, contentType, contentData } = payload;
  const cacheKey = \`\${contentType}-\${contentId}\`;
  
  const cache = await caches.open(CACHE_NAME);
  await cache.put(
    new Request(\`/api/offline/\${contentType}/\${contentId}\`),
    new Response(JSON.stringify(contentData), {
      headers: { 'Content-Type': 'application/json' }
    })
  );
}

async function syncOfflineChanges(userId) {
  // Sync any pending changes from IndexedDB
  if ('indexedDB' in self) {
    const dbPromise = idb.openDB('econojin-offlinedb', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('changes')) {
          const store = db.createObjectStore('changes', { keyPath: 'id', autoIncrement: true });
          store.createIndex('userId', 'userId');
        }
      }
    });
    
    const db = await dbPromise;
    const tx = db.transaction('changes', 'readonly');
    const store = tx.objectStore('changes');
    const changes = await store.index('userId').getAll(IDBKeyRange.only(userId));
    
    // Send changes to server
    for (const change of changes) {
      try {
        await fetch('/api/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(change)
        });
        
        // Remove synced change
        const writeTx = db.transaction('changes', 'readwrite');
        const writeStore = writeTx.objectStore('changes');
        await writeStore.delete(change.id);
      } catch (error) {
        console.error('Failed to sync change:', error);
      }
    }
  }
}

// Import idb for IndexedDB operations
importScripts('https://unpkg.com/idb@7.0.1/build/iife/index-min.js');
`;

      strapi.log.info('Generated PWA service worker');
      return serviceWorkerCode;
    } catch (error) {
      strapi.log.error(`Error generating service worker: ${error.message}`);
      throw error;
    }
  },

  /**
   * کش کردن محتوا برای کار بدون اینترنت
   */
  async cacheContentForOffline(contentId: string, contentType: string, userId: string): Promise<void> {
    try {
      // دریافت محتوای کامل
      const content = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (!content) {
        throw new Error(`Content not found: ${contentId}`);
      }

      // ذخیره در کش سرور برای ارائه به سرویس ورکر
      const cacheKey = `${contentType}-${contentId}-${userId}`;
      const cacheData = {
        contentId,
        contentType,
        contentData: content,
        userId,
        cachedAt: new Date().toISOString()
      };

      // ذخیره در جدول کش
      await strapi.query('api::offline-cache.offline-cache').create({
        data: {
          key: cacheKey,
          data: cacheData,
          userId,
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // ۷ روز
        }
      });

      strapi.log.info(`Cached content ${contentId} for offline use by user ${userId}`);
    } catch (error) {
      strapi.log.error(`Error caching content for offline: ${error.message}`);
      throw error;
    }
  },

  /**
   * همگام‌سازی تغییرات بدون اینترنت
   */
  async syncOfflineChanges(userId: string): Promise<void> {
    try {
      // دریافت تغییرات ذخیره شده بدون اینترنت برای کاربر
      const offlineChanges = await strapi.query('api::offline-change.offline-change').findMany({
        where: {
          userId,
          synced: false
        }
      });

      for (const change of offlineChanges) {
        try {
          // اعمال تغییرات بر اساس نوع عمل
          switch (change.operation) {
            case 'create':
              await strapi.entityService.create(`api::${change.contentType}.${change.contentType}`, {
                data: change.payload
              });
              break;
              
            case 'update':
              await strapi.entityService.update(`api::${change.contentType}.${change.contentType}`, change.entityId, {
                data: change.payload
              });
              break;
              
            case 'delete':
              await strapi.entityService.delete(`api::${change.contentType}.${change.contentType}`, change.entityId);
              break;
              
            default:
              strapi.log.warn(`Unknown operation: ${change.operation}`);
          }

          // به‌روزرسانی وضعیت همگام‌سازی
          await strapi.query('api::offline-change.offline-change').update({
            where: { id: change.id },
            data: { synced: true, syncedAt: new Date().toISOString() }
          });

          strapi.log.info(`Synced offline change ${change.id} for user ${userId}`);
        } catch (syncError) {
          strapi.log.error(`Failed to sync change ${change.id}: ${syncError.message}`);
        }
      }
    } catch (error) {
      strapi.log.error(`Error syncing offline changes: ${error.message}`);
      throw error;
    }
  },

  /**
   * بررسی در دسترس بودن محتوا بدون اینترنت
   */
  async checkOfflineAvailability(contentId: string, contentType: string): Promise<boolean> {
    try {
      // بررسی وجود محتوا در کش بدون اینترنت
      const cacheKey = `${contentType}-${contentId}`;
      const cachedItem = await strapi.query('api::offline-cache.offline-cache').findOne({
        where: {
          key: { $startsWith: cacheKey }
        }
      });

      if (cachedItem && new Date(cachedItem.expiresAt) > new Date()) {
        return true;
      }

      return false;
    } catch (error) {
      strapi.log.error(`Error checking offline availability: ${error.message}`);
      return false;
    }
  }
});