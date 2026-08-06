/**
 * Idempotent default permissions for core content-types + Editor role.
 */

type StrapiLike = {
  log: { info: (m: string) => void; warn: (m: string) => void; error: (m: string) => void };
  db: {
    query: (uid: string) => {
      findOne: (args: unknown) => Promise<any>;
      findMany: (args?: unknown) => Promise<any[]>;
      create: (args: unknown) => Promise<any>;
    };
  };
};

const CONTENT_ACTIONS = {
  page: [
    'api::page.page.find',
    'api::page.page.findOne',
    'api::page.page.create',
    'api::page.page.update',
    'api::page.page.delete',
  ],
  'blog-post': [
    'api::blog-post.blog-post.find',
    'api::blog-post.blog-post.findOne',
    'api::blog-post.blog-post.create',
    'api::blog-post.blog-post.update',
    'api::blog-post.blog-post.delete',
  ],
  category: [
    'api::category.category.find',
    'api::category.category.findOne',
    'api::category.category.create',
    'api::category.category.update',
    'api::category.category.delete',
  ],
  tag: [
    'api::tag.tag.find',
    'api::tag.tag.findOne',
    'api::tag.tag.create',
    'api::tag.tag.update',
    'api::tag.tag.delete',
  ],
} as const;

const PUBLIC_ACTIONS = [
  'api::page.page.find',
  'api::page.page.findOne',
  'api::blog-post.blog-post.find',
  'api::blog-post.blog-post.findOne',
  'api::category.category.find',
  'api::category.category.findOne',
  'api::tag.tag.find',
  'api::tag.tag.findOne',
];

const AUTHENTICATED_ACTIONS = [
  ...CONTENT_ACTIONS.page,
  ...CONTENT_ACTIONS['blog-post'],
  ...CONTENT_ACTIONS.category,
  ...CONTENT_ACTIONS.tag,
];

/** Editor: create/update/read — no delete */
const EDITOR_ACTIONS = [
  'api::page.page.find',
  'api::page.page.findOne',
  'api::page.page.create',
  'api::page.page.update',
  'api::blog-post.blog-post.find',
  'api::blog-post.blog-post.findOne',
  'api::blog-post.blog-post.create',
  'api::blog-post.blog-post.update',
  'api::category.category.find',
  'api::category.category.findOne',
  'api::category.category.create',
  'api::category.category.update',
  'api::tag.tag.find',
  'api::tag.tag.findOne',
  'api::tag.tag.create',
  'api::tag.tag.update',
];

async function ensurePermission(
  strapi: StrapiLike,
  roleId: number,
  action: string,
  existing: Set<string>
): Promise<void> {
  if (existing.has(action)) return;
  try {
    await strapi.db.query('plugin::users-permissions.permission').create({
      data: { action, role: roleId },
    });
    existing.add(action);
  } catch (e: any) {
    strapi.log.warn(`[cms:permissions] skip ${action}: ${e?.message || e}`);
  }
}

async function ensureEditorRole(strapi: StrapiLike): Promise<any | null> {
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
  } catch (e: any) {
    strapi.log.warn(`[cms:permissions] Editor role create failed: ${e?.message || e}`);
    return null;
  }
}

export async function ensureDefaultPermissions(strapi: StrapiLike): Promise<void> {
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

    const roleIds = [publicRole.id, authRole.id, editorRole?.id].filter(Boolean) as number[];
    const allPerms = await permQuery.findMany({
      where: { role: { $in: roleIds } },
      limit: 1000,
    });

    const byRole = new Map<number, Set<string>>();
    for (const id of roleIds) byRole.set(id, new Set());
    for (const p of allPerms || []) {
      const rid = typeof p.role === 'object' ? p.role?.id : p.role;
      if (rid == null || !byRole.has(rid)) continue;
      byRole.get(rid)!.add(p.action);
    }

    for (const action of PUBLIC_ACTIONS) {
      await ensurePermission(strapi, publicRole.id, action, byRole.get(publicRole.id)!);
    }
    for (const action of AUTHENTICATED_ACTIONS) {
      await ensurePermission(strapi, authRole.id, action, byRole.get(authRole.id)!);
    }
    if (editorRole) {
      for (const action of EDITOR_ACTIONS) {
        await ensurePermission(strapi, editorRole.id, action, byRole.get(editorRole.id)!);
      }
    }

    strapi.log.info(
      '[cms:permissions] defaults applied — Public:read | Authenticated:CRUD | Editor:no-delete'
    );
  } catch (e: any) {
    strapi.log.error(`[cms:permissions] bootstrap failed: ${e?.message || e}`);
  }
}

export const ROLE_MATRIX = {
  public: PUBLIC_ACTIONS,
  authenticated: AUTHENTICATED_ACTIONS,
  editor: EDITOR_ACTIONS,
};
