"""
🔧 اتصال کامل صفحات آکادمی و پاک‌سازی Cache
"""
from pathlib import Path
import subprocess
import sys

print("=" * 80)
print("🔧 FIXING ACADEMY PAGES CONNECTION & CLEARING CACHE")
print("=" * 80)

frontend_path = Path('apps/web/src')
backend_path = Path('api')

# ============================================================
# 1. VERIFY ALL FILES EXIST
# ============================================================
print("\n1️⃣  Verifying file structure...")

required_files = [
    'app/academy/page.tsx',
    'app/academy/courses/[id]/page.tsx',
    'app/academy/courses/[id]/lessons/[lessonId]/page.tsx',
    'app/academy/create/page.tsx',
    'app/academy/my-courses/page.tsx',
    'app/academy/certificates/page.tsx',
    'app/academy/guide/page.tsx',
    'lib/academy/api.ts',
    'hooks/academy/useAcademy.ts'
]

all_exist = True
for file in required_files:
    full_path = frontend_path / file
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"   ✅ {file} ({size:,} bytes)")
    else:
        print(f"   ❌ {file} [MISSING]")
        all_exist = False

if not all_exist:
    print("\n❌ Some files are missing! Please run create scripts first.")
    sys.exit(1)

# ============================================================
# 2. FIX REMAINING 'any' TYPE
# ============================================================
print("\n2️⃣  Fixing remaining 'any' type...")

page_path = frontend_path / 'app/academy/page.tsx'
if page_path.exists():
    content = page_path.read_text(encoding='utf-8')
    
    # Find and fix any remaining 'any' types
    if 'categoryIcons: Record<string, any>' in content:
        content = content.replace(
            'categoryIcons: Record<string, any>',
            'categoryIcons: Record<string, React.ComponentType<{ className?: string }>>'
        )
        page_path.write_text(content, encoding='utf-8')
        print("   ✅ Fixed categoryIcons type")
    elif ': any' in content:
        # Find the line with 'any'
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if ': any' in line and 'categoryIcons' in line:
                lines[i] = line.replace(': any', ': React.ComponentType<{ className?: string }>')
                content = '\n'.join(lines)
                page_path.write_text(content, encoding='utf-8')
                print("   ✅ Fixed remaining 'any' type")
                break
    else:
        print("   ✅ No 'any' types found")

# ============================================================
# 3. ADD MISSING EXPORTS TO API CLIENT
# ============================================================
print("\n3️⃣  Checking API client exports...")

api_path = frontend_path / 'lib/academy/api.ts'
if api_path.exists():
    content = api_path.read_text(encoding='utf-8')
    
    # Check if all methods are exported
    required_methods = ['getStats', 'getCourses', 'getCourse', 'getCategories', 'getStandards']
    missing_methods = []
    
    for method in required_methods:
        if method not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"   ⚠️  Missing methods: {', '.join(missing_methods)}")
        # Recreate API client with all methods
        api_content = '''import api from '@/lib/api-client';

export const academyApi = {
  getStats: async () => {
    try {
      const response = await api.get('/api/v1/academy/statistics');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch academy stats:', error);
      throw error;
    }
  },
  
  getCourses: async (params?: { category?: string; level?: string }) => {
    try {
      const response = await api.get('/api/v1/academy/courses', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch courses:', error);
      throw error;
    }
  },
  
  getCourse: async (id: number) => {
    try {
      const response = await api.get(`/api/v1/academy/courses/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch course ${id}:`, error);
      throw error;
    }
  },
  
  getCategories: async () => {
    try {
      const response = await api.get('/api/v1/academy/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  },
  
  getStandards: async () => {
    try {
      const response = await api.get('/api/v1/academy/standards');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch standards:', error);
      throw error;
    }
  },
};
'''
        api_path.write_text(api_content, encoding='utf-8')
        print("   ✅ Recreated API client with all methods")
    else:
        print("   ✅ All API methods present")

# ============================================================
# 4. CHECK HOOKS EXPORTS
# ============================================================
print("\n4️⃣  Checking hooks exports...")

