# ⚡ Eco-Nojin Ultra-Fast Analysis Report
**Generated:** 2026-08-08 06:48:27 | **Execution Time:** 13.85 seconds

## 📊 Executive Summary
- **Total Files:** 1,930
- **Total Lines:** 792,662
- **Total Size:** 59.36 MB
- **Security Alerts:** 10
- **Technical Debt (TODOs):** 51
- **Damaged Files:** 23
- **Orphan Files:** 10

## ⚠️ Damaged Files (Action Required)
| File | Status | Issues |
|------|--------|--------|
| `apps\admin_panel\performance_patch.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\admin_panel\tasks.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\admin_panel\service_security_patch.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\api\routes\library.py` | DAMAGED_CRITICAL | SyntaxError: invalid syntax (Line 56) |
| `apps\ml\global_sensitivity.py` | DAMAGED_CRITICAL | SyntaxError: f-string: expecting '}' (Line 352) |
| `apps\shared_core\middleware\request_id.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\shared_knowledge\knowledge\seed_data.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\shared_knowledge\knowledge\tek_models.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\shared_knowledge\knowledge\tek_router.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\shared_knowledge\knowledge\tek_matcher.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\simulation\carbon_cycle\daycent.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\simulation\data\nasa_power.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\simulation\registry.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\simulation\tests\test_paper_validation.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\simulation\tests\test_physical_laws.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\simulation\soil\hydrus.py` | DAMAGED_CRITICAL | SyntaxError: invalid non-printable character U+FEFF (Line 1) |
| `apps\web\src\components\simulators\paramI18n.ts` | DAMAGED_MINOR | Unbalanced brackets/braces |
| `contracts\typechain-types\common.ts` | DAMAGED_MINOR | Unbalanced brackets/braces |
| `data\offline_content\offline_package.py` | DAMAGED_CRITICAL | SyntaxError: unterminated string literal (detected at line 48) (Line 48) |
| `packages\ui\src\components\config.py` | DAMAGED_CRITICAL | SyntaxError: unexpected indent (Line 5) |

## 🗑️ Orphan Files (Unreferenced)
| File | Size (KB) | Lines |
|------|-----------|-------|
| `apps\admin_panel\frontend\src\utils\a11yUtils.ts` | 2.5 | 95 |
| `apps\admin_panel\frontend\src\components\CustomizableDashboard.tsx` | 20.5 | 471 |
| `apps\admin_panel\cms_routes.py` | 3.2 | 97 |
| `apps\admin_panel\frontend\src\styles\globals.css` | 2.0 | 61 |
| `apps\admin_panel\frontend\src\pages\Dashboard.tsx` | 9.1 | 186 |
| `apps\admin_panel\frontend\src\components\ContentManagement.tsx` | 13.9 | 334 |
| `apps\admin_panel\derived_analytics.py` | 11.0 | 292 |
| `alembic\env.py` | 2.0 | 72 |
| `agents\memory\vectors.json` | 22.1 | 790 |
| `01_fix_auth_vulnerabilities.py` | 14.3 | 321 |

## 🔒 Security Vulnerabilities

Found **10** potential security issues (Hardcoded secrets, SQLi, Eval). Immediate audit required.

## 🏗️ Architecture & Stack Detection
- **React**: 441 files
- **Satellite/IoT**: 262 files
- **SQLAlchemy**: 196 files
- **FastAPI**: 178 files
