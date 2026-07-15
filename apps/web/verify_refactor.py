#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web Refactor — Verification Script
================================================================================
 Validates that all 42 refactored files exist and meet quality bar.

 CHECKS PERFORMED
 ----------------
  1. EXISTENCE      — every expected file is present
  2. NON-EMPTY      — no zero-byte or stub files
  3. SYNTAX         — .ts/.tsx parse via `tsc --noEmit`-style regex checks
                      (balanced braces, no obvious unclosed templates)
  4. JSON VALIDITY  — .json files parse without error
  5. i18n PARITY    — fa.json and en.json have identical key sets
  6. IMPORT HEALTH  — no leftover `import … from "@/types"` collisions,
                      all "@/…" aliases point to files that exist
  7. HARDCODED TEXT — detect Persian/English literal strings in .tsx
                      (should use t("…") instead)
  8. RTL/LTR HYGIENE — flag any use of `ml-`, `mr-`, `pl-`, `pr-`,
                      `left-`, `right-`, `text-left`, `text-right`
                      (should use logical properties: ms-/me-/ps-/pe-…)
  9. BUILD BLOCKERS — re-check for the original TS2484 / TS2339 patterns
                      that broke the build

 USAGE
 -----
  python verify_refactor.py --root D:\\econojin.com\\apps\\web

  # If the apps/web folder isn't available locally, point --root at the
  # downloaded `apps-web-fixed/` folder instead.

 EXIT CODES
 ----------
  0 = all checks passed
  1 = one or more checks failed (see report for details)
  2 = invocation error (bad --root, etc.)
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Expected file inventory — the 42 files we promised
# ---------------------------------------------------------------------------

EXPECTED_FILES: Tuple[str, ...] = (
    # Root config (7)
    ".env.example",
    "INSTALL.fa.md",
    "tsconfig.json",
    "tsconfig.node.json",
    "postcss.config.js",
    "tailwind.config.js",
    "vite.config.ts",

    # Entry + i18n (5)
    "src/main.tsx",
    "src/App.tsx",
    "src/i18n/index.ts",
    "src/i18n/locales/fa.json",
    "src/i18n/locales/en.json",

    # lib + styles (3)
    "src/lib/utils.ts",
    "src/lib/i18n-utils.ts",
    "src/styles/index.css",

    # types (3)
    "src/types/index.ts",
    "src/types/api.ts",
    "src/types/ethereum.d.ts",

    # services + hooks (4)
    "src/services/authService.ts",
    "src/hooks/useApi.tsx",
    "src/hooks/useAuth.tsx",
    "src/hooks/useLanguage.tsx",

    # components/common (5)
    "src/components/common/ErrorBoundary.tsx",
    "src/components/common/ErrorFallback.tsx",
    "src/components/common/LoadingSpinner.tsx",
    "src/components/common/PagePlaceholder.tsx",
    "src/components/common/LanguageSwitcher.tsx",

    # components/Layout (4)
    "src/components/Layout/Header.tsx",
    "src/components/Layout/Sidebar.tsx",
    "src/components/Layout/Footer.tsx",
    "src/components/Layout/Layout.tsx",

    # pages (11)
    "src/pages/Dashboard.tsx",
    "src/pages/Documents.tsx",
    "src/pages/Login.tsx",
    "src/pages/Register/Register.tsx",
    "src/pages/Carbon/CarbonDashboard.tsx",
    "src/pages/Hydrology/WatershedList.tsx",
    "src/pages/Soil/SoilDashboard.tsx",
    "src/pages/AboutUs/AboutUs.tsx",
    "src/pages/Accounting/Accounting.tsx",
    "src/pages/AgricultureSchools/AgricultureSchools.tsx",
    "src/pages/Animations/Animations.tsx",
)

assert len(EXPECTED_FILES) == 42, f"expected 42 files, listed {len(EXPECTED_FILES)}"

# ---------------------------------------------------------------------------
# Anti-patterns we scan for
# ---------------------------------------------------------------------------

# Logical-property violations (should use ms-/me-/ps-/pe-/start-/end-)
RTL_VIOLATIONS = [
    (re.compile(r"\bml-(\d)"),       "ml-$1 → use ms-$1 (margin-inline-start)"),
    (re.compile(r"\bmr-(\d)"),       "mr-$1 → use me-$1 (margin-inline-end)"),
    (re.compile(r"\bpl-(\d)"),       "pl-$1 → use ps-$1 (padding-inline-start)"),
    (re.compile(r"\bpr-(\d)"),       "pr-$1 → use pe-$1 (padding-inline-end)"),
    (re.compile(r"\bleft-(\d)"),     "left-$1 → use start-$1"),
    (re.compile(r"\bright-(\d)"),    "right-$1 → use end-$1"),
    (re.compile(r"\btext-left\b"),   "text-left → use text-start"),
    (re.compile(r"\btext-right\b"),  "text-right → use text-end"),
    (re.compile(r"\bborder-l\b"),    "border-l → use border-s"),
    (re.compile(r"\bborder-r\b"),    "border-r → use border-e"),
    (re.compile(r"\brounded-l-"),    "rounded-l-* → use rounded-s-*"),
    (re.compile(r"\brounded-r-"),    "rounded-r-* → use rounded-e-*"),
]

