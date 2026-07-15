# =====================================================
# اسکریپت اصلاح خودکار خطاهای TypeScript
# =====================================================

$ErrorActionPreference = "Continue"
$srcDir = "D:\econojin.com\apps\web\src"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  شروع اصلاح خودکار خطاهای TypeScript" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# =====================================================
# ۱. اصلاح api.ts (Syntax Error)
# =====================================================
Write-Host "📝 ۱. اصلاح api.ts..." -ForegroundColor Yellow

$apiPath = Join-Path $srcDir "services\api.ts"

$apiContent = @"
import axios from 'axios';
import { API_BASE_URL } from '@/utils/constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = ``Bearer `${token}``;
  }
  return config;
});

// Interceptor to handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
export { apiClient };
"@

Set-Content -Path $apiPath -Value $apiContent -Encoding UTF8
Write-Host "   ✅ api.ts اصلاح شد" -ForegroundColor Green

# =====================================================
# ۲. اصلاح Chat.tsx
# =====================================================
Write-Host "`n📝 ۲. اصلاح Chat.tsx..." -ForegroundColor Yellow

$chatPath = Join-Path $srcDir "pages\Chat.tsx"

if (Test-Path $chatPath) {
    $chatContent = Get-Content -Path $chatPath -Raw -Encoding UTF8
    
    # اصلاح import apiClient
    $chatContent = $chatContent -replace "import \{ apiClient \} from '@/services/api';", "import apiClient from '@/services/api';"
    
    # اصلاح FiBot به FiCpu
    $chatContent = $chatContent -replace "FiBot", "FiCpu"
    
    Set-Content -Path $chatPath -Value $chatContent -Encoding UTF8 -NoNewline
    Write-Host "   ✅ Chat.tsx اصلاح شد" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Chat.tsx وجود ندارد" -ForegroundColor Red
}

# =====================================================
# ۳. اصلاح Documents.tsx
# =====================================================
Write-Host "`n📝 ۳. اصلاح Documents.tsx..." -ForegroundColor Yellow

$docsPath = Join-Path $srcDir "pages\Documents.tsx"

if (Test-Path $docsPath) {
    $docsContent = Get-Content -Path $docsPath -Raw -Encoding UTF8
    
    # اصلاح import apiClient
    $docsContent = $docsContent -replace "import \{ apiClient \} from '@/services/api';", "import apiClient from '@/services/api';"
    
    Set-Content -Path $docsPath -Value $docsContent -Encoding UTF8 -NoNewline
    Write-Host "   ✅ Documents.tsx اصلاح شد" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Documents.tsx وجود ندارد" -ForegroundColor Red
}

# =====================================================
# ۴. ایجاد type declaration برای window.ethereum
# =====================================================
Write-Host "`n📝 ۴. ایجاد type declaration برای window.ethereum..." -ForegroundColor Yellow

$typesPath = Join-Path $srcDir "types\ethereum.d.ts"

$ethereumTypes = @"
// Type declaration for window.ethereum (MetaMask)
interface Window {
  ethereum?: {
    isMetaMask?: boolean;
    request: (args: { method: string; params?: any[] }) => Promise<any>;
    on: (event: string, callback: (...args: any[]) => void) => void;
    removeListener: (event: string, callback: (...args: any[]) => void) => void;
  };
}
"@

Set-Content -Path $typesPath -Value $ethereumTypes -Encoding UTF8
Write-Host "   ✅ ethereum.d.ts ایجاد شد" -ForegroundColor Green

# =====================================================
# ۵. بررسی و اصلاح Login.tsx
# =====================================================
Write-Host "`n📝 ۵. بررسی Login.tsx..." -ForegroundColor Yellow

$loginPath = Join-Path $srcDir "pages\Login.tsx"
$useAuthPath = Join-Path $srcDir "hooks\useAuth.tsx"

if (Test-Path $loginPath -and (Test-Path $useAuthPath)) {
    $useAuthContent = Get-Content -Path $useAuthPath -Raw -Encoding UTF8
    
    # بررسی اینکه آیا login در useAuth وجود دارد
    if ($useAuthContent -match "login:") {
        Write-Host "   ✅ login در useAuth وجود دارد" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  login در useAuth وجود ندارد - باید اضافه شود" -ForegroundColor Red
        
        # نمایش محتوای useAuth برای بررسی
        Write-Host "`n   محتوای useAuth.tsx:" -ForegroundColor Gray
        Get-Content -Path $useAuthPath | Select-Object -First 30
    }
} else {
    Write-Host "   ⚠️  Login.tsx یا useAuth.tsx وجود ندارد" -ForegroundColor Red
}

# =====================================================
# ۶. تست Build
# =====================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  تست Build..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location "D:\econojin.com\apps\web"
pnpm build

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  پایان اصلاح خودکار" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan