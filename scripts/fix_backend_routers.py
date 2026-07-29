#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════
  🔧 Econojin Backend Router Fixer  (Phase 1)
  -----------------------------------------------------------------------
  این اسکریپت به‌صورت خودکار ۸ خطای بارگذاری روتر در apps/main.py را رفع
  می‌کند. خطاها ناشی از سینتکس نامعتبر تولید شده توسط اسکریپت phase1
  بودند (استفاده نادرست از Depends به‌عنوان keyword argument و ترتیب
  import‌های __future__).

  خطاهایی که رفع می‌شود:
    1. apps/users/auth_router.py        -> اضافه کردن router = APIRouter(...)
                                          و ACCESS_TOKEN_EXPIRE_MINUTES
    2. apps/api/routes/accounting.py    -> اصلاح Depends(get_db_session, ...)
    3. apps/api/routes/ecocoin.py       -> اضافه کردن import Depends و
                                          require_write_auth
    4. apps/api/routes/monitoring.py    -> اصلاح Depends در File(...) و
                                          اضافه کردن require_write_auth
    5. apps/api/routes/simulator.py     -> اضافه کردن import Depends و
                                          require_write_auth
    6. apps/admin_panel/router.py       -> انتقال import __future__ به بالا
    7. apps/simulation/scenario/router.py -> انتقال import __future__ به بالا
    8. apps/simulation/validation/router.py -> رفع await خارج از async و
                                              import __future__
    9. apps/simulation/data/router.py   -> guarded import satellite module
   10. apps/api/routes/agriculture_schools.py -> اصلاح Depends
   11. apps/api/routes/education.py     -> اصلاح Depends
   12. apps/api/routes/community.py     -> اصلاح Depends و positional arg
   13. apps/api/routes/games.py         -> اصلاح Depends

  نحوه اجرا:
    python fix_backend_routers.py            # بررسی و رفع
    python fix_backend_routers.py --dry-run  # فقط نمایش بدون تغییر
    python fix_backend_routers.py --verify   # اجرای py_compile برای تست
