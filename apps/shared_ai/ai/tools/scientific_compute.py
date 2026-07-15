"""
محاسبات علمی با SciPy (جایگزین Julia)

این ماژول از SciPy برای محاسبات علمی پیشرفته استفاده می‌کند.
"""

from langchain_core.tools import tool
from typing import List
import logging
import numpy as np
from scipy import integrate, linalg, stats
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import time

logger = logging.getLogger(__name__)


# ==========================================
# Differential Equations with SciPy
# ==========================================

@tool
async def solve_differential_equation(
    equation_type: str = "ode",
    initial_conditions: List[float] = [1.0],
    time_span: List[float] = [0.0, 10.0],
    coefficients: List[float] = [1.0]
) -> str:
    """
    حل معادلات دیفرانسیل با SciPy (solve_ivp).
    
    Args:
        equation_type: نوع معادله (ode)
        initial_conditions: شرایط اولیه
        time_span: بازه زمانی [t0, tf]
        coefficients: ضرایب معادله
    
    Returns:
        نقاط زمانی و مقادیر حل
    
    Performance:
        - SciPy solve_ivp (RK45, Radau, BDF)
        - دقت بالا
        - سریع
    """
    logger.info(f"🧮 Solving differential equation with {len(initial_conditions)} variables")
    
    start_time = time.time()
    
    try:
        # تعریف تابع ODE
        def ode_system(t, y):
            dydt = []
            for i in range(len(y)):
                if i < len(coefficients):
                    dydt.append(coefficients[i] * y[i])
                else:
                    dydt.append(0.0)
            return dydt
        
        # حل معادله
        sol = solve_ivp(
            ode_system,
            time_span,
            initial_conditions,
            method='RK45',
            dense_output=True,
            rtol=1e-8,
            atol=1e-8
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        # نقاط زمانی برای نمایش
        t_eval = np.linspace(time_span[0], time_span[1], 100)
        y_eval = sol.sol(t_eval)
        
        output = [
            f"🧮 نتایج حل معادله دیفرانسیل (SciPy - {elapsed:.2f} ms):",
            "",
            f"⚙️ روش حل: RK45 (Runge-Kutta 4-5)",
            f"📊 تعداد نقاط: {len(sol.t)}",
            f"✅ موفقیت: {'بله' if sol.success else 'خیر'}",
            "",
            f"📈 نقاط زمانی: {len(t_eval)} نقطه",
            f"   • بازه: [{time_span[0]:.2f}, {time_span[1]:.2f}]",
            "",
            f"📊 مقادیر حل (نمونه):",
        ]
        
        # نمایش 10 نقطه
        step = len(t_eval) // 10
        for i in range(0, len(t_eval), step):
            t = t_eval[i]
            y = y_eval[:, i]
            y_str = ", ".join([f"{v:.4f}" for v in y])
            output.append(f"   • t={t:.2f}: [{y_str}]")
        
        output.extend([
            "",
            f"⚡ Performance: SciPy solve_ivp"
        ])
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Differential equation error: {e}")
        return f"❌ خطا در حل معادله: {str(e)}"


# ==========================================
# Matrix Operations with SciPy
# ==========================================

@tool
async def advanced_matrix_operations(
    matrix: List[float],
    operation: str = "eigen"
) -> str:
    """
    عملیات ماتریسی پیشرفته با SciPy (LinearAlgebra).
    
    Args:
        matrix: ماتریس به صورت لیست تخت (row-major)
        operation: نوع عملیات (eigen, svd, lu, qr, inverse, determinant)
    
    Returns:
        نتایج عملیات ماتریسی
    
    Performance:
        - SciPy linalg (LAPACK-based)
        - سریع و دقیق
    """
    logger.info(f"🔢 Performing {operation} on matrix")
    
    start_time = time.time()
    
    try:
        # تبدیل به ماتریس
        n = int(np.sqrt(len(matrix)))
        A = np.array(matrix, dtype=np.float64).reshape(n, n)
        
        output = [f"🔢 نتایج عملیات ماتریسی ({operation}):", ""]
        
        if operation == "eigen":
            eigenvalues, eigenvectors = linalg.eig(A)
            spectral_radius = np.max(np.abs(eigenvalues))
            
            output.append("📊 مقادیر ویژه:")
            for i, val in enumerate(eigenvalues):
                if np.iscomplex(val):
                    output.append(f"   • λ{i+1} = {val.real:.4f} + {val.imag:.4f}i")
                else:
                    output.append(f"   • λ{i+1} = {val.real:.4f}")
            
            output.append(f"\n📐 شعاع طیفی: {spectral_radius:.4f}")
        
        elif operation == "svd":
            U, s, Vh = linalg.svd(A)
            condition_number = np.max(s) / np.min(s)
            
            output.append("📊 مقادیر منفرد:")
            for i, val in enumerate(s):
                output.append(f"   • σ{i+1} = {val:.4f}")
            
            output.append(f"\n📐 عدد شرطی: {condition_number:.4f}")
        
        elif operation == "determinant":
            det = linalg.det(A)
            output.append(f"📊 دترمینان: {det:.4f}")
        
        elif operation == "inverse":
            try:
                inv_A = linalg.inv(A)
                det = linalg.det(A)
                output.append(f"📊 دترمینان: {det:.4f}")
                output.append("✅ ماتریس معکوس‌پذیر است")
            except linalg.LinAlgError:
                output.append("❌ ماتریس تکین است و معکوس‌پذیر نیست")
        
        elapsed = (time.time() - start_time) * 1000
        output.extend([
            "",
            f"⏱️ زمان محاسبه: {elapsed:.2f} ms",
            f"⚡ Performance: SciPy linalg (LAPACK)"
        ])
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Matrix operations error: {e}")
        return f"❌ خطا در عملیات ماتریسی: {str(e)}"


# ==========================================
# Machine Learning with SciPy/NumPy
# ==========================================

@tool
async def train_ml_model(
    X: List[float],
    y: List[float],
    model_type: str = "linear_regression",
    degree: int = 2
) -> str:
    """
    آموزش مدل‌های یادگیری ماشین با NumPy/SciPy.
    
    Args:
        X: داده‌های ورودی (لیست تخت)
        y: مقادیر هدف
        model_type: نوع مدل (linear_regression, polynomial_regression)
        degree: درجه چندجمله‌ای (برای polynomial)
    
    Returns:
        ضرایب مدل و معیارهای ارزیابی
    """
    logger.info(f"🤖 Training {model_type} model with {len(y)} samples")
    
    start_time = time.time()
    
    try:
        y_arr = np.array(y, dtype=np.float64)
        n_samples = len(y_arr)
        
        output = []
        
        if model_type == "linear_regression":
            # y = ax + b
            X_arr = np.array(X, dtype=np.float64)
            n_features = len(X_arr) // n_samples
            X_matrix = X_arr.reshape(n_samples, n_features)
            
            # افزودن bias term
            X_bias = np.hstack([np.ones((n_samples, 1)), X_matrix])
            
            # حل با normal equations
            theta = linalg.lstsq(X_bias, y_arr)[0]
            
            # پیش‌بینی
            y_pred = X_bias @ theta
            
            # معیارها
            mse = np.mean((y_arr - y_pred) ** 2)
            rmse = np.sqrt(mse)
            ss_res = np.sum((y_arr - y_pred) ** 2)
            ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
            
            output = [
                f"🤖 نتایج آموزش مدل (linear_regression):",
                "",
                f"📊 ضرایب مدل:",
                f"   • θ0 (bias) = {theta[0]:.6f}",
            ]
            
            for i in range(1, len(theta)):
                output.append(f"   • θ{i} = {theta[i]:.6f}")
            
            output.extend([
                "",
                f"📈 معیارهای ارزیابی:",
                f"   • MSE: {mse:.6f}",
                f"   • RMSE: {rmse:.6f}",
                f"   • R² Score: {r2:.6f}",
            ])
        
        elif model_type == "polynomial_regression":
            X_arr = np.array(X, dtype=np.float64).flatten()
            
            # ایجاد ویژگی‌های چندجمله‌ای
            X_poly = np.vstack([X_arr ** d for d in range(degree + 1)]).T
            
            # حل
            theta = linalg.lstsq(X_poly, y_arr)[0]
            y_pred = X_poly @ theta
            
            mse = np.mean((y_arr - y_pred) ** 2)
            rmse = np.sqrt(mse)
            
            output = [
                f"🤖 نتایج آموزش مدل (polynomial_regression - degree {degree}):",
                "",
                f"📊 ضرایب مدل:",
            ]
            
            for i, coeff in enumerate(theta):
                output.append(f"   • θ{i} (x^{i}) = {coeff:.6f}")
            
            output.extend([
                "",
                f"📈 معیارهای ارزیابی:",
                f"   • MSE: {mse:.6f}",
                f"   • RMSE: {rmse:.6f}",
            ])
        
        elapsed = (time.time() - start_time) * 1000
        output.extend([
            "",
            f"⏱️ زمان محاسبه: {elapsed:.2f} ms",
            f"⚡ Performance: NumPy/SciPy lstsq"
        ])
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ ML training error: {e}")
        return f"❌ خطا در آموزش مدل: {str(e)}"


# ==========================================
# Numerical Integration with SciPy
# ==========================================

@tool
async def numerical_integration(
    coefficients: List[float],
    bounds: List[float]
) -> str:
    """
    انتگرال‌گیری عددی با SciPy (quad).
    
    Args:
        coefficients: ضرایب چندجمله‌ای [a0, a1, a2, ...]
        bounds: کران‌های انتگرال [a, b]
    
    Returns:
        مقدار انتگرال و تخمین خطا
    """
    logger.info(f"∫ Computing integral from {bounds[0]} to {bounds[1]}")
    
    start_time = time.time()
    
    try:
        # تعریف تابع
        def f(x):
            result = 0.0
            for i, coeff in enumerate(coefficients):
                result += coeff * (x ** i)
            return result
        
        # انتگرال‌گیری
        integral, error = integrate.quad(f, bounds[0], bounds[1])
        
        elapsed = (time.time() - start_time) * 1000
        
        # نمایش تابع
        terms = []
        for i, coeff in enumerate(coefficients):
            if coeff != 0:
                if i == 0:
                    terms.append(f"{coeff}")
                elif i == 1:
                    terms.append(f"{coeff}x")
                else:
                    terms.append(f"{coeff}x^{i}")
        
        func_str = " + ".join(terms) if terms else "0"
        
        output = [
            f"∫ نتایج انتگرال‌گیری عددی (SciPy - {elapsed:.2f} ms):",
            "",
            f"📊 تابع: f(x) = {func_str}",
            f"📐 بازه: [{bounds[0]}, {bounds[1]}]",
            "",
            f"💎 مقدار انتگرال: {integral:.6f}",
            f"⚠️ تخمین خطا: {error:.2e}",
            "",
            f"⚡ Performance: SciPy quad (Gaussian quadrature)"
        ]
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Integration error: {e}")
        return f"❌ خطا در انتگرال‌گیری: {str(e)}"


# ==========================================
# Scientific Optimization with SciPy
# ==========================================

@tool
async def scientific_optimization(
    objective: str = "rosenbrock",
    initial_point: List[float] = [0.0, 0.0],
    bounds: List[List[float]] = None
) -> str:
    """
    بهینه‌سازی علمی با SciPy (Optimize).
    
    Args:
        objective: تابع هدف (rosenbrock, rastrigin, quadratic)
        initial_point: نقطه اولیه
        bounds: کران‌های جستجو
    
    Returns:
        نقطه بهینه و مقدار بهینه
    """
    logger.info(f"⚡ Optimizing {objective} function")
    
    start_time = time.time()
    
    try:
        # تعریف تابع هدف
        if objective == "rosenbrock":
            def func(x):
                return (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2
        elif objective == "rastrigin":
            def func(x):
                A = 10
                n = len(x)
                return A * n + sum(xi ** 2 - A * np.cos(2 * np.pi * xi) for xi in x)
        else:  # quadratic
            def func(x):
                return sum(xi ** 2 for xi in x)
        
        # حل بهینه‌سازی
        if bounds:
            result = minimize(func, initial_point, method='L-BFGS-B', bounds=bounds)
        else:
            result = minimize(func, initial_point, method='Nelder-Mead')
        
        elapsed = (time.time() - start_time) * 1000
        
        output = [
            f"⚡ نتایج بهینه‌سازی علمی (SciPy - {elapsed:.2f} ms):",
            "",
            f"🎯 تابع هدف: {objective}",
            f"✅ همگرایی: {'بله' if result.success else 'خیر'}",
            f"🔄 تعداد تکرارها: {result.nit}",
            "",
            f"💎 نقطه بهینه:",
        ]
        
        for i, val in enumerate(result.x):
            output.append(f"   • x{i+1} = {val:.6f}")
        
        output.extend([
            "",
            f"📊 مقدار بهینه: {result.fun:.6f}",
            f"📝 پیام: {result.message}",
            "",
            f"⚡ Performance: SciPy optimize"
        ])
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Optimization error: {e}")
        return f"❌ خطا در بهینه‌سازی: {str(e)}"