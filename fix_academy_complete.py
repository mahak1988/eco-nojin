"""
🔧 بررسی و رفع کامل اتصال صفحات آکادمی
"""
from pathlib import Path
import re

print("=" * 80)
print("🔧 COMPREHENSIVE ACADEMY CONNECTION FIX")
print("=" * 80)

frontend_path = Path('apps/web/src')
backend_path = Path('api')

# ============================================================
# 1. FIX REMAINING 'any' TYPE IN PAGE.TSX
# ============================================================
print("\n1️⃣  Fixing remaining 'any' type in academy page...")

page_path = frontend_path / 'app/academy/page.tsx'
if page_path.exists():
    content = page_path.read_text(encoding='utf-8')
    
    # Fix the remaining 'any' in filteredCourses
    if 'filteredCourses?.map((course: any)' in content:
        content = content.replace(
            'filteredCourses?.map((course: any)',
            'filteredCourses?.map((course: Course)'
        )
        page_path.write_text(content, encoding='utf-8')
        print("   ✅ Fixed 'any' type in filteredCourses")
    
    # Verify no 'any' remains
    any_count = content.count(': any') + content.count('as any')
    if any_count == 0:
        print("   ✅ No 'any' types remaining")
    else:
        print(f"   ⚠️  Still {any_count} 'any' types")

# ============================================================
# 2. CHECK NAVBAR LINK
# ============================================================
print("\n2️⃣  Checking Navbar for academy link...")

navbar_paths = [
    frontend_path / 'components/layout/Navbar.tsx',
    frontend_path / 'components/layout/navbar.tsx',
    frontend_path / 'components/Navbar.tsx',
    frontend_path / 'app/Navbar.tsx',
]

navbar_found = False
navbar_updated = False

for nav_path in navbar_paths:
    if nav_path.exists():
        navbar_found = True
        content = nav_path.read_text(encoding='utf-8')
        
        if '/academy' in content:
            print(f"   ✅ Academy link found in {nav_path.relative_to(frontend_path)}")
        else:
            print(f"   ⚠️  Academy link NOT in {nav_path.relative_to(frontend_path)}")
            print("   💡 Adding academy link...")
            
            # Try to add academy link
            if 'GraduationCap' not in content and 'BookOpen' not in content:
                # Add import
                if "from 'lucide-react'" in content:
                    content = re.sub(
                        r"from 'lucide-react'",
                        "GraduationCap, \n} from 'lucide-react'",
                        content
                    )
            
            # Add link in navigation items
            if 'href=' in content:
                # Find a good place to add the link
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'href="/gis"' in line or 'href="/dashboard"' in line:
                        # Add academy link after this
                        indent = len(line) - len(line.lstrip())
                        academy_link = ' ' * indent + '<Link href="/academy" className="...">آکادمی</Link>'
                        lines.insert(i + 1, academy_link)
                        content = '\n'.join(lines)
                        nav_path.write_text(content, encoding='utf-8')
                        navbar_updated = True
                        print(f"   ✅ Added academy link to navbar")
                        break
        break

if not navbar_found:
    print("   ❌ Navbar not found in common locations")
    print("   💡 Please check manually")

# ============================================================
# 3. VERIFY ALL PAGE FILES
# ============================================================
print("\n3️⃣  Verifying all academy page files...")

pages = {
    'main': 'app/academy/page.tsx',
    'course_detail': 'app/academy/courses/[id]/page.tsx',
    'lesson': 'app/academy/courses/[id]/lessons/[lessonId]/page.tsx',
    'create': 'app/academy/create/page.tsx',
    'my_courses': 'app/academy/my-courses/page.tsx',
    'certificates': 'app/academy/certificates/page.tsx',
    'guide': 'app/academy/guide/page.tsx',
}

all_pages_ok = True
for name, path in pages.items():
    full_path = frontend_path / path
    if full_path.exists():
        size = full_path.stat().st_size
        content = full_path.read_text(encoding='utf-8')
        
        # Check if file has content
        if size < 1000:
            print(f"   ⚠️  {name}: File too small ({size} bytes)")
            all_pages_ok = False
        elif 'export default' not in content and 'export function' not in content:
            print(f"   ⚠️  {name}: No default export found")
            all_pages_ok = False
        else:
            print(f"   ✅ {name}: OK ({size:,} bytes)")
    else:
        print(f"   ❌ {name}: MISSING")
        all_pages_ok = False