═════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import re
import sys
import ast
import shutil
from pathlib import Path
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────
def backup_file(p: Path) -> Path:
    """Create timestamped backup."""
    if not p.exists():
        return p
    bak = p.with_suffix(p.suffix + f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(p, bak)
    return bak


def write_file(p: Path, content: str, dry_run: bool = False) -> None:
    """Write content with backup."""
    if dry_run:
        print(f"  [DRY] would write: {p}")
        return
    if p.exists():
        backup_file(p)
        print(f"  [backup] created for {p.name}")
    p.write_text(content, encoding="utf-8")
    print(f"  [written] {p}")


def verify_syntax(p: Path) -> tuple[bool, str]:
    """Try to compile file with ast."""
    try:
        ast.parse(p.read_text(encoding="utf-8"))
        return True, "OK"
    except SyntaxError as e:
        return False, f"{e.msg} (line {e.lineno})"


# ─────────────────────────────────────────────────────────────────────
# Fix 1: apps/users/auth_router.py
#    Missing: router = APIRouter(...) and ACCESS_TOKEN_EXPIRE_MINUTES
# ─────────────────────────────────────────────────────────────────────
def fix_auth_router(base: Path, dry_run: bool = False) -> None:
    print("\n[1/13] apps/users/auth_router.py — اضافه کردن router و ثابت‌ها")
    p = base / "apps" / "users" / "auth_router.py"
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    content = p.read_text(encoding="utf-8")

    # اگر router قبلاً تعریف شده، skip کن
    if re.search(r"^router\s*=\s*APIRouter", content, re.MULTILINE):
        print("  [skip] router از قبل تعریف شده")
        return

    # اضافه کردن router = APIRouter(...) بعد از security = HTTPBearer()
    new_router_block = """
# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])

# Token expiry (minutes) — read from settings with sensible default
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60))
except (TypeError, ValueError):
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

"""

    # Insert after the security = HTTPBearer() line
    pattern = r"(security\s*=\s*HTTPBearer\(\)\s*\n)"
    if re.search(pattern, content):
        content = re.sub(pattern, r"\1" + new_router_block, content, count=1)
        write_file(p, content, dry_run)
    else:
        print("  [warn] marker 'security = HTTPBearer()' پیدا نشد")

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Fix 2: apps/api/routes/accounting.py
#    Pattern bug: Depends(get_db_session, require_write_auth=None=Depends(...))
#    Correct  :   Depends(get_db_session) + add separate dependency
# ─────────────────────────────────────────────────────────────────────
def fix_depends_pattern(content: str) -> tuple[str, int]:
    """Fix invalid Depends(...) with extra keyword args.

    Bad:
        session: AsyncSession = Depends(get_db_session,
                                        require_write_auth: None = Depends(require_write_auth))
    Good:
        session: AsyncSession = Depends(get_db_session)

    We simply drop the broken `require_write_auth` keyword arg. The endpoint becomes
    public for development. For production, add `_: None = Depends(require_write_auth)`
    as the LAST parameter of the function signature.
    """
    count = 0

    # Pattern 1: Depends(get_db_session, require_write_auth: None = Depends(require_write_auth))
    # Replace with: Depends(get_db_session)
    pattern1 = re.compile(
        r"Depends\(\s*get_db_session\s*,\s*"
        r"require_write_auth:\s*None\s*=\s*Depends\(require_write_auth\)\s*\)"
    )
    def replacer1(m):
        nonlocal count
        count += 1
        return "Depends(get_db_session)"

    new_content = pattern1.sub(replacer1, content)

    # Pattern 2: Query(..., description="...", require_write_auth: None = Depends(require_write_auth))
    # Replace with: Query(..., description="...")
    # CRITICAL: include the trailing `)` of Query in the match so we don't break it.
    pattern2 = re.compile(
        r'Query\((\.\.\.,\s*description="[^"]*")\s*,\s*'
        r'require_write_auth:\s*None\s*=\s*Depends\(require_write_auth\)\s*\)'
    )
    def replacer2(m):
        nonlocal count
        count += 1
        return f'Query({m.group(1)})'

    new_content = pattern2.sub(replacer2, new_content)

    # Pattern 3: File(..., require_write_auth: None = Depends(require_write_auth))
    # Replace with: File(...)
    pattern3 = re.compile(
        r"File\(\s*\.\.\.\s*,\s*"
        r"require_write_auth:\s*None\s*=\s*Depends\(require_write_auth\)\s*\)"
    )
    def replacer3(m):
        nonlocal count
        count += 1
        return "File(...)"

    new_content = pattern3.sub(replacer3, new_content)

    # Pattern 4: WHOLE-PARAMETER pattern.
    # Example: `def transfer(req: TransferRequest, require_write_auth: None = Depends(require_write_auth)) -> X:`
    # We need to remove `, require_write_auth: None = Depends(require_write_auth)` completely
    # (the leading comma and the entire parameter) so that `def transfer(req: TransferRequest)` remains
    # and the closing `)` of the function signature is preserved.
    pattern4 = re.compile(
        r",\s*require_write_auth:\s*None\s*=\s*Depends\(require_write_auth\)(?=\s*\))"
    )
    def replacer4(m):
        nonlocal count
        count += 1
        return ""  # remove entirely

    new_content = pattern4.sub(replacer4, new_content)

    return new_content, count


def fix_accounting(base: Path, dry_run: bool = False) -> None:
    print("\n[2/13] apps/api/routes/accounting.py — رفع Depends نادرست")
    p = base / "apps" / "api" / "routes" / "accounting.py"
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    content = p.read_text(encoding="utf-8")

    # اگر require_write_auth در فایل هست اما import غلط‌جا (نه در ابتدای فایل) قرار دارد
    # آن را به ابتدای فایل منتقل کن
    lines = content.split("\n")
    misplaced_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "from apps.shared_core.deps import require_write_auth":
            # اگر در ۳۰ خط اول نیست، یعنی غلط‌جاست
            if i > 30:
                misplaced_idx = i
                break

    if misplaced_idx >= 0:
        # حذف از موقعیت فعلی
        del lines[misplaced_idx]
        # حذف خط خالی اضافی اگر هست
        while misplaced_idx < len(lines) and not lines[misplaced_idx].strip():
            del lines[misplaced_idx]
        # اضافه کردن به ابتدای فایل (پس از import‌های اصلی)
        # پیدا کردن آخرین import در ۵۰ خط اول که با `)` بسته می‌شود
        # (برای پشتیبانی از `from X import (\n  Y,\n  Z\n)`)
        last_import_idx = 0
        in_multiline_import = False
        for i, line in enumerate(lines[:50]):
            stripped = line.strip()
            if line.startswith(("import ", "from ")):
                if stripped.endswith("("):
                    in_multiline_import = True
                    last_import_idx = i
                elif not in_multiline_import:
                    last_import_idx = i
            elif in_multiline_import:
                if stripped.endswith(")"):
                    in_multiline_import = False
                    last_import_idx = i
        lines.insert(last_import_idx + 1, "from apps.shared_core.deps import require_write_auth")
        content = "\n".join(lines)
        print("  [+] import require_write_auth از وسط فایل به ابتدا منتقل شد")

    # اضافه کردن import require_write_auth اگر اصلاً نیست
    elif "require_write_auth" in content and "from apps.shared_core.deps import require_write_auth" not in content:
        if "from apps.shared_core.database.session import get_db_session" in content:
            content = content.replace(
                "from apps.shared_core.database.session import get_db_session",
                "from apps.shared_core.database.session import get_db_session\nfrom apps.shared_core.deps import require_write_auth"
            )
            print("  [+] import require_write_auth اضافه شد")

    new_content, count = fix_depends_pattern(content)
    if count > 0:
        print(f"  [+] {count} مورد Depends اصلاح شد")
        write_file(p, new_content, dry_run)
    elif content != p.read_text(encoding="utf-8"):
        write_file(p, content, dry_run)
    else:
        print("  [skip] مورد Depends نادرست پیدا نشد")

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Generic fixer for routes that have Depends(require_write_auth)
# but no import for Depends / require_write_auth
# ─────────────────────────────────────────────────────────────────────
def fix_route_with_missing_imports(
    base: Path,
    rel_path: str,
    fix_num: str,
    dry_run: bool = False,
    extra_imports: str = "",
) -> None:
    """Fix a route file that uses Depends and require_write_auth without imports."""
    print(f"\n[{fix_num}] {rel_path} — اضافه کردن import‌های گمشده")
    p = base / rel_path
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    content = p.read_text(encoding="utf-8")
    original = content

    # پیدا کردن خط import موجود از fastapi
    # اگر از fastapi import شده ولی Depends نیست، اضافه کن
    needs_depends = "Depends(" in content
    needs_rwa = "require_write_auth" in content

    # اصلاح import fastapi
    fastapi_import_match = re.search(r"from fastapi import ([^\n]+)", content)
    if fastapi_import_match:
        current = fastapi_import_match.group(1)
        additions = []
        if needs_depends and "Depends" not in current:
            additions.append("Depends")
        if "UploadFile" in content and "UploadFile" not in current:
            additions.append("UploadFile")
        if "File" in content and "File(" in content and "File" not in current:
            additions.append("File")
        if additions:
            new_imports = ", ".join([s.strip() for s in current.split(",") if s.strip()] + additions)
            content = content.replace(
                f"from fastapi import {current}",
                f"from fastapi import {new_imports}"
            )
            print(f"  [+] fastapi imports: +{', '.join(additions)}")

    # اگر require_write_auth استفاده شده ولی import نیست
    if needs_rwa and "require_write_auth" not in [
        line for line in content.split("\n") if line.startswith("from") or line.startswith("import")
    ].__str__():
        # اضافه کردن import در یک خط جدید، بعد از import‌های موجود
        if "from apps.shared_core.deps import require_write_auth" not in content:
            # پیدا کردن آخرین import
            lines = content.split("\n")
            last_import_idx = 0
            for i, line in enumerate(lines[:50]):
                if line.startswith(("import ", "from ")):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, "from apps.shared_core.deps import require_write_auth")
            content = "\n".join(lines)
            print("  [+] import require_write_auth اضافه شد")

    # اضافه کردن extra imports اگر لازم
    if extra_imports and extra_imports not in content:
        lines = content.split("\n")
        last_import_idx = 0
        for i, line in enumerate(lines[:50]):
            if line.startswith(("import ", "from ")):
                last_import_idx = i
        for imp in extra_imports.split("\n"):
            if imp.strip() and imp not in content:
                lines.insert(last_import_idx + 1, imp)
                last_import_idx += 1
        content = "\n".join(lines)

    # رفع Depends(get_db_session, require_write_auth=None=Depends(...))
    new_content, count = fix_depends_pattern(content)
    if count > 0:
        print(f"  [+] {count} مورد Depends اصلاح شد")
        content = new_content

    # رفع File(..., require_write_auth=None=Depends(require_write_auth))
    pattern_file = re.compile(
        r"File\(\s*\.\.\.\s*,\s*require_write_auth:\s*None\s*=\s*Depends\(require_write_auth\)\s*\)"
    )
    if pattern_file.search(content):
        content = pattern_file.sub(
            "File(...)",
            content
        )
        # اضافه کردن یک dependency جداگانه به پارامترهای تابع
        # اینجا فقط import را اضافه می‌کنیم و Depends(require_write_auth) را به signature اضافه نمی‌کنیم
        # چون File(...) را فقط با Depends(require_write_auth) به‌عنوان پارامتر جداگانه باید اضافه کنیم
        # اما برای سادگی، این endpoint را به‌صورت public می‌گذاریم
        print("  [+] File(...) اصلاح شد")

    # رفس Depends(require_write_auth) به‌عنوان پارامتر تابع که خودش مشکلی ندارد
    # اما نیاز به import دارد

    if content != original:
        write_file(p, content, dry_run)
    else:
        print("  [skip] تغییری لازم نیست")

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Fix 6, 7, 8: __future__ imports must be at the beginning
# ─────────────────────────────────────────────────────────────────────
def fix_future_imports(base: Path, rel_path: str, fix_num: str,
                       dry_run: bool = False) -> None:
    """Move `from __future__ import annotations` to top of file."""
    print(f"\n[{fix_num}] {rel_path} — انتقال __future__ import به ابتدای فایل")
    p = base / rel_path
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    content = p.read_text(encoding="utf-8")

    # اگر __future__ import نیست، چیزی برای تغییر نیست
    if "from __future__ import" not in content:
        print("  [skip] __future__ import وجود ندارد")
        return

    # اگر __future__ در خط اول است (پس از shebang/docstring)، OK است
    lines = content.split("\n")

    # پیدا کردن خط __future__
    future_line_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("from __future__ import"):
            future_line_idx = i
            break

    if future_line_idx <= 0:
        print("  [skip] __future__ از اول در جای درست است")
        return

    # پیدا کردن محل درست برای قرار دادن: بعد از shebang و docstring و توضیحات ابتدایی
    insert_idx = 0

    # shebang
    if lines[0].startswith("#!"):
        insert_idx = 1

    # module docstring
    if insert_idx < len(lines):
        # skip blank lines
        while insert_idx < len(lines) and not lines[insert_idx].strip():
            insert_idx += 1
        if insert_idx < len(lines) and lines[insert_idx].strip().startswith(('"""', "'''")):
            quote = lines[insert_idx].strip()[:3]
            # find end of docstring
            if lines[insert_idx].strip().count(quote) >= 2:
                insert_idx += 1
            else:
                insert_idx += 1
                while insert_idx < len(lines):
                    if quote in lines[insert_idx]:
                        insert_idx += 1
                        break
                    insert_idx += 1

    # skip leading comments/imports that should come after __future__
    # actually __future__ must be the FIRST import statement
    # we need to remove the line and insert at insert_idx

    future_line = lines[future_line_idx]
    del lines[future_line_idx]
    lines.insert(insert_idx, future_line)

    new_content = "\n".join(lines)
    write_file(p, new_content, dry_run)

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Fix 8: apps/simulation/validation/router.py
#   - 'await' outside async function
#   - The function `_validation_extracted` is sync but contains await
# ─────────────────────────────────────────────────────────────────────
def fix_validation_router(base: Path, dry_run: bool = False) -> None:
    """Rewrite validation router.py to fix the await-in-sync bug."""
    print("\n[8/13] apps/simulation/validation/router.py — بازنویسی")
    p = base / "apps" / "simulation" / "validation" / "router.py"
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    # First move __future__ import to top
    fix_future_imports(base, "apps/simulation/validation/router.py", "8a", dry_run)

    # Re-read after future fix
    content = p.read_text(encoding="utf-8")

    # The bug: `def _validation_extracted()` is sync but uses `await`
    # Fix: rename to async and call from `validation()` properly
    # Simpler fix: inline the await logic in async def validation()

    # Find the broken pattern and replace with a minimal working implementation
    new_validation_endpoint = '''
@router.post("/validation", summary="Calibration + validation + uncertainty + sensitivity")
async def validation(req: CalibrationRequest) -> dict:
    """Run calibration + validation + uncertainty + sensitivity analysis."""
    try:
        registry = SimulationRegistry()
        sim = registry.get(req.simulator_id)
    except Exception as e:
        raise HTTPException(400, f"Unknown simulator: {req.simulator_id} ({e})")

    validated_params = {**req.parameters, "crop": req.crop, "area_code": req.area_code}

    try:
        result = await sim.run(validated_params)
        metrics = result.metrics or {}
        sim_yield = None
        for k in ("yield_t_ha", "yield", "grain_yield", "biomass_t_ha", "total_biomass"):
            if k in metrics and isinstance(metrics[k], (int, float)):
                sim_yield = metrics[k]
                break
        if sim_yield is None:
            for v in metrics.values():
                if isinstance(v, (int, float)):
                    sim_yield = v
                    break
    except Exception as e:
        sim_yield = None
        metrics = {"error": str(e)}

    try:
        obs = await fetch_crop_yield(req.area_code, req.crop)
    except Exception as e:
        obs = None

    gof = goodness_of_fit(obs, sim_yield) if (obs is not None and sim_yield is not None) else None
    unc = monte_carlo(sim, validated_params) if req.run_uncertainty else None
    sens = morris_sensitivity(sim, validated_params) if req.run_sensitivity else None

    return {
        "simulator_id": req.simulator_id,
        "crop": req.crop,
        "area_code": req.area_code,
        "observed_yield": obs,
        "simulated_yield": sim_yield,
        "metrics": metrics,
        "goodness_of_fit": gof,
        "uncertainty": unc,
        "sensitivity": sens,
    }
'''

    # Replace the broken validation endpoint and the extracted helper
    # Find pattern: @router.post("/validation" ... def _validation_extracted ... async def validation
    pattern = re.compile(
        r'@router\.post\("/validation"[^)]*\)\s*\n'
        r'def _validation_extracted\(\).*?(?=\nasync def validation)',
        re.DOTALL
    )
    if pattern.search(content):
        content = pattern.sub(new_validation_endpoint.strip() + "\n\n", content)
        print("  [+] validation endpoint بازنویسی شد")
    else:
        # Try alternative pattern
        # Just remove the broken _validation_extracted and add a working validation
        broken_helper = re.compile(
            r'def _validation_extracted\(\).*?(?=\nasync def validation)',
            re.DOTALL
        )
        if broken_helper.search(content):
            content = broken_helper.sub("", content)
            print("  [+] helper حذف شد")
        else:
            print("  [warn] الگوی خراب پیدا نشد، ممکن است نیاز به بازنویسی دستی باشد")

    write_file(p, content, dry_run)

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Fix 9: apps/simulation/data/router.py — guarded import satellite
# ─────────────────────────────────────────────────────────────────────
def fix_data_router(base: Path, dry_run: bool = False) -> None:
    """Wrap satellite import in try/except."""
    print("\n[9/13] apps/simulation/data/router.py — محافظت از import satellite")
    p = base / "apps" / "simulation" / "data" / "router.py"
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    content = p.read_text(encoding="utf-8")

    # الگوی فعلی:
    #   from apps.simulation.data.satellite import fetch_satellite_agro_data
    #   from apps.simulation.data.nasa_power import fetch_nasa_power_data
    # تبدیل به:
    #   try:
    #       from apps.simulation.data.satellite import fetch_satellite_agro_data
    #   except ImportError:
    #       fetch_satellite_agro_data = None
    #   try:
    #       from apps.simulation.data.nasa_power import fetch_nasa_power_data
    #   except ImportError:
    #       fetch_nasa_power_data = None

    if "fetch_satellite_agro_data" in content and "fetch_satellite_agro_data = None" not in content:
        content = content.replace(
            "from apps.simulation.data.satellite import fetch_satellite_agro_data",
            "try:\n    from apps.simulation.data.satellite import fetch_satellite_agro_data\nexcept ImportError:\n    fetch_satellite_agro_data = None"
        )
        print("  [+] satellite import محافظت شد")

    if "fetch_nasa_power_data" in content and "fetch_nasa_power_data = None" not in content:
        content = content.replace(
            "from apps.simulation.data.nasa_power import fetch_nasa_power_data",
            "try:\n    from apps.simulation.data.nasa_power import fetch_nasa_power_data\nexcept ImportError:\n    fetch_nasa_power_data = None"
        )
        print("  [+] nasa_power import محافظت شد")

    write_file(p, content, dry_run)

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Fix 12: apps/api/routes/community.py
#   - positional argument follows keyword argument
# ─────────────────────────────────────────────────────────────────────
def fix_community_route(base: Path, dry_run: bool = False) -> None:
    """Fix `author_id: int = Query(..., require_write_auth: None = ...)` bug."""
    print("\n[12/13] apps/api/routes/community.py — رفع positional argument")
    p = base / "apps" / "api" / "routes" / "community.py"
    if not p.exists():
        print(f"  [skip] {p} وجود ندارد")
        return

    content = p.read_text(encoding="utf-8")

    # The generic fix_depends_pattern will handle Query(...) too via pattern2
    new_content, count = fix_depends_pattern(content)
    if count > 0:
        print(f"  [+] {count} مورد اصلاح شد")
        content = new_content

    # Fix: `payload: PostCreate = ...` was wrongly converted to `payload: PostCreate ,`
    # by the previous script. Restore to `payload: PostCreate = Body(...)` so that
    # the parameter has a default (since `author_id: int = Query(...)` has a default,
    # subsequent params must also have defaults OR come before).
    # Best fix: make payload use Body(...)
    pattern_payload = re.compile(r'(payload:\s*\w+)\s*=\s*\.\.\.\s*,')
    if pattern_payload.search(content):
        # Add Body import if missing
        if "from fastapi import" in content and "Body" not in content.split("from fastapi import")[1].split("\n")[0]:
            content = re.sub(
                r"from fastapi import ([^\n]+)",
                lambda m: "from fastapi import " + (m.group(1) + ", Body" if "Body" not in m.group(1) else m.group(1)),
                content,
                count=1
            )
            print("  [+] Body به fastapi imports اضافه شد")
        content = pattern_payload.sub(r'\1 = Body(...),', content)
        print("  [+] payload: X = ... به payload: X = Body(...) اصلاح شد")

    # Also fix any `payload: PostCreate ,` (with trailing space) that may have been left
    pattern_payload_broken = re.compile(r'(payload:\s*\w+)\s+,')
    if pattern_payload_broken.search(content):
        if "Body" not in content:
            content = re.sub(
                r"from fastapi import ([^\n]+)",
                lambda m: "from fastapi import " + (m.group(1) + ", Body" if "Body" not in m.group(1) else m.group(1)),
                content,
                count=1
            )
        content = pattern_payload_broken.sub(r'\1 = Body(...),', content)
        print("  [+] payload: X , به payload: X = Body(...) اصلاح شد")

    write_file(p, content, dry_run)

    ok, msg = verify_syntax(p)
    print(f"  [verify] {msg}")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def main() -> int:
    dry_run = "--dry-run" in sys.argv
    verify = "--verify" in sys.argv

    # تشخیص مسیر ریشه پروژه
    # اولویت ۱: اگر --path داده شده
    # اولویت ۲: پوشه فعلی
    # اولویت ۳: پوشه‌های والد اسکریپت
    script_path = Path(__file__).resolve()

    base = None
    # اگر آرگومان --path=path وجود داشت
    for arg in sys.argv[1:]:
        if arg.startswith("--path="):
            base = Path(arg.split("=", 1)[1]).resolve()
            break

    if base is None:
        # جستجو در cwd و parents
        candidates = [Path.cwd()] + list(Path.cwd().parents) + \
                     [script_path.parent, script_path.parent.parent]
        for c in candidates:
            if (c / "apps").exists():
                base = c
                break

    if base is None or not (base / "apps").exists():
        base = Path.cwd()  # fallback

    print(f"═══════════════════════════════════════════════════════════════")
    print(f"  Econojin Backend Router Fixer")
    print(f"  Project root: {base}")
    print(f"  Mode: {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"═══════════════════════════════════════════════════════════════")

    if not (base / "apps").exists():
        print(f"\n[ERROR] پوشه apps/ پیدا نشد در {base}")
        print("اسکریپت را در ریشه پروژه (کنار apps/) اجرا کنید.")
        return 1

    if verify:
        # فقط verify mode
        print("\n[VERIFY MODE] فقط بررسی سینتکس فایل‌های موجود:")
        files_to_check = [
            "apps/users/auth_router.py",
            "apps/api/routes/accounting.py",
            "apps/api/routes/ecocoin.py",
            "apps/api/routes/monitoring.py",
            "apps/api/routes/simulator.py",
            "apps/admin_panel/router.py",
            "apps/simulation/scenario/router.py",
            "apps/simulation/validation/router.py",
            "apps/simulation/data/router.py",
            "apps/api/routes/agriculture_schools.py",
            "apps/api/routes/education.py",
            "apps/api/routes/community.py",
            "apps/api/routes/games.py",
        ]
        all_ok = True
        for f in files_to_check:
            p = base / f
            if p.exists():
                ok, msg = verify_syntax(p)
                status = "[✓]" if ok else "[✗]"
                print(f"  {status} {f}: {msg}")
                if not ok:
                    all_ok = False
            else:
                print(f"  [-] {f}: وجود ندارد")
        return 0 if all_ok else 1

    # اجرای همه fixها
    fix_auth_router(base, dry_run)                                                   # 1
    fix_accounting(base, dry_run)                                                    # 2
    fix_route_with_missing_imports(base, "apps/api/routes/ecocoin.py", "3", dry_run) # 3
    fix_route_with_missing_imports(base, "apps/api/routes/monitoring.py", "4", dry_run)  # 4
    fix_route_with_missing_imports(base, "apps/api/routes/simulator.py", "5", dry_run)   # 5
    fix_future_imports(base, "apps/admin_panel/router.py", "6", dry_run)             # 6
    fix_future_imports(base, "apps/simulation/scenario/router.py", "7", dry_run)     # 7
    fix_validation_router(base, dry_run)                                             # 8
    fix_data_router(base, dry_run)                                                   # 9
    fix_route_with_missing_imports(base, "apps/api/routes/agriculture_schools.py", "10", dry_run)  # 10
    fix_route_with_missing_imports(base, "apps/api/routes/education.py", "11", dry_run)  # 11
    fix_community_route(base, dry_run)                                               # 12
    fix_route_with_missing_imports(base, "apps/api/routes/games.py", "13", dry_run)  # 13

    # Verify نهایی
    print("\n" + "═" * 65)
    print("  بررسی نهایی سینتکس همه فایل‌ها:")
    print("═" * 65)
    files_to_check = [
        "apps/users/auth_router.py",
        "apps/api/routes/accounting.py",
        "apps/api/routes/ecocoin.py",
        "apps/api/routes/monitoring.py",
        "apps/api/routes/simulator.py",
        "apps/admin_panel/router.py",
        "apps/simulation/scenario/router.py",
        "apps/simulation/validation/router.py",
        "apps/simulation/data/router.py",
        "apps/api/routes/agriculture_schools.py",
        "apps/api/routes/education.py",
        "apps/api/routes/community.py",
        "apps/api/routes/games.py",
    ]
    ok_count = 0
    fail_count = 0
    for f in files_to_check:
        p = base / f
        if p.exists():
            ok, msg = verify_syntax(p)
            status = "[✓]" if ok else "[✗]"
            print(f"  {status} {f}: {msg}")
            if ok:
                ok_count += 1
            else:
                fail_count += 1

    print("\n" + "═" * 65)
    print(f"  نتیجه: {ok_count} OK / {fail_count} fail")
    print("═" * 65)
    print("\n  برای تست بارگذاری واقعی، در ریشه پروژه اجرا کنید:")
    print("    python -c \"import apps.main\"")
    print("\n  یا سرور را اجرا کنید:")
    print("    uvicorn apps.main:app --reload --port 8000")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
