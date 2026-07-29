# Changelog

## [2.0.1] Phase 0 complete

### Fixed
- JWT via python-jose only (no PyJWT import)
- auth router registration
- Broken Depends syntax across API routers
- admin_panel / scenario `from __future__` order
- validation `await` outside async
- Optional modules (numba, satellite) logged at DEBUG

### Added
- RBAC tables + seed + require_permission
- Pagination envelope (data/meta)
- Access + refresh token helpers + cookie kwargs

### Verified
- health, rbac/seed, education/courses, accounting/summary
