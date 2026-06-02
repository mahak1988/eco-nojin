import { test, expect } from "@playwright/test";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

test.describe("Login → Farmers flow", () => {
  test("OTP login and farmers page loads", async ({ page }) => {
    const otpRes = await page.request.post(`${API}/api/v1/auth/otp/request`, {
      data: { phone: "+989009009009", fid: "e2e_farmer" },
    });
    expect(otpRes.ok()).toBeTruthy();
    const { dev_code } = await otpRes.json();
    expect(dev_code).toBeTruthy();

    const verifyRes = await page.request.post(`${API}/api/v1/auth/otp/verify`, {
      data: {
        phone: "+989009009009",
        code: dev_code,
        fid: "e2e_farmer",
        name: "E2E User",
      },
    });
    expect(verifyRes.ok()).toBeTruthy();
    const { access_token } = await verifyRes.json();

    await page.context().addCookies([
      {
        name: "econojin_token",
        value: access_token,
        url: "http://localhost:3001",
      },
    ]);

    await page.goto("/fa/farmers");
    await expect(page.getByText(/کشاورز|Farmers|ثبت کشاورز/i)).toBeVisible({ timeout: 15_000 });
  });
});
