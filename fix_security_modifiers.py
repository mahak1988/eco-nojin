import os
import re

# لیست فایل‌های هدف
TARGET_FILES = [
    "contracts/EcoCoin.sol",
    "contracts/VerificationOracle.sol"
]

# نگاشت هوشمند توابع به مودیفایرهای مناسب
# توجه: توابعی مثل stake, unstake, burn کاربردی هستند و باید public بمانند.
# این اسکریپت فقط توابع مدیریتی و حساس را هدف قرار می‌دهد.
MODIFIER_MAP = {
    "mint": "onlyOracle",
    "setoracle": "onlySteward",
    "registerproject": "onlySteward",
    "verify": "onlyVerifier",  # یا onlyOracle بسته به طراحی قرارداد
    "addverifier": "onlySteward",
    "removeverifier": "onlySteward"
}

def fix_solidity_file(filepath):
    if not os.path.exists(filepath):
        print(f"⚠️ فایل یافت نشد: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    changes_made = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = line[:len(line) - len(line.lstrip())]
        new_line = line

        # ۱. علامت‌گذاری توابع read-only (view/pure)
        if re.search(r'\bfunction\s+\w+\s*\([^)]*\)\s+(?:public|external)\s+(?:view|pure)\b', stripped, re.IGNORECASE):
            if '// safe: read-only' not in stripped:
                new_lines.append(f"{indent}// safe: read-only\n")
                changes_made += 1

        # ۲. بررسی توابع state-changing برای افزودن مودیفایر
        func_match = re.search(r'\bfunction\s+(\w+)\s*\([^)]*\)\s+(public|external)\b', stripped, re.IGNORECASE)
        
        if func_match:
            func_name = func_match.group(1).lower()
            
            # بررسی اینکه آیا قبلاً مودیفایر دسترسی دارد یا خیر
            has_modifier = any(mod in stripped for mod in ['onlySteward', 'onlyOracle', 'onlyVerifier', 'onlyOwner'])
            
            if not has_modifier and func_name in MODIFIER_MAP:
                modifier = MODIFIER_MAP[func_name]
                
                # درج مودیفایر قبل از { یا ;
                if '{' in stripped:
                    new_line = stripped.replace('{', f' {modifier} {{')
                elif ';' in stripped:
                    new_line = stripped.replace(';', f' {modifier};')
                else:
                    new_line = f"{stripped} {modifier}"
                
                new_lines.append(f"{indent}{new_line}\n")
                print(f"  [+] افزودن '{modifier}' به تابع '{func_name}' در {os.path.basename(filepath)}")
                changes_made += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if changes_made > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  ✅ فایل {os.path.basename(filepath)} با موفقیت به‌روزرسانی شد ({changes_made} تغییر).")
        return True
    else:
        print(f"  · فایل {os.path.basename(filepath)} از قبل اصلاح شده یا تغییری نیاز نداشت.")
        return False

def main():
    print("=" * 60)
    print("  🛡️ شروع اصلاح‌گر امنیتی هوشمند قراردادهای هوشمند")
    print("=" * 60)
    
    total_changes = 0
    for filepath in TARGET_FILES:
        if fix_solidity_file(filepath):
            total_changes += 1
            
    print("=" * 60)
    if total_changes > 0:
        print("  ✅ عملیات با موفقیت به پایان رسید. لطفاً فایل‌ها را بازبینی کنید.")
    else:
        print("  · هیچ تغییری اعمال نشد (فایل‌ها از قبل ایمن هستند).")
    print("=" * 60)

if __name__ == "__main__":
    main()