'use strict';
const { createCoreService } = require('@strapi/strapi').factories;
module.exports = createCoreService('api::registered-webhook.registered-webhook');
