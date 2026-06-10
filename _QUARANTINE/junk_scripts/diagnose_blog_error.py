"""
🔍 Diagnose and Fix admin/blog/page.tsx Syntax Error
"""
from pathlib import Path

print("=" * 100)
print("DIAGNOSING admin/blog/page.tsx")
print("=" * 100)

blog_page = Path('apps/web/src/app/admin/blog/page.tsx')

if not blog_page.exists():
    print("❌ File not found!")
    exit(1)

content = blog_page.read_text(encoding='utf-8')
lines = content.split('\n')

print(f"\n📄 Total lines: {len(lines)}")

# Show lines 95-115 to see the problem
print("\n🔍 Lines 95-115 (around error):")
print("-" * 100)
for i in range(94, min(115, len(lines))):
    line_num = i + 1
    marker = ">>>" if 103 <= i <= 107 else "   "
    print(f"{marker} {line_num:4}: {lines[i]}")

# Analyze brace balance
print("\n📊 Brace Analysis:")
brace_count = 0
for i, line in enumerate(lines[:110], 1):
    # Count braces (rough - ignores strings)
    open_braces = line.count('{')
    close_braces = line.count('}')
    brace_count += open_braces - close_braces
    
    if i >= 95 and i <= 110:
        print(f"   Line {i:3}: braces={open_braces - close_braces:+2d}, total={brace_count:+3d} | {line[:60]}")

print(f"\n   Final brace count at line 110: {brace_count}")
print(f"   Expected: 0 (balanced)")

# Find the problem
if brace_count < 0:
    print("\n❌ PROBLEM: Too many closing braces!")
    print("   The component function closed too early.")
    
    # Find where it went negative
    running_count = 0
    for i, line in enumerate(lines[:110], 1):
        running_count += line.count('{') - line.count('}')
        if running_count < 0:
            print(f"\n   First negative at line {i}: {line.strip()}")
            break

elif brace_count > 0:
    print("\n⚠️  WARNING: Unclosed braces")
else:
    print("\n✅ Braces are balanced")

# Check for common issues
print("\n🔎 Checking for common issues:")

# Issue 1: "use client" at top
if not content.strip().startswith('"use client"') and not content.strip().startswith("'use client'"):
    print("   ⚠️  Missing 'use client' at top")

# Issue 2: export default
if 'export default function' not in content:
    print("   ⚠️  Missing 'export default function'")

# Issue 3: Find all "};" lines
print("\n📍 Lines with '};':")
for i, line in enumerate(lines[:110], 1):
    if line.strip() == '};':
        print(f"   Line {i:3}: {line}")

# Issue 4: Find "return (" lines
print("\n📍 Lines with 'return (':")
for i, line in enumerate(lines[:110], 1):
    if 'return (' in line:
        print(f"   Line {i:3}: {line}")

print("\n" + "=" * 100)
print("DIAGNOSIS COMPLETE")
print("=" * 100)