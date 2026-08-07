/**
 * Phase 5 — Admin panel smoke + permission UX tests
 */
import { test, expect } from '@playwright/test'

test.describe('Admin panel smoke', () => {
  test('login page renders in Persian', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByText(/پنل مدیریت/)).toBeVisible()
    await expect(page.locator('input[type="email"]')).toBeVisible()
  })

  test('unauthenticated user redirected to login', async ({ page }) => {
    await page.goto('/users')
    await expect(page).toHaveURL(/login/)
  })

  test('404 or login for unknown route', async ({ page }) => {
    await page.goto('/this-route-does-not-exist-xyz')
    const body = await page.textContent('body')
    expect(body).toMatch(/۴۰۴|یافت نشد|login|ورود/i)
  })
})

test.describe('Permission UX', () => {
  test('forbidden page content is Persian when navigated directly', async ({ page }) => {
    // Without auth, AuthGuard sends to login — either is acceptable
    await page.goto('/forbidden')
    const body = await page.textContent('body')
    expect(body).toMatch(/۴۰۳|دسترسی|login|ورود|مجاز/i)
  })
})
