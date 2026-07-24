# مستندات اتصال فرانت‌اند به بک‌اند
# Backend Integration Documentation

## 📋 خلاصه تغییرات | Summary of Changes

این مستندات خلاءهای شناسایی‌شده بین فرانت‌اند و بک‌اند را پر کرده و ارتباط صحیح را برقرار می‌کند.

This documentation bridges the identified gaps between frontend and backend, establishing proper communication.

---

## 🔍 خلاءهای شناسایی‌شده | Identified Gaps

### ۱. عدم تطابق تایپ‌ها | Type Mismatch
- **مشکل**: تایپ‌های فرانت‌اند با اسکیماهای پایتون در بک‌اند مطابقت نداشتند
- **حل**: ایجاد فایل `backend.ts` با تایپ‌های دقیقاً منطبق بر بک‌اند

### ۲. سرویس‌های ناقص | Incomplete Services  
- **مشکل**: سرویس‌های فرانت‌اند اندپوینت‌های بک‌اند را به درستی صدا نمی‌زدند
- **حل**: ایجاد `backendService.ts` با متدهای کامل برای تمام ماژول‌ها

### ۳. مسیرهای API ناسازگار | Incompatible API Routes
- **مشکل**: مسیرهای API در فرانت‌اند با روترهای FastAPI همخوانی نداشتند
- **حل**: به‌روزرسانی مسیرها بر اساس `apps/main.py` و روترهای ماژول‌ها

---

## 📁 فایل‌های ایجادشده | Created Files

### ۱. `/src/types/backend.ts`
تعاریف TypeScript که دقیقاً با Pydantic schemas در بک‌اند مطابقت دارند:

```typescript
// Auth Types (matching auth_router.py)
export interface LoginRequest {
  email?: string;
  username?: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: BackendUser;
}

// Admin Types (matching admin_panel/schemas.py)
export interface AdminDashboardSummary {
  user_count: number;
  active_user_count: number;
  // ...
}

// AI Agents Types (matching ai_agents/schemas.py)
export type AgentType = "financial" | "support" | "admin" | "research" | "data_analyst" | "code_assistant";

// Simulation Types (matching simulation/schemas.py)
export interface Simulation {
  id: number;
  name: string;
  is_active: boolean;
  // ...
}
```

### ۲. `/src/services/backendService.ts`
سرویس لایه کامل برای ارتباط با تمام اندپوینت‌های بک‌اند:

```typescript
// Authentication
authService.login()      // POST /api/v1/auth/login
authService.register()   // POST /api/v1/auth/register
authService.getCurrentUser() // GET /api/v1/auth/me
authService.logout()     // POST /api/v1/auth/logout
authService.refreshToken() // POST /api/v1/auth/refresh

// User Management
usersService.getProfile()    // GET /api/v1/users/me
usersService.updateProfile() // PUT /api/v1/users/me
usersService.listUsers()     // GET /api/v1/users/ (admin)

// Admin Panel
adminService.getDashboardSummary() // GET /api/v1/admin/
adminService.listSettings()        // GET /api/v1/admin/settings
adminService.updateSetting()       // PUT /api/v1/admin/settings/{key}
adminService.listAuditLogs()       // GET /api/v1/admin/audit-logs
adminService.listReports()         // GET /api/v1/admin/reports

// AI Agents
aiAgentsService.createConversation() // POST /api/v1/ai-agents/conversations
aiAgentsService.getConversation()    // GET /api/v1/ai-agents/conversations/{id}
aiAgentsService.chat()               // POST /api/v1/ai-agents/chat

// Simulation
simulationService.listSimulations()   // GET /api/v1/simulation/
simulationService.createSimulation()  // POST /api/v1/simulation/
simulationService.getSimulation()     // GET /api/v1/simulation/{id}
simulationService.updateSimulation()  // PATCH /api/v1/simulation/{id}
simulationService.deleteSimulation()  // DELETE /api/v1/simulation/{id}
```

### ۳. `/src/types/index.ts` (به‌روزرسانی‌شده)
صادرات تمام تایپ‌ها از یک نقطه مرکزی

---

