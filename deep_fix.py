from pathlib import Path
import re

print("=" * 80)
print("🔧 DEEP FIX - Comprehensive Frontend Repair")
print("=" * 80)

frontend_path = Path('apps/web')

# Fix 1: Ensure all critical imports exist
print("\n1️⃣  Checking critical imports...")

critical_files = {
    'src/lib/api.ts': '''// Econojin API Client
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error(`API call failed: ${path}`, error);
    throw error;
  }
}
''',
    'src/lib/types.ts': '''// Econojin Type Definitions
export interface User {
  id: string;
  email: string;
  name: string;
}

export interface ApiError {
  message: string;
  code: string;
}
''',
}

for path, content in critical_files.items():
    file_path = frontend_path / path
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        print(f"   ✅ Created {path}")
    else:
        print(f"   ✅ {path} exists")

# Fix 2: Add console.log cleanup
print("\n2️⃣  Checking for debug console.logs...")
console_count = 0

for ts_file in frontend_path.rglob('*.ts'):
    if 'node_modules' in str(ts_file) or '.next' in str(ts_file):
        continue
    
    try:
        content = ts_file.read_text(encoding='utf-8')
        if 'console.log' in content:
            console_count += 1
    except:
        pass

print(f"   🔍 Found {console_count} files with console.log")

# Fix 3: Check package.json dependencies
print("\n3️⃣  Checking package.json...")
package_json = frontend_path / 'package.json'
if package_json.exists():
    import json
    pkg = json.loads(package_json.read_text(encoding='utf-8'))
    
    deps = pkg.get('dependencies', {})
    dev_deps = pkg.get('devDependencies', {})
    
    required = ['@tanstack/react-query', 'axios', 'react', 'next']
    missing = []
    
    for dep in required:
        if dep not in deps and dep not in dev_deps:
            missing.append(dep)
    
    if missing:
        print(f"   ⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"   💡 Run: pnpm add {' '.join(missing)}")
    else:
        print("   ✅ All critical dependencies installed")

# Fix 4: Verify layout.tsx one more time
print("\n4️⃣  Final layout.tsx check...")
layout_path = frontend_path / 'src/app/layout.tsx'
if layout_path.exists():
    content = layout_path.read_text(encoding='utf-8')
    
    checks = {
        'has Vazirmatn': 'Vazirmatn' in content,
        'has Inter': 'Inter' in content,
        'has Providers': 'Providers' in content,
        'has html tag': '<html' in content,
        'has body tag': '<body' in content,
        'no broken backticks': r'className={\ ' not in content,
    }
    
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
        if not result:
            all_good = False
    
    if all_good:
        print("   ✅ layout.tsx is ready!")
    else:
        print("   ⚠️  layout.tsx needs manual review")

print("\n" + "=" * 80)
print("✅ DEEP FIX COMPLETE")
print("=" * 80)
print("\n🚀 Now run: npx next dev -p 3001")