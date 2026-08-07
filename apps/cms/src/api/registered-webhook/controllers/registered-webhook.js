'use strict';
const { createCoreController } = require('@strapi/strapi').factories;
module.exports = createCoreController('api::registered-webhook.registered-webhook');
