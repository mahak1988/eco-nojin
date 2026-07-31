module.exports = {
  type: 'content-api',
  routes: [
    {
      method: 'POST',
      path: '/module-integration/connect',
      handler: 'module-integration.connect',
      config: {
        policies: ['global::module-access'],
      },
    },
    {
      method: 'POST',
      path: '/module-integration/sync-content',
      handler: 'module-integration.syncContent',
      config: {
        policies: ['global::module-access'],
      },
    },
    {
      method: 'POST',
      path: '/module-integration/receive-content',
      handler: 'module-integration.receiveContent',
      config: {
        policies: ['global::module-access'],
      },
    },
    {
      method: 'POST',
      path: '/module-integration/register-webhook',
      handler: 'module-integration.registerWebhook',
      config: {
        policies: ['global::module-access'],
      },
    },
    {
      method: 'DELETE',
      path: '/module-integration/unregister-webhook',
      handler: 'module-integration.unregisterWebhook',
      config: {
        policies: ['global::module-access'],
      },
    },
  ],
};