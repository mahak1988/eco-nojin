import { ensureDefaultPermissions } from './bootstrap/ensure-permissions';

export default {
  /**
   * An asynchronous register function that runs before
   * your application is initialized.
   */
  register(/* { strapi } */) {},

  /**
   * Called when the server is fully loaded.
   */
  async bootstrap({ strapi }) {
    strapi.log.info('[cms] EcoNojin CMS bootstrap — content-types: page, blog-post, category, tag');
    await ensureDefaultPermissions(strapi);
  },
};
