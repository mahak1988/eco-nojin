"""
🔧 تشخیص و رفع مشکل اتصال صفحات آکادمی
"""
from pathlib import Path
import re

print("=" * 80)
print("🔧 DIAGNOSING ACADEMY PAGES CONNECTION ISSUE")
print("=" * 80)

frontend_path = Path('apps/web/src')

# ============================================================
# 1. CHECK NAVBAR LINKS
# ============================================================
print("\n1️⃣  Checking Navbar links...")

navbar_paths = [
    frontend_path / 'components/layout/Navbar.tsx',
    frontend_path / 'components/layout/navbar.tsx',
    frontend_path / 'components/Navbar.tsx',
    frontend_path / 'app/Navbar.tsx',
]

navbar_found = False
for nav_path in navbar_paths:
    if nav_path.exists():
        navbar_found = True
        content = nav_path.read_text(encoding='utf-8')
        
        print(f"   ✅ Found: {nav_path.relative_to(frontend_path)}")
        
        # Check for academy link
        if '/academy' in content:
            print(f"   ✅ Academy link present")
            
            # Extract the link
            links = re.findall(r'href=["\'](/academy[^"\']*)["\']', content)
            if links:
                print(f"   🔗 Links found: {links}")
        else:
            print(f"   ❌ Academy link NOT found")
            print(f"   💡 Adding academy link...")
            
            # Add academy link
            if 'href=' in content:
                # Find a good place to insert
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'href="/' in line and 'academy' not in line:
                        # Insert academy link before this
                        indent = len(line) - len(line.lstrip())
                        academy_link = ' ' * indent + '<Link href="/academy" className="text-slate-300 hover:text-emerald-400 transition-colors">آکادمی</Link>'
                        lines.insert(i, academy_link)
                        content = '\n'.join(lines)
                        nav_path.write_text(content, encoding='utf-8')
                        print(f"   ✅ Added academy link")
                        break
        break

if not navbar_found:
    print("   ❌ Navbar not found")

# ============================================================
# 2. CHECK LAYOUT FILE
# ============================================================
print("\n2️⃣  Checking layout.tsx...")

layout_path = frontend_path / 'app/layout.tsx'
if layout_path.exists():
    content = layout_path.read_text(encoding='utf-8')
    
    # Check if Navbar is included
    if 'Navbar' in content or 'navbar' in content:
        print("   ✅ Navbar included in layout")
    else:
        print("   ⚠️  Navbar not included in layout")
    
    # Check for Providers
    if 'Providers' in content:
        print("   ✅ QueryClient Provider included")
    else:
        print("   ⚠️  QueryClient Provider missing")
else:
    print("   ❌ layout.tsx not found")

# ============================================================
# 3. CHECK API ENDPOINTS
# ============================================================
print("\n3️⃣  Checking API endpoints...")

# Check if backend router exists
router_path = Path('api/modules/academy/router.py')
if router_path.exists():
    content = router_path.read_text(encoding='utf-8-sig')
    
    endpoints = ['statistics', 'courses', 'categories', 'standards']
    for endpoint in endpoints:
        if f'/{endpoint}' in content:
            print(f"   ✅ /api/v1/academy/{endpoint}")
        else:
            print(f"   ❌ /api/v1/academy/{endpoint} MISSING")
    
    # Check if router is registered
    main_path = Path('api/main.py')
    if main_path.exists():
        main_content = main_path.read_text(encoding='utf-8-sig')
        if 'academy_router' in main_content:
            print("   ✅ Router registered in main.py")
        else:
            print("   ❌ Router NOT registered in main.py")
else:
    print("   ❌ Router file not found")

# ============================================================
# 4. CHECK PAGE IMPORTS
# ============================================================
print("\n4️⃣  Checking page imports...")

page_path = frontend_path / 'app/academy/page.tsx'
if page_path.exists():
    content = page_path.read_text(encoding='utf-8')
    
    # Check for required imports
    required = [
        'useAcademyStats',
        'useCourses',
        'useCategories',
        "from '@/hooks/academy/useAcademy'"
    ]
    
    missing = []
    for imp in required:
        if imp not in content:
            missing.append(imp)
    
    if missing:
        print(f"   ❌ Missing imports: {missing}")
    else:
        print("   ✅ All required imports present")
    
    # Check for export default
    if 'export default function' in content:
        print("   ✅ Default export present")
    else:
        print("   ❌ Default export missing")
