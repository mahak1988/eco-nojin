/**
 * Idempotent default permissions for core content-types.
 * Safe to run on every Strapi boot.
 */

type StrapiLike = {
  log: { info: (m: string) => void; warn: (m: string) => void; error: (m: string) => void };
  db: {
    query: (uid: string) => {
      findOne: (args: unknown) => Promise<any>;
      findMany: (args?: unknown) => Promise<any[]>;
      create: (args: unknown) => Promise<any>;
      deleteMany?: (args: unknown) => Promise<any>;
    };
  };
};

/** Content-type actions we manage */
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

/** Public: read published marketing content only */
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

/** Authenticated editors: full CRUD on content */
const AUTHENTICATED_ACTIONS = [
  ...CONTENT_ACTIONS.page,
  ...CONTENT_ACTIONS['blog-post'],
  ...CONTENT_ACTIONS.category,
  ...CONTENT_ACTIONS.tag,
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
      data: {
        action,
        role: roleId,
      },
    });
    existing.add(action);
  } catch (e: any) {
    // Duplicate or schema not ready yet
    strapi.log.warn(`[cms:permissions] skip ${action}: ${e?.message || e}`);
  }
}

export async function ensureDefaultPermissions(strapi: StrapiLike): Promise<void> {
  try {
    const roleQuery = strapi.db.query('plugin::users-permissions.role');
    const permQuery = strapi.db.query('plugin::users-permissions.permission');

    const publicRole = await roleQuery.findOne({ where: { type: 'public' } });
    const authRole = await roleQuery.findOne({ where: { type: 'authenticated' } });

    if (!publicRole || !authRole) {
      strapi.log.warn('[cms:permissions] Public/Authenticated roles not found yet');
      return;
    }

    const allPerms = await permQuery.findMany({
      where: {
        role: { $in: [publicRole.id, authRole.id] },
      },
      limit: 500,
    });

    const byRole = new Map<number, Set<string>>();
    byRole.set(publicRole.id, new Set());
    byRole.set(authRole.id, new Set());
    for (const p of allPerms || []) {
      const rid = typeof p.role === 'object' ? p.role?.id : p.role;
      if (rid == null) continue;
      if (!byRole.has(rid)) byRole.set(rid, new Set());
      byRole.get(rid)!.add(p.action);
    }

    for (const action of PUBLIC_ACTIONS) {
      await ensurePermission(strapi, publicRole.id, action, byRole.get(publicRole.id)!);
    }
    for (const action of AUTHENTICATED_ACTIONS) {
      await ensurePermission(strapi, authRole.id, action, byRole.get(authRole.id)!);
    }

    strapi.log.info(
      '[cms:permissions] defaults applied — Public: read content; Authenticated: full CRUD'
    );
  } catch (e: any) {
    strapi.log.error(`[cms:permissions] bootstrap failed: ${e?.message || e}`);
  }
}

export const ROLE_MATRIX = {
  public: PUBLIC_ACTIONS,
  authenticated: AUTHENTICATED_ACTIONS,
};