# ============================================================
# 4. VERIFY API CLIENT
# ============================================================
print("\n4️⃣  Verifying API client...")

api_path = frontend_path / 'lib/academy/api.ts'
if api_path.exists():
    content = api_path.read_text(encoding='utf-8')
    
    methods = ['getStats', 'getCourses', 'getCourse', 'getCategories', 'getStandards']
    missing = [m for m in methods if m not in content]
    
    if missing:
        print(f"   ❌ Missing methods: {', '.join(missing)}")
        all_pages_ok = False
    else:
        print(f"   ✅ All {len(methods)} API methods present")
    
    # Check error handling
    if 'try {' in content and 'catch' in content:
        print("   ✅ Error handling present")
    else:
        print("   ⚠️  Missing error handling")
else:
    print("   ❌ API client not found")
    all_pages_ok = False

# ============================================================
# 5. VERIFY HOOKS
# ============================================================
print("\n5️⃣  Verifying hooks...")

hooks_path = frontend_path / 'hooks/academy/useAcademy.ts'
if hooks_path.exists():
    content = hooks_path.read_text(encoding='utf-8')
    
    hooks = ['useAcademyStats', 'useCourses', 'useCourse', 'useCategories']
    missing = [h for h in hooks if h not in content]
    
    if missing:
        print(f"   ❌ Missing hooks: {', '.join(missing)}")
        all_pages_ok = False
    else:
        print(f"   ✅ All {len(hooks)} hooks present")
else:
    print("   ❌ Hooks file not found")
    all_pages_ok = False

# ============================================================
# 6. VERIFY BACKEND
# ============================================================
print("\n6️⃣  Verifying backend...")

router_path = backend_path / 'modules/academy/router.py'
if router_path.exists():
    content = router_path.read_text(encoding='utf-8-sig')
    
    endpoints = ['statistics', 'courses', 'categories', 'standards']
    missing = [e for e in endpoints if f'/{e}' not in content]
    
    if missing:
        print(f"   ❌ Missing endpoints: {', '.join(missing)}")
        all_pages_ok = False
    else:
        print(f"   ✅ All {len(endpoints)} endpoints present")
    
    # Check registration in main.py
    main_path = backend_path / 'main.py'
    if main_path.exists():
        main_content = main_path.read_text(encoding='utf-8-sig')
        if 'academy_router' in main_content:
            print("   ✅ Router registered in main.py")
        else:
            print("   ❌ Router NOT registered in main.py")
            all_pages_ok = False
else:
    print("   ❌ Router not found")
    all_pages_ok = False

# ============================================================
# 7. CHECK IMPORTS IN MAIN PAGE
# ============================================================
print("\n7️⃣  Checking imports in main academy page...")

if page_path.exists():
    content = page_path.read_text(encoding='utf-8')
    
    required_imports = [
        "useAcademyStats",
        "useCourses",
        "useCategories",
        "from '@/hooks/academy/useAcademy'"
    ]
    
    missing = [imp for imp in required_imports if imp not in content]
    
    if missing:
        print(f"   ❌ Missing imports: {missing}")
        all_pages_ok = False
    else:
        print("   ✅ All required imports present")

# ============================================================
# 8. SUMMARY
# ============================================================
print("\n" + "=" * 80)
if all_pages_ok:
    print("✅ ALL CHECKS PASSED - ACADEMY MODULE IS READY")
else:
    print("⚠️  SOME ISSUES FOUND - SEE ABOVE")
print("=" * 80)

print("\n🚀 Next steps:")
print("   1. Clear Next.js cache:")
print("      cd D:\\econojin.com\\apps\\web")
print("      Remove-Item -Recurse -Force .next")
print("\n   2. Restart backend:")
print("      cd D:\\econojin.com")
print("      uvicorn api.main:app --reload --port 8000")
print("\n   3. Restart frontend:")
print("      cd D:\\econojin.com\\apps\\web")
print("      npx next dev -p 3001")
print("\n   4. Visit and hard refresh:")
print("      http://localhost:3001/academy")
print("      Press Ctrl+Shift+R to clear browser cache")

print("\n🔍 If still not working:")
print("   - Open browser DevTools (F12)")
print("   - Check Console tab for errors")
print("   - Check Network tab for failed API calls")
print("   - Verify backend is running on port 8000")
print("   - Check if http://localhost:8000/api/v1/academy/courses returns data")