## 🔗 نقشه اتصال ماژول‌ها | Module Connection Map

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)              │
├─────────────────────────────────────────────────────────────┤
│  Pages → Hooks → Services → API Client → Backend            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI/Python)                 │
├─────────────────────────────────────────────────────────────┤
│  main.py → Routers → Services → Models → Database           │
└─────────────────────────────────────────────────────────────┘
```

### ماژول Users/Auth
| Frontend | Backend Router | Endpoint |
|----------|---------------|----------|
| `authService.login()` | `apps/users/auth_router.py` | `POST /api/v1/auth/login` |
| `authService.register()` | `apps/users/auth_router.py` | `POST /api/v1/auth/register` |
| `authService.getCurrentUser()` | `apps/users/auth_router.py` | `GET /api/v1/auth/me` |
| `usersService.getProfile()` | `apps/users/router.py` | `GET /api/v1/users/me` |

### ماژول Admin
| Frontend | Backend Router | Endpoint |
|----------|---------------|----------|
| `adminService.getDashboardSummary()` | `apps/admin_panel/router.py` | `GET /api/v1/admin/` |
| `adminService.listSettings()` | `apps/admin_panel/router.py` | `GET /api/v1/admin/settings` |
| `adminService.updateSetting()` | `apps/admin_panel/router.py` | `PUT /api/v1/admin/settings/{key}` |
| `adminService.listAuditLogs()` | `apps/admin_panel/router.py` | `GET /api/v1/admin/audit-logs` |
| `adminService.listReports()` | `apps/admin_panel/router.py` | `GET /api/v1/admin/reports` |

### ماژول AI Agents
| Frontend | Backend Router | Endpoint |
|----------|---------------|----------|
| `aiAgentsService.createConversation()` | `apps/ai_agents/router.py` | `POST /api/v1/ai-agents/conversations` |
| `aiAgentsService.getConversation()` | `apps/ai_agents/router.py` | `GET /api/v1/ai-agents/conversations/{id}` |
| `aiAgentsService.chat()` | `apps/ai_agents/router.py` | `POST /api/v1/ai-agents/chat` |

### ماژول Simulation
| Frontend | Backend Router | Endpoint |
|----------|---------------|----------|
| `simulationService.listSimulations()` | `apps/simulation/router.py` | `GET /api/v1/simulation/` |
| `simulationService.createSimulation()` | `apps/simulation/router.py` | `POST /api/v1/simulation/` |
| `simulationService.getSimulation()` | `apps/simulation/router.py` | `GET /api/v1/simulation/{id}` |
| `simulationService.updateSimulation()` | `apps/simulation/router.py` | `PATCH /api/v1/simulation/{id}` |
| `simulationService.deleteSimulation()` | `apps/simulation/router.py` | `DELETE /api/v1/simulation/{id}` |

---

## 🚀 نحوه استفاده | Usage Examples

### مثال لاگین | Login Example
```typescript
import { authService } from "@/services/backendService";

async function handleLogin(identifier: string, password: string) {
  try {
    const response = await authService.login({
      email: identifier.includes("@") ? identifier : undefined,
      username: identifier.includes("@") ? undefined : identifier,
      password,
    });
    
    console.log("Access Token:", response.accessToken);
    console.log("User:", response.user);
  } catch (error) {
    console.error("Login failed:", error);
  }
}
```

### مثال دریافت اطلاعات کاربر | Get Current User
```typescript
import { authService } from "@/services/backendService";

async function loadUserProfile() {
  try {
    const user = await authService.getCurrentUser();
    console.log("User Profile:", user);
  } catch (error) {
    console.error("Failed to load profile:", error);
  }
}
```

### مثال چت با AI | Chat with AI
```typescript
import { aiAgentsService } from "@/services/backendService";

async function chatWithAI(message: string, agentType: AgentType = "financial") {
  try {
    const response = await aiAgentsService.chat({
      message,
      agent_type: agentType,
    });
    
    console.log("AI Response:", response.assistant_message);
    return response;
  } catch (error) {
    console.error("Chat failed:", error);
  }
}
```

### مثال پنل ادمین | Admin Dashboard
```typescript
import { adminService } from "@/services/backendService";

async function loadAdminDashboard() {
  try {
    const summary = await adminService.getDashboardSummary();
    console.log("Dashboard Summary:", summary);
    
    const settings = await adminService.listSettings();
    console.log("Settings:", settings);
  } catch (error) {
    console.error("Dashboard load failed:", error);
  }
}
```

---

## ✅ بررسی صحت اتصال | Verification Checklist

- [x] تایپ‌های TypeScript با Pydantic schemas مطابقت دارند
- [x] مسیرهای API با routerهای FastAPI همخوانی دارند
- [x] متدهای HTTP (GET, POST, PUT, PATCH, DELETE) صحیح هستند
- [x] پارامترهای درخواست و پاسخ درست تعریف شده‌اند
- [x] احراز هویت (JWT Bearer Token) پیاده‌سازی شده است
- [x] مدیریت خطاها به درستی انجام می‌شود

---

## 📝 نکات مهم | Important Notes

1. **Base URL**: تمام درخواست‌ها به `${VITE_API_BASE_URL}/api/v1` ارسال می‌شوند
2. **Authentication**: توکن JWT به صورت خودکار توسط apiClient اضافه می‌شود
3. **Error Handling**: خطاها از طریق Axios interceptors مدیریت می‌شوند
4. **Type Safety**: تمام سرویس‌ها کاملاً تایپ‌شده هستند

---

## 🔧 پیکربندی محیطی | Environment Configuration

در فایل `.env` فرانت‌اند:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📚 مستندات بیشتر | Additional Resources

- بک‌اند: `/apps/main.py` - نقطه ورود اصلی
- احراز هویت: `/apps/users/auth_router.py`
- پنل ادمین: `/apps/admin_panel/router.py`
- ایجنت‌های هوش مصنوعی: `/apps/ai_agents/router.py`
- شبیه‌سازی: `/apps/simulation/router.py`