else:
    print("   ❌ Academy page not found")

# ============================================================
# 5. CHECK HOOKS
# ============================================================
print("\n5️⃣  Checking hooks...")

hooks_path = frontend_path / 'hooks/academy/useAcademy.ts'
if hooks_path.exists():
    content = hooks_path.read_text(encoding='utf-8')
    
    hooks = ['useAcademyStats', 'useCourses', 'useCategories']
    missing = [h for h in hooks if h not in content]
    
    if missing:
        print(f"   ❌ Missing hooks: {missing}")
    else:
        print("   ✅ All hooks present")
    
    # Check for React Query
    if 'useQuery' in content:
        print("   ✅ React Query used")
    else:
        print("   ⚠️  React Query not used")
else:
    print("   ❌ Hooks file not found")

# ============================================================
# 6. CHECK API CLIENT
# ============================================================
print("\n6️⃣  Checking API client...")

api_path = frontend_path / 'lib/academy/api.ts'
if api_path.exists():
    content = api_path.read_text(encoding='utf-8')
    
    methods = ['getStats', 'getCourses', 'getCategories']
    missing = [m for m in methods if m not in content]
    
    if missing:
        print(f"   ❌ Missing methods: {missing}")
    else:
        print("   ✅ All API methods present")
    
    # Check for base API import
    if "from '@/lib/api-client'" in content or 'import api' in content:
        print("   ✅ Base API client imported")
    else:
        print("   ⚠️  Base API client not imported")
else:
    print("   ❌ API client not found")

# ============================================================
# 7. TEST INSTRUCTIONS
# ============================================================
print("\n" + "=" * 80)
print("🧪 MANUAL TEST INSTRUCTIONS")
print("=" * 80)

print("""
📋 Please follow these steps to test:

1. RESTART BACKEND:
   cd D:\\econojin.com
   uvicorn api.main:app --reload --port 8000

2. TEST API ENDPOINTS (in browser or curl):
   - http://localhost:8000/api/v1/academy/statistics
   - http://localhost:8000/api/v1/academy/courses
   - http://localhost:8000/api/v1/academy/categories
   - http://localhost:8000/api/v1/academy/standards

3. RESTART FRONTEND:
   cd D:\\econojin.com\\apps\\web
   Remove-Item -Recurse -Force .next
   npx next dev -p 3001

4. TEST PAGES (in browser):
   - http://localhost:3001/academy
   - http://localhost:3001/academy/courses/1
   - http://localhost:3001/academy/my-courses
   - http://localhost:3001/academy/certificates
   - http://localhost:3001/academy/guide

5. CHECK BROWSER CONSOLE:
   - Press F12
   - Go to Console tab
   - Look for errors (red text)
   - Go to Network tab
   - Check if API calls are successful (200 OK)

6. CHECK NAVBAR:
   - Is "آکادمی" link visible?
   - Does clicking it go to /academy?
""")

# ============================================================
# 8. COMMON ISSUES
# ============================================================
print("\n" + "=" * 80)
print("⚠️  COMMON ISSUES & SOLUTIONS")
print("=" * 80)

print("""
❌ Issue: Pages show 404
   ✅ Solution: Clear .next folder and restart

❌ Issue: Data not loading
   ✅ Solution: Check if backend is running on port 8000

❌ Issue: Navbar link not working
   ✅ Solution: Check if Navbar.tsx has <Link href="/academy">

❌ Issue: API calls failing
   ✅ Solution: Check browser Network tab for error details

❌ Issue: Styles not loading
   ✅ Solution: Hard refresh (Ctrl+Shift+R)

❌ Issue: TypeScript errors
   ✅ Solution: Run: pnpm exec tsc --noEmit
""")

print("\n" + "=" * 80)
print("✅ DIAGNOSIS COMPLETE")
print("=" * 80)