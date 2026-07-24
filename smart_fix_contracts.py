import re
from pathlib import Path

def find_and_fix_contracts(root_dir):
    root = Path(root_dir)
    
    # جستجوی بازگشتی برای تمام فایل‌های .sol در کل پروژه
    sol_files = list(root.rglob("*.sol"))
    
    # فیلتر کردن فایل‌های هدف
    target_files = [f for f in sol_files if f.name in ["EcoCoin.sol", "VerificationOracle.sol"]]
    
    if not target_files:
        print("❌ فایل‌های EcoCoin.sol یا VerificationOracle.sol در پروژه یافت نشدند.")
        print("💡 راهنما: لطفاً در PowerShell دستور زیر را اجرا کنید تا مسیر دقیق آن‌ها را پیدا کنیم:")
        print("   Get-ChildItem -Path D:\\econojin.com -Recurse -Filter *.sol -Name")
        return

    print(f"✅ تعداد {len(target_files)} فایل قرارداد هوشمند هدف یافت شد.\n")

    for file_path in target_files:
        print(f"🔍 در حال بررسی: {file_path}")
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            if file_path.name == "EcoCoin.sol":
                # اصلاح تابع mint: افزودن onlyOracle
                content = re.sub(
                    r'(function\s+mint\s*\([^)]*\)\s+public)',
                    r'\1 onlyOracle',
                    content
                )
                # اصلاح تابع setOracle: افزودن onlySteward
                content = re.sub(
                    r'(function\s+setOracle\s*\([^)]*\)\s+public)',
                    r'\1 onlySteward',
                    content
                )

            elif file_path.name == "VerificationOracle.sol":
                # اصلاح تابع registerProject: افزودن onlySteward
                content = re.sub(
                    r'(function\s+registerProject\s*\([^)]*\)\s+public)',
                    r'\1 onlySteward',
                    content
                )
                # اصلاح تابع addVerifier: افزودن onlySteward
                content = re.sub(
                    r'(function\s+addVerifier\s*\([^)]*\)\s+public)',
                    r'\1 onlySteward',
                    content
                )
                # اصلاح تابع removeVerifier: افزودن onlySteward
                content = re.sub(
                    r'(function\s+removeVerifier\s*\([^)]*\)\s+public)',
                    r'\1 onlySteward',
                    content
                )

            # ذخیره تغییرات در صورت وجود تغییر
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                print(f"   ✅ اصلاحات امنیتی با موفقیت روی {file_path.name} اعمال شد.")
            else:
                print(f"   ℹ️ فایل {file_path.name} از قبل اصلاح شده یا الگوی توابع public بدون modifier را نداشت.")
                
        except Exception as e:
            print(f"   ❌ خطا در خواندن/نوشتن فایل {file_path}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("  🛡️ شروع جستجو و اصلاح‌گر امنیتی هوشمند")
    print("=" * 60)
    find_and_fix_contracts("D:\\econojin.com")
    print("=" * 60)
    print("  ✅ عملیات به پایان رسید.")
    print("=" * 60)