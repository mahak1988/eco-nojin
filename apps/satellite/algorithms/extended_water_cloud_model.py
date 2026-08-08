"""
ماژول الگوریتم Extended Water Cloud Model (EWCM) - نسخه تکمیل شده

این ماژول بخشی از تلاش برای پیاده‌سازی مرحله ۱ مانیفست Hydroma-Nojin است.
هدف: پیاده‌سازی یک الگوریتم فیزیکی برای استخراج رطوبت خاک از داده C-Band SAR (Sentinel-1).
این نسخه یک پیاده‌سازی نمادین و ساده شده است.
"""

import numpy as np
from typing import Dict


def calculate_vegetation_transmittance_B(b_vv: float, b_vh: float, vwc: float, lai: float, angle_deg: float) -> tuple:
    """
    محاسبه تابع عبور گیاه (tau_veg) با استفاده از پارامتر B بهبود یافته.
    پارامتر B می‌تواند بر اساس LAI و فنولوژی محصول تغییر کند.
    """
    theta = np.radians(angle_deg)
    # مدل ساده برای B بسته به LAI
    # این یک تابع نمادین است. در عمل باید از مطالعات تجربی آمده باشد.
    B_vv_adaptive = b_vv * (1 + 0.1 * lai) # B بیشتر با افزایش LAI
    B_vh_adaptive = b_vh * (1 + 0.1 * lai)

    tau_veg_vv = np.exp(- B_vv_adaptive * vwc / np.cos(theta))
    tau_veg_vh = np.exp(- B_vh_adaptive * vwc / np.cos(theta))
    return tau_veg_vv, tau_veg_vh


def calculate_soil_moisture_ewcm(
    sigma_vv: np.ndarray,
    sigma_vh: np.ndarray,
    lai: float,
    vwc: float,
    frequency_hz: float = 5.405e9, # C-Band
    angle_deg: float = 39.0, # incidence angle
    sigma_rough_dry_vv: float = -15.0, # σ^0 rough dry soil (dB) for VV
    sigma_rough_dry_vh: float = -20.0,  # σ^0 rough dry soil (dB) for VH
    b_vv: float = 0.05, # ضریب تأثیر VWC در VV
    b_vh: float = 0.03  # ضریب تأثیر VWC در VH
) -> np.ndarray:
    """
    تخمین رطوبت حجمی خاک (VSM) با استفاده از EWCM.

    Args:
        sigma_vv: سیگنال backscatter VV (dB).
        sigma_vh: سیگنال backscatter VH (dB).
        lai: شاخص سطح برگ.
        vwc: محتوای آب پوشش گیاهی.
        frequency_hz: فرکانس موج (هرتز).
        angle_deg: زاویه ورودی (درجه).
        sigma_rough_dry_vv, sigma_rough_dry_vh: σ^0 خاک خشک ناهموار مرجع.
        b_vv, b_vh: ضرایب اولیه تأثیر VWC.

    Returns:
        تخمین رطوبت حجمی خاک (VSM).
    """
    # تبدیل dB به linear
    sigma_vv_lin = 10**(sigma_vv / 10.0)
    sigma_vh_lin = 10**(sigma_vh / 10.0)

    # محاسبه تابع عبور گیاه با در نظر گرفتن LAI
    tau_veg_vv, tau_veg_vh = calculate_vegetation_transmittance_B(b_vv, b_vh, vwc, lai, angle_deg)

    # تقریب σ^0_veg
    sigma_veg_vv_approx = b_vv * vwc
    sigma_veg_vh_approx = b_vh * vwc

    # محاسبه σ^0_soil تخمینی
    sigma_soil_vv_lin_estim = (sigma_vv_lin - sigma_veg_vv_approx) / (tau_veg_vv**2)
    sigma_soil_vh_lin_estim = (sigma_vh_lin - sigma_veg_vh_approx) / (tau_veg_vh**2)

    sigma_soil_vv_db_estim = 10 * np.log10(sigma_soil_vv_lin_estim)
    sigma_soil_vh_db_estim = 10 * np.log10(sigma_soil_vh_lin_estim)

    # حل معکوس مدل IEM ساده شده
    k_param = 0.2 # dB / (m3/m3)
    vsm_vv = (sigma_soil_vv_db_estim - sigma_rough_dry_vv) / k_param
    vsm_vh = (sigma_soil_vh_db_estim - sigma_rough_dry_vh) / k_param

    # ترکیب تخمین‌ها
    vsm_combined = 0.6 * vsm_vv + 0.4 * vsm_vh

    # محدود کردن مقدار رطوبت بین 0 و 1
    vsm = np.clip(vsm_combined, 0.0, 1.0)

    return vsm


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("Testing Extended Water Cloud Model with Adaptive B...")
    sig_vv = np.array([-10.0])
    sig_vh = np.array([-18.0])
    lai_val = 3.0 # LAI بالاتر
    vwc_val = 0.25
    freq = 5.405e9
    angle = 39.0

    vsm_estimate = calculate_soil_moisture_ewcm(sig_vv, sig_vh, lai_val, vwc_val, freq, angle)
    print(f"Estimated VSM (LAI={lai_val}): {vsm_estimate[0]:.3f}")