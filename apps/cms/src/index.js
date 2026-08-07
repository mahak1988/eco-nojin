'use strict';

const { ensureDefaultPermissions } = require('./bootstrap/ensure-permissions');

module.exports = {
  register(/* { strapi } */) {},

  async bootstrap({ strapi }) {
    strapi.log.info('[cms] EcoNojin CMS bootstrap — content-types: page, blog-post, category, tag');
    try {
      await ensureDefaultPermissions(strapi);
    } catch (e) {
      strapi.log.warn(`[cms] permissions bootstrap skipped: ${e && e.message ? e.message : e}`);
    }
  },
};
