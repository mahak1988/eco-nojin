export default {
  /**
   * Called when the server is fully loaded.
   */
  async bootstrap({ strapi }) {
    strapi.log.info('[cms] EcoNojin CMS bootstrap — content-types: page, blog-post, category, tag');
  },
};
