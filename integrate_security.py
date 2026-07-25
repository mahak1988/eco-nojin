#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
integrate_security.py — یکپارچه‌سازی خودکار Security Middleware با FastAPI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
فایل main.py/app.py را پیدا و middleware امنیتی را اضافه می‌کند.
'''
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── کد import و middleware ──
IMPORT_BLOCK = '''
# ── Spider Web Security ──
from security.middleware.security_middleware import SecurityMiddleware
from security.config import SecurityConfig
'''

MIDDLEWARE_BLOCK = '''
# ── Spider Web Security Middleware (Layer 3-4) ──
app.add_middleware(SecurityMiddleware)

# ── CORS (Layer 3) ──
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=SecurityConfig.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
'''

# ── الگوهای جستجوی فایل اصلی FastAPI ──
CANDIDATE_FILES = [
    'apps/api/main.py',
    'apps/api/app.py',
    'apps/main.py',
    'apps/app.py',
    'main.py',
    'app.py',
    'apps/shared_core/main.py',
    'apps/shared_core/app.py',
]


def find_fastapi_app() -> Path | None:
    '''پیدا کردن فایل اصلی FastAPI.'''
    # اولویت ۱: فایل‌های شناخته‌شده
    for rel in CANDIDATE_FILES:
        p = ROOT / rel
        if p.exists():
            text = p.read_text(encoding='utf-8', errors='ignore')
            if 'FastAPI' in text or 'fastapi' in text:
                return p

    # اولویت ۲: جستجوی فایل‌های حاوی FastAPI()
    for py in ROOT.rglob('*.py'):
        if any(skip in str(py) for skip in
               ('node_modules', '.pnpm-store', '__pycache__', '.venv',
                'venv', '.git', 'security/', 'tests/', 'test_')):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore')
            if 'FastAPI(' in text and 'app' in text:
                return py
        except OSError:
            continue
    return None


def integrate(app_file: Path, apply: bool) -> bool:
    '''اضافه کردن middleware به فایل FastAPI.'''
    text = app_file.read_text(encoding='utf-8')

    # بررسی اینکه آیا قبلاً اضافه شده
    if 'SecurityMiddleware' in text:
        print(f'  ✅ SecurityMiddleware قبلاً در {app_file.name} وجود دارد')
        return True

    print(f'  📄 فایل هدف: {app_file.relative_to(ROOT)}')

    # ── ۱. افزودن import ──
    # پیدا کردن آخرین import
    lines = text.splitlines(keepends=True)
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('import ', 'from ')):
            last_import_idx = i

    # اضافه کردن import بعد از آخرین import
    import_lines = IMPORT_BLOCK.strip().splitlines(keepends=True)
    for j, imp_line in enumerate(import_lines):
        lines.insert(last_import_idx + 1 + j, imp_line)

    # ── ۲. افزودن middleware ──
    # پیدا کردن خط app = FastAPI(...)
    text_joined = ''.join(lines)
    app_match = re.search(r'(app\s*=\s*FastAPI\([^)]*\))', text_joined)
    if not app_match:
        print('  ⚠️  الگوی app = FastAPI(...) یافت نشد')
        print('  → middleware را دستی اضافه کنید:')
        print('    app.add_middleware(SecurityMiddleware)')
        return False

    # پیدا کردن موقعیت بعد از app = FastAPI(...)
    insert_pos = app_match.end()
    # پیدا کردن خط بعدی
    next_newline = text_joined.find('\n', insert_pos)
    if next_newline == -1:
        next_newline = len(text_joined)

    # اضافه کردن middleware
    middleware_lines = '\n' + MIDDLEWARE_BLOCK.strip() + '\n'
    text_joined = (text_joined[:next_newline] +
                   middleware_lines +
                   text_joined[next_newline:])

    # ── ۳. validate ──
    try:
        ast.parse(text_joined)
        print('  ✅ syntax معتبر است')
    except SyntaxError as e:
        print(f'  ❌ خطای syntax: {e}')
        print('  → تغییرات اعمال نشد')
        return False

    if apply:
        app_file.write_text(text_joined, encoding='utf-8')
        print(f'  ✅ {app_file.name} به‌روزرسانی شد')
        return True
    else:
        print('  → برای اعمال: --apply')
        # نمایش پیش‌نمایش
        print('\n  ── پیش‌نمایش تغییرات ──')
        for line in IMPORT_BLOCK.strip().splitlines():
            print(f'  + {line}')
        print('  ...')
        for line in MIDDLEWARE_BLOCK.strip().splitlines()[:5]:
            print(f'  + {line}')
        print('  + ...')
        return True


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🔗 یکپارچه‌سازی Security Middleware با FastAPI')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت گزارش — برای اعمال: --apply')

    # پیدا کردن فایل FastAPI
    print('\n  [۱] جستجوی فایل اصلی FastAPI …')
    app_file = find_fastapi_app()
    if not app_file:
        print('  ❌ فایل FastAPI یافت نشد')
        print('  → فایل‌های بررسی‌شده:')
        for rel in CANDIDATE_FILES:
            exists = '✅' if (ROOT / rel).exists() else '⚪'
            print(f'     {exists} {rel}')
        return 1

    # یکپارچه‌سازی
    print(f'\n  [۲] یکپارچه‌سازی …')
    ok = integrate(app_file, apply)

    if ok and apply:
        # تست import
        print(f'\n  [۳] تست import …')
        r = subprocess.run(
            [sys.executable, '-c',
             'from security.middleware.security_middleware import SecurityMiddleware; '
             'from security.config import SecurityConfig; '
             'print("OK")'],
            cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0 and 'OK' in r.stdout:
            print('  ✅ import موفق')
        else:
            print(f'  ⚠️  import ناموفق: {r.stderr[:200]}')

        print(f'\n  [۴] commit و push:')
        print(f'     git add {app_file.relative_to(ROOT)}')
        print(f'     git commit -m "security: integrate spider web middleware with FastAPI"')
        print(f'     git push')

    print('\n' + '═' * 60)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())