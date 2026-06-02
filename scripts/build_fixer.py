# ... (بخش‌های اولیه بیلدر بدون تغییر) ...

# ✅ افزودن فاز امنیتی Phase 1 Security Hardening به بیلدر
PHASE_SECURITY_TPAF = '''
def phase_run_security_scan():
    R.section("Phase 0: Run TPAF Security Scan (Shift-Left)")
    security_script = ROOT / "phase1_security_v1.0.3.py"
    if not security_script.exists():
        R.warn("phase1_security_v1.0.3.py not found, skipping automated scan")
        R.info("Download from: https://github.com/your-org/security-tools")
        return True  # Non-blocking
    R.info("Running security pipeline...")
    try:
        result = subprocess.run(
            [sys.executable, str(security_script), "--root", str(ROOT), "--allow-warnings"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        # پارس گزارش JSON
        report_path = ROOT / "phase1_security_report.json"
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            score = report.get("overall_score", 0)
            status = report.get("status", "UNKNOWN")
            print(NL + "  Security Score: " + C.BOLD + str(score) + C.RESET + " | Status: " + C.BOLD + status + C.RESET)
            if status == "PASS":
                R.ok("Security scan passed (score >= 0.8)")
                return True
            elif status == "WARN":
                R.warn("Security warnings found - review report")
                return True  # Non-blocking for development
            else:
                R.err("Security scan failed - fix CRITICAL findings first")
                return False  # Blocking for production
        else:
            R.warn("Security report not generated")
            return True
    except subprocess.TimeoutExpired:
        R.err("Security scan timeout")
        return False
    except Exception as e:
        R.err("Security scan error: " + str(e))
        return False
'''

# ... (در بخش MAIN_FUNC، افزودن فاز امنیتی به ابتدای results) ...

MAIN_FUNC = '''
def main():
    print(C.BOLD + C.CYAN)
    print("=" * 62)
    print("  ECONOJIN FINAL FIXER - Security & Test Automation")
    print("=" * 62)
    print(C.RESET)
    start_time = time.time()
    results = {
        "security": phase_run_security_scan(),  # ✅ فاز امنیتی اولویت اول
        "init": phase_init(),
        "syntax": phase_fix_connect_postgres(),
        "subprocess": phase_fix_subprocess(),
        "secrets": phase_fix_hardcoded_secrets(),
        "warnings": phase_fix_syntax_warnings(),
        "openzeppelin": phase_install_openzeppelin(),
        "git": phase_setup_git(),
        "tests": phase_run_tests(),
        "guardian": phase_run_guardian(),
    }
    # ... (بقیه کد گزارش‌دهی بدون تغییر) ...
'''

# ✅ در بخش نهایی بیلدر، افزودن فاز جدید به لیست L:
L.append(PHASE_SECURITY_TPAF)  # قبل از PHASE_INIT
# و جایگزینی MAIN_FUNC با نسخه به‌روزشده بالا