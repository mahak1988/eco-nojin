# API Reference

This documentation outlines the API surface for the multi-tenant SaaS platform.

## Frontend API

- `GET /api/revalidate` - Internal webhook endpoint for Strapi content revalidation.

## Backend integrations

- **Supabase Auth**: user sign-up, sign-in, and role management.
- **Supabase Storage**: file uploads for tenant assets.
- **Supabase Realtime**: dashboard streaming and notifications.
- **Strapi CMS**: content endpoints for marketing pages and blog content.

## Notes

- API endpoints should be protected with role-based authorization.
- Tenant context must be derived from session claims and Supabase JWT.
- Use RLS policies in Supabase to isolate tenant data.