hooks_path = frontend_path / 'hooks/academy/useAcademy.ts'
if hooks_path.exists():
    content = hooks_path.read_text(encoding='utf-8')
    
    required_hooks = ['useAcademyStats', 'useCourses', 'useCourse', 'useCategories']
    missing_hooks = []
    
    for hook in required_hooks:
        if hook not in content:
            missing_hooks.append(hook)
    
    if missing_hooks:
        print(f"   ⚠️  Missing hooks: {', '.join(missing_hooks)}")
        # Recreate hooks
        hooks_content = '''import { useQuery } from '@tanstack/react-query';
import { academyApi } from '@/lib/academy/api';

export function useAcademyStats() {
  return useQuery({
    queryKey: ['academy', 'stats'],
    queryFn: academyApi.getStats,
  });
}

export function useCourses(filters?: { category?: string; level?: string }) {
  return useQuery({
    queryKey: ['academy', 'courses', filters],
    queryFn: () => academyApi.getCourses(filters),
  });
}

export function useCourse(id: number) {
  return useQuery({
    queryKey: ['academy', 'course', id],
    queryFn: () => academyApi.getCourse(id),
    enabled: !!id,
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ['academy', 'categories'],
    queryFn: academyApi.getCategories,
  });
}
'''
        hooks_path.write_text(hooks_content, encoding='utf-8')
        print("   ✅ Recreated hooks with all exports")
    else:
        print("   ✅ All hooks present")

# ============================================================
# 5. CLEAR NEXT.JS CACHE
# ============================================================
print("\n5️⃣  Clearing Next.js cache...")

next_cache = Path('apps/web/.next')
if next_cache.exists():
    try:
        import shutil
        shutil.rmtree(next_cache)
        print("   ✅ Next.js cache cleared")
    except Exception as e:
        print(f"   ⚠️  Could not clear cache: {e}")
else:
    print("   ✅ No cache to clear")

# ============================================================
# 6. CHECK IMPORTS IN MAIN PAGE
# ============================================================
print("\n6️⃣  Checking imports in academy page...")

if page_path.exists():
    content = page_path.read_text(encoding='utf-8')
    
    required_imports = [
        "from '@/hooks/academy/useAcademy'",
        "useAcademyStats",
        "useCourses",
        "useCategories"
    ]
    
    missing_imports = []
    for imp in required_imports:
        if imp not in content:
            missing_imports.append(imp)
    
    if missing_imports:
        print(f"   ⚠️  Missing imports: {missing_imports}")
    else:
        print("   ✅ All required imports present")

# ============================================================
# 7. VERIFY BACKEND ROUTER
# ============================================================
print("\n7️⃣  Verifying backend router...")

router_path = backend_path / 'modules/academy/router.py'
if router_path.exists():
    content = router_path.read_text(encoding='utf-8-sig')
    
    # Check if router is properly defined
    if 'router = APIRouter' in content:
        print("   ✅ Router properly defined")
    else:
        print("   ❌ Router not properly defined")
    
    # Check endpoints
    endpoints = ['statistics', 'courses', 'categories', 'standards']
    for endpoint in endpoints:
        if f'/{endpoint}' in content:
            print(f"   ✅ Endpoint /{endpoint} found")
        else:
            print(f"   ❌ Endpoint /{endpoint} missing")
else:
    print("   ❌ Router file not found")

# ============================================================
# 8. CHECK MAIN.PY REGISTRATION
# ============================================================
print("\n8️⃣  Checking main.py registration...")

main_path = backend_path / 'main.py'
if main_path.exists():
    content = main_path.read_text(encoding='utf-8-sig')
    
    if 'academy_router' in content:
        print("   ✅ Academy router registered in main.py")
    else:
        print("   ❌ Academy router NOT registered in main.py")
        print("   💡 Please add: from api.modules.academy.router import router as academy_router")
        print("   💡 And: app.include_router(academy_router, prefix='/api/v1')")
else:
    print("   ❌ main.py not found")

# ============================================================
# 9. SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("✅ ALL CHECKS COMPLETE")
print("=" * 80)

print("\n🚀 Next steps:")
print("   1. Restart backend:")
print("      uvicorn api.main:app --reload --port 8000")
print("\n   2. Restart frontend:")
print("      cd apps/web")
print("      npx next dev -p 3001")
print("\n   3. Visit:")
print("      http://localhost:3001/academy")
print("      http://localhost:3001/academy/courses/1")
print("      http://localhost:3001/academy/my-courses")
print("      http://localhost:3001/academy/certificates")
print("      http://localhost:3001/academy/guide")

print("\n💡 If pages still don't work:")
print("   - Clear browser cache (Ctrl+Shift+R)")
print("   - Check browser console for errors")
print("   - Verify backend is running on port 8000")
print("   - Check network tab for API calls")