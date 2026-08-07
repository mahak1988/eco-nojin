'use strict';

/** UIDs must match API folder names under src/api/ */
const CONTENT_ACTIONS = {
  page: [
    'api::pages.page.find',
    'api::pages.page.findOne',
    'api::pages.page.create',
    'api::pages.page.update',
    'api::pages.page.delete',
  ],
  'blog-post': [
    'api::blog-posts.blog-post.find',
    'api::blog-posts.blog-post.findOne',
    'api::blog-posts.blog-post.create',
    'api::blog-posts.blog-post.update',
    'api::blog-posts.blog-post.delete',
  ],
  category: [
    'api::categories.category.find',
    'api::categories.category.findOne',
    'api::categories.category.create',
    'api::categories.category.update',
    'api::categories.category.delete',
  ],
  tag: [
    'api::tags.tag.find',
    'api::tags.tag.findOne',
    'api::tags.tag.create',
    'api::tags.tag.update',
    'api::tags.tag.delete',
  ],
};

const PUBLIC_ACTIONS = [
  'api::pages.page.find',
  'api::pages.page.findOne',
  'api::blog-posts.blog-post.find',
  'api::blog-posts.blog-post.findOne',
  'api::categories.category.find',
  'api::categories.category.findOne',
  'api::tags.tag.find',
  'api::tags.tag.findOne',
];

const AUTHENTICATED_ACTIONS = [
  ...CONTENT_ACTIONS.page,
  ...CONTENT_ACTIONS['blog-post'],
  ...CONTENT_ACTIONS.category,
  ...CONTENT_ACTIONS.tag,
];

const EDITOR_ACTIONS = [
  'api::pages.page.find',
  'api::pages.page.findOne',
  'api::pages.page.create',
  'api::pages.page.update',
  'api::blog-posts.blog-post.find',
  'api::blog-posts.blog-post.findOne',
  'api::blog-posts.blog-post.create',
  'api::blog-posts.blog-post.update',
  'api::categories.category.find',
  'api::categories.category.findOne',
  'api::categories.category.create',
  'api::categories.category.update',
  'api::tags.tag.find',
  'api::tags.tag.findOne',
  'api::tags.tag.create',
  'api::tags.tag.update',
];

async function ensurePermission(strapi, roleId, action, existing) {
  if (existing.has(action)) return;
  try {
    await strapi.db.query('plugin::users-permissions.permission').create({
      data: { action, role: roleId },
    });
    existing.add(action);
  } catch (e) {
    strapi.log.warn(`[cms:permissions] skip ${action}: ${e && e.message ? e.message : e}`);
  }
}

async function ensureEditorRole(strapi) {
  const roleQuery = strapi.db.query('plugin::users-permissions.role');
  let editor = await roleQuery.findOne({ where: { type: 'editor' } });
  if (editor) return editor;
  editor = await roleQuery.findOne({ where: { name: 'Editor' } });
  if (editor) return editor;
  try {
    editor = await roleQuery.create({
      data: {
        name: 'Editor',
        description: 'Can create and edit content; cannot delete',
        type: 'editor',
      },
    });
    strapi.log.info('[cms:permissions] created role Editor');
    return editor;
  } catch (e) {
    strapi.log.warn(`[cms:permissions] Editor role create failed: ${e && e.message ? e.message : e}`);
    return null;
  }
}

async function ensureDefaultPermissions(strapi) {
  try {
    const roleQuery = strapi.db.query('plugin::users-permissions.role');
    const permQuery = strapi.db.query('plugin::users-permissions.permission');

    const publicRole = await roleQuery.findOne({ where: { type: 'public' } });
    const authRole = await roleQuery.findOne({ where: { type: 'authenticated' } });
    const editorRole = await ensureEditorRole(strapi);

    if (!publicRole || !authRole) {
      strapi.log.warn('[cms:permissions] Public/Authenticated roles not found yet');
      return;
    }

    const roleIds = [publicRole.id, authRole.id, editorRole && editorRole.id].filter(Boolean);
    const allPerms = await permQuery.findMany({
      where: { role: { $in: roleIds } },
      limit: 1000,
    });

    const byRole = new Map();
    for (const id of roleIds) byRole.set(id, new Set());
    for (const p of allPerms || []) {
      const rid = typeof p.role === 'object' ? p.role && p.role.id : p.role;
      if (rid == null || !byRole.has(rid)) continue;
      byRole.get(rid).add(p.action);
    }

    for (const action of PUBLIC_ACTIONS) {
      await ensurePermission(strapi, publicRole.id, action, byRole.get(publicRole.id));
    }
    for (const action of AUTHENTICATED_ACTIONS) {
      await ensurePermission(strapi, authRole.id, action, byRole.get(authRole.id));
    }
    if (editorRole) {
      for (const action of EDITOR_ACTIONS) {
        await ensurePermission(strapi, editorRole.id, action, byRole.get(editorRole.id));
      }
    }

    strapi.log.info(
      '[cms:permissions] defaults applied — Public:read | Authenticated:CRUD | Editor:no-delete'
    );
  } catch (e) {
    strapi.log.error(`[cms:permissions] bootstrap failed: ${e && e.message ? e.message : e}`);
  }
}

module.exports = {
  ensureDefaultPermissions,
  ROLE_MATRIX: {
    public: PUBLIC_ACTIONS,
    authenticated: AUTHENTICATED_ACTIONS,
    editor: EDITOR_ACTIONS,
  },
};
