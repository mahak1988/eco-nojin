#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
cleanup_temp.py — حذف اسکریپت‌ها و فایل‌های موقت
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
فایل‌های ابزاری، گزارش‌ها و خروجی‌های موقت را حذف می‌کند.
فایل‌های اصلی (security/, .github/, project_analyzer.py, ...) حفظ می‌شوند.
'''
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── فایل‌های موقت برای حذف ──
TEMP_FILES = [
    # ابزارهای تحلیل
    'analyze_apps.py',
    'analyze_ecocoin_v2.py',
    'analyze_frontend.py',
    'apps-analysis.json',
    'fix_analyze.py',
    'upgrade_apps.py',
    'upgrade_phase1b.py',

    # ابزارهای i18n
    'discover_i18n.py',
    'extract_ui_keys.py',
    'extract_real_i18n.py',
    'clean_i18n_generator.py',
    'generate_i18n_from_base.py',
    'apply_clean_i18n.py',
    'sync_i18n.py',
    'advanced_i18n_analyzer.py',
    'master_i18n_extractor.py',
    'master_i18n_keys.txt',
    'master_i18n_keys_v2.txt',
    'master_base_template.json',
    'master_base_template_v2.json',

    # خروجی‌های i18n
    'orphaned_keys_bn.txt',
    'orphaned_keys_de.txt',
    'orphaned_keys_en.txt',
    'orphaned_keys_fa.txt',
    'orphaned_keys_fr.txt',
    'orphaned_keys_hi.txt',
    'orphaned_keys_id.txt',
    'orphaned_keys_it.txt',
    'orphaned_keys_pt.txt',
    'orphaned_keys_ru.txt',
    'orphaned_keys_sw.txt',
    'orphaned_keys_tr.txt',
    'orphaned_keys_zh-CN.txt',

    # ابزارهای sync
    'sync_repo.py',
    'sync_report_20260724_060311.json',
    'sync_report_20260724_060347.json',
    'sync_report_20260724_232131.json',
    'current_snapshot.json',
    'previous_snapshot.json',
    'run_sync.bat',

    # ابزارهای contracts
    'apply_contract_fixes.py',
    'smart_fix_contracts.py',
    'fix_security_modifiers.py',

    # ابزارهای متفرقه
    'merge_branches.py',
    'setup_security.py',
    'harden_security.py',
    'fix_bandit.py',
    'fix_integration.py',
    'complete_env.py',
]

# ── دایرکتوری‌های موقت ──
TEMP_DIRS = [
    'clean_i18n_output',
    'i18n_clean_output',
    'i18n_report',
]

# ── فایل‌هایی که هرگز حذف نشوند ──
KEEP = {
    'project_analyzer.py',
    'staged_scan.py',
    'secure_fix.py',
    '.gitignore',
    '.pre-commit-config.yaml',
    '.bandit',
    '.env.example',
}


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🧹 حذف اسکریپت‌ها و فایل‌های موقت')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت گزارش — برای اعمال: --apply')

    # ── ۱. شناسایی فایل‌های موجود ──
    found_files = []
    for name in TEMP_FILES:
        p = ROOT / name
        if p.exists() and name not in KEEP:
            found_files.append(name)

    found_dirs = []
    for name in TEMP_DIRS:
        p = ROOT / name
        if p.is_dir():
            found_dirs.append(name)

    # ── ۲. گزارش ──
    print(f'\n  📄 {len(found_files)} فایل موقت یافت شد:')
    for f in found_files:
        size = (ROOT / f).stat().st_size
        print(f'     🗑️  {f} ({size:,} bytes)')

    print(f'\n  📁 {len(found_dirs)} دایرکتوری موقت یافت شد:')
    for d in found_dirs:
        p = ROOT / d
        count = sum(1 for _ in p.rglob('*') if _.is_file())
        print(f'     🗑️  {d}/ ({count} فایل)')

    if not found_files and not found_dirs:
        print('\n  ✅ هیچ فایل موقتی یافت نشد')
        return 0

    # ── ۳. حذف ──
    if apply:
        print(f'\n{"─" * 60}')
        print('  🗑️  حذف …')

        # حذف فایل‌ها
        for name in found_files:
            p = ROOT / name
            try:
                p.unlink()
                git('rm', '--cached', '--ignore-unmatch', name, check=False)
                print(f'     ✅ {name}')
            except OSError as e:
                print(f'     ⚠️  {name}: {e}')

        # حذف دایرکتوری‌ها
        import shutil
        for name in found_dirs:
            p = ROOT / name
            try:
                shutil.rmtree(p)
                git('rm', '-r', '--cached', '--ignore-unmatch', name, check=False)
                print(f'     ✅ {name}/')
            except OSError as e:
                print(f'     ⚠️  {name}/: {e}')

        # ── ۴. به‌روزرسانی gitignore ──
        gi = ROOT / '.gitignore'
        content = gi.read_text(encoding='utf-8') if gi.exists() else ''
        additions = [
            '# Temp analysis outputs',
            'apps-analysis.json',
            'clean_i18n_output/',
            'i18n_clean_output/',
            'i18n_report/',
            'orphaned_keys_*.txt',
            'master_*.json',
            'master_*.txt',
            'sync_report_*.json',
            '*_snapshot.json',
        ]
        missing = [a for a in additions if a not in content]
        if missing:
            with gi.open('a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(missing) + '\n')
            print(f'\n  ✅ .gitignore به‌روزرسانی شد ({len(missing)} الگو)')

        # ── ۵. خلاصه ──
        total = len(found_files) + len(found_dirs)
        print(f'\n{"═" * 60}')
        print(f'  ✅ {total} مورد حذف شد')
        print(f'\n  📋 commit:')
        print(f'     git add -A')
        print(f'     git commit -m "chore: remove temp scripts and analysis outputs"')
        print(f'     git push')
    else:
        print(f'\n  → {len(found_files) + len(found_dirs)} مورد آماده حذف')
        print(f'  → python cleanup_temp.py --apply')

    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())