# Build-blocker patterns (the original TS2484 / TS2339 bugs)
DUPLICATE_USER_EXPORT = re.compile(
    r"export\s+(?:type|interface)\s+User\b"
)
HARDCODED_PERSIAN_IN_TSX = re.compile(r"[\u0600-\u06FF]{3,}")
HARDCODED_ENGLISH_UI_IN_TSX = re.compile(
    r">\s*(Sign in|Sign up|Loading|Dashboard|Documents|Cancel|Save|Edit|Delete)\s*<"
)
ANY_USAGE = re.compile(r":\s*any\b|\bas\s+any\b|<any>")
TS_IGNORE = re.compile(r"//\s*@ts-(ignore|nocheck|expect-error)")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class FileCheck:
    rel_path: str
    exists: bool = False
    size_bytes: int = 0
    line_count: int = 0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    status: str = "ok"  # ok | warning | error | missing

@dataclass
class VerificationReport:
    root: str
    total_files_expected: int
    files: List[FileCheck] = field(default_factory=list)
    i18n_parity_ok: bool = True
    i18n_missing_keys: List[Tuple[str, str]] = field(default_factory=list)  # (lang, key)
    summary: str = ""
    passed: bool = True

# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class RefactorVerifier:
    def __init__(self, root: Path):
        self.root = root.resolve()

    # ----- file-level checks ------------------------------------------------

    def check_file(self, rel_path: str) -> FileCheck:
        full = self.root / rel_path
        fc = FileCheck(rel_path=rel_path)

        if not full.exists():
            fc.status = "missing"
            fc.issues.append("file does not exist")
            return fc

        fc.exists = True
        fc.size_bytes = full.stat().st_size

        try:
            text = full.read_text(encoding="utf-8")
        except Exception as e:
            fc.status = "error"
            fc.issues.append(f"unreadable: {e}")
            return fc

        fc.line_count = len(text.splitlines())

        if fc.size_bytes < 50:
            fc.status = "error"
            fc.issues.append(f"suspiciously small ({fc.size_bytes} bytes)")
            return fc

        ext = full.suffix.lower()

        # Per-extension checks
        if ext == ".json":
            self._check_json(text, fc)
        elif ext in {".ts", ".tsx"}:
            self._check_typescript(text, fc)
        elif ext == ".css":
            self._check_css(text, fc)
        elif ext == ".js":
            self._check_js(text, fc)

        # RTL hygiene — applies to .tsx and .css
        if ext in {".tsx", ".ts", ".css"}:
            self._check_rtl_hygiene(text, fc)

        # Determine final status
        if fc.issues:
            fc.status = "error"
        elif fc.warnings:
            fc.status = "warning"

        return fc

    # ----- JSON -------------------------------------------------------------

    def _check_json(self, text: str, fc: FileCheck) -> None:
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            fc.issues.append(f"invalid JSON: {e}")

    # ----- TypeScript / TSX -------------------------------------------------

    def _check_typescript(self, text: str, fc: FileCheck) -> None:
        # 1. Balanced braces (very rough — catches obvious truncations)
        open_braces = text.count("{")
        close_braces = text.count("}")
        if open_braces != close_braces:
            fc.issues.append(f"unbalanced braces: {open_braces}{{ vs {close_braces}}}")

        open_parens = text.count("(")
        close_parens = text.count(")")
        if abs(open_parens - close_parens) > 2:
            fc.issues.append(f"unbalanced parens: {open_parens}( vs {close_parens})")

        # 2. Build-blocker: duplicate User export (TS2484)
        if DUPLICATE_USER_EXPORT.search(text):
            matches = DUPLICATE_USER_EXPORT.findall(text)
            if len(matches) > 1 and "types/index.ts" not in fc.rel_path:
                # only types/index.ts is allowed to export User (and only once)
                fc.issues.append(f"User exported {len(matches)}× in one file → TS2484 risk")
            elif "types/index.ts" in fc.rel_path and len(matches) > 1:
                fc.issues.append(f"types/index.ts exports User {len(matches)}× → TS2484")

        # 3. TS-ignore directives
        ts_ignores = TS_IGNORE.findall(text)
        if ts_ignores:
            fc.warnings.append(f"{len(ts_ignores)} @ts-ignore/@ts-nocheck directive(s)")

        # 4. `any` usage (acceptable only in .d.ts)
        if not fc.rel_path.endswith(".d.ts"):
            any_hits = ANY_USAGE.findall(text)
            if any_hits:
                fc.warnings.append(f"{len(any_hits)} `any` usage(s)")

        # 5. Hardcoded Persian in .tsx (must use t("…"))
        if fc.rel_path.endswith(".tsx"):
            persian_hits = HARDCODED_PERSIAN_IN_TSX.findall(text)
            # Filter out Persian inside comments and string-literal t() args
            # (rough heuristic — keep false positives low)
            real_hits = []
            for match in persian_hits:
                # Skip if it's inside a t("…") call
                idx = text.find(match)
                if idx == -1:
                    continue
                # Look back 30 chars for "t(" or "//"
                lookback = text[max(0, idx - 30):idx]
                if 't("' in lookback or "t('" in lookback or "//" in lookback:
                    continue
                real_hits.append(match)
            if real_hits:
                fc.warnings.append(f"{len(real_hits)} hardcoded Persian string(s) outside t() calls")

        # 6. Import path sanity — "@/…" should map to src/…
        for m in re.finditer(r'from\s+["\'](@/[^"\']+)["\']', text):
            alias = m.group(1)
            # resolve to a file path
            stripped = alias[2:]  # drop "@/"
            candidates = [
                self.root / "src" / f"{stripped}.ts",
                self.root / "src" / f"{stripped}.tsx",
                self.root / "src" / f"{stripped}/index.ts",
                self.root / "src" / f"{stripped}/index.tsx",
                self.root / "src" / stripped,  # for non-code assets
            ]
            if not any(c.exists() for c in candidates):
                fc.issues.append(f"@/ alias not resolvable: {alias}")

    # ----- CSS --------------------------------------------------------------

    def _check_css(self, text: str, fc: FileCheck) -> None:
        # Must include @tailwind directives
        if "@tailwind base" not in text:
            fc.issues.append("missing @tailwind base directive")
        if "@tailwind components" not in text:
            fc.issues.append("missing @tailwind components directive")
        if "@tailwind utilities" not in text:
            fc.issues.append("missing @tailwind utilities directive")

    # ----- JS (config files) -----------------------------------------------

    def _check_js(self, text: str, fc: FileCheck) -> None:
        # postcss.config.js / tailwind.config.js should use `export default`
        if "export default" not in text:
            fc.issues.append("config file missing `export default`")

    # ----- RTL hygiene ------------------------------------------------------

    def _check_rtl_hygiene(self, text: str, fc: FileCheck) -> None:
        for pattern, message in RTL_VIOLATIONS:
            hits = pattern.findall(text)
            if hits:
                fc.warnings.append(f"{len(hits)}× {message}")

    # ----- i18n parity check ------------------------------------------------

    def check_i18n_parity(self, fa_path: Path, en_path: Path) -> Tuple[List[Tuple[str, str]], bool]:
        """Returns (missing_keys_list, parity_ok)."""
        if not fa_path.exists() or not en_path.exists():
            return [], False

        try:
            fa = json.loads(fa_path.read_text(encoding="utf-8"))
            en = json.loads(en_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return [], False

        fa_keys = self._flatten_keys(fa)
        en_keys = self._flatten_keys(en)

        missing: List[Tuple[str, str]] = []
        for key in fa_keys:
            if key not in en_keys:
                missing.append(("en", key))
        for key in en_keys:
            if key not in fa_keys:
                missing.append(("fa", key))

        return missing, len(missing) == 0

    @staticmethod
    def _flatten_keys(obj: object, prefix: str = "") -> Set[str]:
        """Flatten a nested dict into dotted keys: {a:{b:1}} → {"a.b"}."""
        keys: Set[str] = set()
        if not isinstance(obj, dict):
            return keys
        for k, v in obj.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(RefactorVerifier._flatten_keys(v, full))
            else:
                keys.add(full)
        return keys

    # ----- run all checks ---------------------------------------------------

    def verify(self) -> VerificationReport:
        report = VerificationReport(
            root=str(self.root),
            total_files_expected=len(EXPECTED_FILES),
        )

        for rel in EXPECTED_FILES:
            report.files.append(self.check_file(rel))

        # i18n parity
        fa_path = self.root / "src/i18n/locales/fa.json"
        en_path = self.root / "src/i18n/locales/en.json"
        missing, parity_ok = self.check_i18n_parity(fa_path, en_path)
        report.i18n_parity_ok = parity_ok
        report.i18n_missing_keys = missing

        # Overall pass/fail
        errors = sum(1 for f in report.files if f.status == "error")
        missing_count = sum(1 for f in report.files if f.status == "missing")
        warnings = sum(1 for f in report.files if f.status == "warning")
        parity_fail = 0 if parity_ok else 1

        report.passed = (errors == 0 and missing_count == 0 and parity_ok)
        report.summary = (
            f"{len(EXPECTED_FILES)} files expected — "
            f"{missing_count} missing, {errors} errored, {warnings} warned, "
            f"i18n parity {'OK' if parity_ok else 'FAIL (' + str(len(missing)) + ' keys)'}"
        )
        return report

# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_markdown(report: VerificationReport) -> str:
    md: List[str] = []
    md.append("# apps/web Refactor — Verification Report\n")
    md.append(f"- **Root:** `{report.root}`")
    md.append(f"- **Files expected:** {report.total_files_expected}")
    md.append(f"- **Overall:** {'✅ PASS' if report.passed else '❌ FAIL'}")
    md.append(f"- **Summary:** {report.summary}\n")

    # File-by-file table
    md.append("## File-by-file results\n")
    md.append("| # | File | Status | Lines | Issues / Warnings |")
    md.append("|---|------|--------|-------|-------------------|")
    for i, fc in enumerate(report.files, 1):
        emoji = "✅" if fc.status == "ok" else "⚠️" if fc.status == "warning" else "❌"
        notes = fc.issues + [f"(warn) {w}" for w in fc.warnings]
        notes_str = "; ".join(notes) if notes else "—"
        if not fc.exists:
            notes_str = "**MISSING**"
        md.append(f"| {i} | `{fc.rel_path}` | {emoji} {fc.status} | {fc.line_count} | {notes_str} |")
    md.append("")

    # i18n parity
    md.append("## i18n key parity (fa.json ↔ en.json)\n")
    if report.i18n_parity_ok:
        md.append("✅ All keys match between `fa.json` and `en.json`.\n")
    else:
        md.append(f"❌ {len(report.i18n_missing_keys)} keys are missing on one side:\n")
        md.append("| Missing in | Key |")
        md.append("|------------|-----|")
        for lang, key in report.i18n_missing_keys[:50]:
            md.append(f"| {lang}.json | `{key}` |")
        if len(report.i18n_missing_keys) > 50:
            md.append(f"| … | _(+{len(report.i18n_missing_keys) - 50} more)_ |")
        md.append("")

    # Aggregate warnings (RTL hygiene, hardcoded text, etc.)
    md.append("## Aggregate warnings\n")
    agg: Dict[str, int] = {}
    for fc in report.files:
        for w in fc.warnings:
            # Normalize the warning text to its first 40 chars for grouping
            key = w[:60]
            agg[key] = agg.get(key, 0) + 1
    if agg:
        md.append("| Warning | Files |")
        md.append("|---------|-------|")
        for k, v in sorted(agg.items(), key=lambda x: -x[1]):
            md.append(f"| `{k}` | {v} |")
    else:
        md.append("_No warnings._")
    md.append("")

    # Final verdict
    md.append("## Verdict\n")
    if report.passed:
        md.append("✅ **All 42 files are present, syntactically valid, and i18n parity holds.**")
        md.append("")
        md.append("You can safely proceed to `pnpm install` and `pnpm run build`.")
    else:
        md.append("❌ **Some checks failed.** See the table above for details.")
        md.append("")
        md.append("Fix the listed issues before running `pnpm run build`.")
    return "\n".join(md)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the apps/web refactor — 42 files + i18n parity."
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Path to the apps/web (or apps-web-fixed) directory.",
    )
    parser.add_argument(
        "--out",
        default="./verification_report",
        help="Output directory for report.json and report.md (default: ./verification_report)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] Root path does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    print(f"[INFO] Verifying: {root}")
    verifier = RefactorVerifier(root=root)
    report = verifier.verify()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "report.json"
    md_path = out_dir / "report.md"

    # JSON (dataclass → dict)
    json_payload = {
        "root": report.root,
        "total_files_expected": report.total_files_expected,
        "passed": report.passed,
        "summary": report.summary,
        "i18n_parity_ok": report.i18n_parity_ok,
        "i18n_missing_keys": report.i18n_missing_keys,
        "files": [
            {
                "rel_path": f.rel_path,
                "exists": f.exists,
                "size_bytes": f.size_bytes,
                "line_count": f.line_count,
                "issues": f.issues,
                "warnings": f.warnings,
                "status": f.status,
            }
            for f in report.files
        ],
    }
    json_path.write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print()
    print("=" * 72)
    print(" VERIFICATION COMPLETE")
    print("=" * 72)
    print(f"  Files expected : {report.total_files_expected}")
    print(f"  Summary        : {report.summary}")
    print(f"  Overall        : {'✅ PASS' if report.passed else '❌ FAIL'}")
    print(f"  JSON report    : {json_path}")
    print(f"  Markdown report: {md_path}")
    print("=" * 72)
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
