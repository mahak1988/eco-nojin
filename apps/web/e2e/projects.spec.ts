import { test, expect } from '@playwright/test'

test.describe('Projects', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')
  })

  test('should create a new project', async ({ page }) => {
    await page.goto('/projects/new')
    
    await page.fill('input[name="name"]', 'Test Project')
    await page.fill('textarea[name="description"]', 'Test description')
    await page.selectOption('select[name="status"]', 'active')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/projects')
    await expect(page.locator('text=Test Project')).toBeVisible()
  })

  test('should edit an existing project', async ({ page }) => {
    await page.goto('/projects')
    await page.click('text=Edit')
    
    await page.fill('input[name="name"]', 'Updated Project Name')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('text=Updated Project Name')).toBeVisible()
  })
})