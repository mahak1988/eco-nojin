/**
 * Phase 3 — Admin panel smoke tests (Playwright-compatible skeleton)
 *
 * Run (when Playwright is configured):
 *   npx playwright test apps/admin_panel/frontend/e2e/admin-smoke.spec.ts
 *
 * These tests document critical paths; adapt selectors to your env.
 */

import { test, expect } from '@playwright/test'

const BASE = process.env.ADMIN_BASE_URL || 'http://localhost:5173'

test.describe('Admin panel smoke', () => {
  test('login page renders in Persian', async ({ page }) => {
    await page.goto(`${BASE}/login`)
    await expect(page.getByRole('heading', { name: /پنل مدیریت/ })).toBeVisible()
    await expect(page.getByLabel(/ایمیل|email/i).or(page.locator('input[type="email"]'))).toBeVisible()
  })

  test('unauthenticated user redirected to login', async ({ page }) => {
    await page.goto(`${BASE}/users`)
    await expect(page).toHaveURL(/login/)
  })

  test('404 page is Persian', async ({ page }) => {
    // May redirect to login first if AuthGuard wraps all routes
    await page.goto(`${BASE}/this-route-does-not-exist-xyz`)
    const body = await page.textContent('body')
    expect(body).toMatch(/۴۰۴|یافت نشد|login|ورود/i)
  })
})
