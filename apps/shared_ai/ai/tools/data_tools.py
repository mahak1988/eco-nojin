from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import logging
import json
import base64
import io
import os

logger = logging.getLogger(__name__)

# ==========================================
# Statistical Analysis Tool
# ==========================================
@tool
async def analyze_statistics(data_json: str, operations: str = "all") -> str:
    """
    انجام محاسبات آماری روی مجموعه داده.
    
    Args:
        data_json: داده‌ها به صورت JSON (لیستی از اعداد یا دیکشنری با ستون‌های عددی)
        operations: عملیات مورد نظر (all, mean, median, std, min, max, variance, percentiles)
    
    Returns:
        نتایج محاسبات آماری
    
    مثال data_json:
        {"values": [10, 20, 30, 40, 50]}
        یا
        {"column1": [1,2,3], "column2": [4,5,6]}
    """
    logger.info(f"📊 Analyzing statistics with operations: {operations}")
    
    try:
        import numpy as np
        
        data = json.loads(data_json)
        
        # اگر داده لیست ساده است
        if isinstance(data, list):
            values = np.array(data, dtype=float)
            return _compute_stats(values, "data", operations)
        
        # اگر دیکشنری با چند ستون است
        if isinstance(data, dict):
            results = []
            for col_name, col_values in data.items():
                if isinstance(col_values, list):
                    values = np.array(col_values, dtype=float)
                    stats = _compute_stats(values, col_name, operations)
                    results.append(stats)
            return "\n\n".join(results)
        
        return "❌ فرمت داده نامعتبر است."
    
    except ImportError:
        return "❌ کتابخانه numpy نصب نیست. دستور: pip install numpy"
    except json.JSONDecodeError:
        return "❌ JSON نامعتبر است."
    except Exception as e:
        logger.error(f"❌ Statistics error: {e}")
        return f"❌ خطا در تحلیل آماری: {str(e)}"

def _compute_stats(values, name: str, operations: str) -> str:
    """محاسبه آمار برای یک ستون."""
    import numpy as np
    
    results = [f"📊 آمار برای: {name}"]
    results.append(f"   تعداد: {len(values)}")
    
    if operations in ["all", "mean"]:
        results.append(f"   میانگین: {np.mean(values):.4f}")
    if operations in ["all", "median"]:
        results.append(f"   میانه: {np.median(values):.4f}")
    if operations in ["all", "std"]:
        results.append(f"   انحراف معیار: {np.std(values):.4f}")
    if operations in ["all", "variance"]:
        results.append(f"   واریانس: {np.var(values):.4f}")
    if operations in ["all", "min"]:
        results.append(f"   حداقل: {np.min(values):.4f}")
    if operations in ["all", "max"]:
        results.append(f"   حداکثر: {np.max(values):.4f}")
    if operations in ["all", "percentiles"]:
        results.append(f"   چارک اول (Q1): {np.percentile(values, 25):.4f}")
        results.append(f"   چارک سوم (Q3): {np.percentile(values, 75):.4f}")
        results.append(f"   IQR: {np.percentile(values, 75) - np.percentile(values, 25):.4f}")
    
    return "\n".join(results)

# ==========================================
# Correlation Analysis Tool
# ==========================================
@tool
async def correlation_analysis(data_json: str, method: str = "pearson") -> str:
    """
    تحلیل همبستگی بین متغیرها.
    
    Args:
        data_json: داده‌ها به صورت JSON (دیکشنری با حداقل 2 ستون عددی)
        method: روش همبستگی (pearson, spearman, kendall)
    
    Returns:
        ماتریس همبستگی و تحلیل
    """
    logger.info(f"🔗 Computing {method} correlation")
    
    try:
        import numpy as np
        
        data = json.loads(data_json)
        
        if not isinstance(data, dict) or len(data) < 2:
            return "❌ نیاز به حداقل 2 ستون عددی برای تحلیل همبستگی است."
        
        columns = list(data.keys())
        matrix = []
        
        for col in columns:
            if isinstance(data[col], list):
                matrix.append(data[col])
        
        if len(matrix) < 2:
            return "❌ حداقل 2 ستون عددی معتبر نیاز است."
        
        matrix = np.array(matrix, dtype=float)
        
        # محاسبه ماتریس همبستگی
        if method == "pearson":
            corr_matrix = np.corrcoef(matrix)
        elif method == "spearman":
            from scipy.stats import spearmanr
            corr_matrix = spearmanr(matrix.T).correlation
        else:
            return f"❌ روش {method} پشتیبانی نمی‌شود."
        
        # تولید خروجی
        output = [f"🔗 ماتریس همبستگی ({method}):\n"]
        output.append("ستون‌ها: " + ", ".join(columns))
        output.append("")
        
        # نمایش ماتریس
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                corr = corr_matrix[i, j]
                if i <= j:  # فقط مثلث بالا
                    strength = _correlation_strength(corr)
                    output.append(f"   {col1} ↔ {col2}: {corr:.4f} ({strength})")
        
        # شناسایی قوی‌ترین همبستگی‌ها
        output.append("\n🎯 قوی‌ترین همبستگی‌ها:")
        pairs = []
        for i in range(len(columns)):
            for j in range(i+1, len(columns)):
                pairs.append((columns[i], columns[j], abs(corr_matrix[i, j])))
        
        pairs.sort(key=lambda x: x[2], reverse=True)
        for col1, col2, strength in pairs[:3]:
            output.append(f"   - {col1} و {col2}: {strength:.4f}")
        
        return "\n".join(output)
    
    except ImportError:
        return "❌ کتابخانه numpy/scipy نصب نیست."
    except Exception as e:
        logger.error(f"❌ Correlation error: {e}")
        return f"❌ خطا در تحلیل همبستگی: {str(e)}"

def _correlation_strength(corr: float) -> str:
    """تعیین قدرت همبستگی."""
    abs_corr = abs(corr)
    if abs_corr >= 0.8:
        return "خیلی قوی"
    elif abs_corr >= 0.6:
        return "قوی"
    elif abs_corr >= 0.4:
        return "متوسط"
    elif abs_corr >= 0.2:
        return "ضعیف"
    else:
        return "بسیار ضعیف/بدون همبستگی"

# ==========================================
# Hypothesis Testing Tool
# ==========================================
@tool
async def hypothesis_test(data_json: str, test_type: str = "ttest") -> str:
    """
    انجام آزمون فرضیه‌های آماری.
    
    Args:
        data_json: داده‌ها به صورت JSON
        test_type: نوع آزمون (ttest, chi2, anova, normality)
    
    Returns:
        نتایج آزمون فرضیه
    """
    logger.info(f"🧪 Performing {test_type} test")
    
    try:
        import numpy as np
        from scipy import stats
        
        data = json.loads(data_json)
        
        if test_type == "ttest":
            # t-test برای مقایسه دو گروه
            if isinstance(data, dict) and len(data) >= 2:
                keys = list(data.keys())
                group1 = np.array(data[keys[0]], dtype=float)
                group2 = np.array(data[keys[1]], dtype=float)
                
                t_stat, p_value = stats.ttest_ind(group1, group2)
                
                output = [
                    "🧪 آزمون t-test (مقایسه دو گروه):",
                    f"   گروه 1 ({keys[0]}): میانگین = {np.mean(group1):.4f}, n = {len(group1)}",
                    f"   گروه 2 ({keys[1]}): میانگین = {np.mean(group2):.4f}, n = {len(group2)}",
                    f"   آماره t: {t_stat:.4f}",
                    f"   p-value: {p_value:.6f}",
                    "",
                    "📊 نتیجه:",
                ]
                
                if p_value < 0.01:
                    output.append("   ✅ تفاوت بسیار معنادار (p < 0.01)")
                elif p_value < 0.05:
                    output.append("   ✅ تفاوت معنادار (p < 0.05)")
                else:
                    output.append("   ❌ تفاوت معنادار نیست (p >= 0.05)")
                
                return "\n".join(output)
            else:
                return "❌ برای t-test نیاز به دو گروه داده است."
        
        elif test_type == "normality":
            # آزمون نرمال بودن
            if isinstance(data, dict):
                key = list(data.keys())[0]
                values = np.array(data[key], dtype=float)
            elif isinstance(data, list):
                values = np.array(data, dtype=float)
            else:
                return "❌ فرمت داده نامعتبر."
            
            stat, p_value = stats.shapiro(values)
            
            output = [
                "🧪 آزمون Shapiro-Wilk (نرمال بودن):",
                f"   تعداد نمونه: {len(values)}",
                f"   آماره W: {stat:.4f}",
                f"   p-value: {p_value:.6f}",
                "",
                "📊 نتیجه:",
            ]
            
            if p_value > 0.05:
                output.append("   ✅ داده‌ها توزیع نرمال دارند (p > 0.05)")
            else:
                output.append("   ❌ داده‌ها توزیع نرمال ندارند (p <= 0.05)")
            
            return "\n".join(output)
        
        elif test_type == "anova":
            # ANOVA برای مقایسه چند گروه
            if isinstance(data, dict) and len(data) >= 2:
                groups = [np.array(data[k], dtype=float) for k in data.keys()]
                f_stat, p_value = stats.f_oneway(*groups)
                
                output = [
                    "🧪 آزمون ANOVA (مقایسه چند گروه):",
                    f"   تعداد گروه‌ها: {len(groups)}",
                    f"   آماره F: {f_stat:.4f}",
                    f"   p-value: {p_value:.6f}",
                    "",
                    "📊 نتیجه:",
                ]
                
                if p_value < 0.05:
                    output.append("   ✅ تفاوت معنادار بین گروه‌ها وجود دارد")
                else:
                    output.append("   ❌ تفاوت معنادار بین گروه‌ها نیست")
                
                return "\n".join(output)
            else:
                return "❌ برای ANOVA نیاز به حداقل 2 گروه است."
        
        else:
            return f"❌ نوع آزمون {test_type} پشتیبانی نمی‌شود. گزینه‌ها: ttest, normality, anova"
    
    except ImportError:
        return "❌ کتابخانه scipy نصب نیست. دستور: pip install scipy"
    except Exception as e:
        logger.error(f"❌ Hypothesis test error: {e}")
        return f"❌ خطا در آزمون فرضیه: {str(e)}"

# ==========================================
# Trend Analysis Tool
# ==========================================
@tool
async def trend_analysis(data_json: str) -> str:
    """
    شناسایی روندها در داده‌های سری زمانی.
    
    Args:
        data_json: داده‌ها به صورت JSON (لیست اعداد یا دیکشنری با ستون value)
    
    Returns:
        تحلیل روند (صعودی، نزولی، ثابت)
    """
    logger.info("📈 Analyzing trends")
    
    try:
        import numpy as np
        
        data = json.loads(data_json)
        
        # استخراج داده‌ها
        if isinstance(data, list):
            values = np.array(data, dtype=float)
        elif isinstance(data, dict):
            # پیدا کردن ستون عددی
            for key, val in data.items():
                if isinstance(val, list):
                    values = np.array(val, dtype=float)
                    break
            else:
                return "❌ هیچ ستون عددی یافت نشد."
        else:
            return "❌ فرمت داده نامعتبر."
        
        if len(values) < 3:
            return "❌ حداقل 3 نقطه داده برای تحلیل روند نیاز است."
        
        # رگرسیون خطی ساده
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # محاسبه R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # تحلیل روند
        output = ["📈 تحلیل روند:\n"]
        output.append(f"   تعداد نقاط: {len(values)}")
        output.append(f"   شیب خط روند: {slope:.4f}")
        output.append(f"   R-squared: {r_squared:.4f}")
        output.append("")
        
        # تعیین نوع روند
        if abs(slope) < 0.01 * np.std(values):
            trend = "ثابت"
            emoji = "➡️"
        elif slope > 0:
            trend = "صعودی"
            emoji = "📈"
        else:
            trend = "نزولی"
            emoji = "📉"
        
        output.append(f"   {emoji} روند: {trend}")
        
        # قدرت روند
        if r_squared > 0.8:
            output.append("   💪 قدرت روند: قوی")
        elif r_squared > 0.5:
            output.append("   💪 قدرت روند: متوسط")
        else:
            output.append("   💪 قدرت روند: ضعیف")
        
        # پیش‌بینی ساده
        next_value = slope * len(values) + intercept
        output.append(f"\n🔮 پیش‌بینی مقدار بعدی: {next_value:.4f}")
        
        return "\n".join(output)
    
    except ImportError:
        return "❌ کتابخانه numpy نصب نیست."
    except Exception as e:
        logger.error(f"❌ Trend analysis error: {e}")
        return f"❌ خطا در تحلیل روند: {str(e)}"

# ==========================================
# Chart Generation Tool
# ==========================================
@tool
async def generate_chart(data_json: str, chart_type: str = "line", title: str = "نمودار") -> str:
    """
    تولید نمودار از داده‌ها.
    
    Args:
        data_json: داده‌ها به صورت JSON
        chart_type: نوع نمودار (line, bar, scatter, histogram, pie)
        title: عنوان نمودار
    
    Returns:
        مسیر فایل نمودار یا base64
    """
    logger.info(f"📊 Generating {chart_type} chart")
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
        
        data = json.loads(data_json)
        
        # ایجاد figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == "line":
            if isinstance(data, list):
                ax.plot(data, marker='o', linewidth=2, markersize=4)
            elif isinstance(data, dict):
                for key, values in data.items():
                    if isinstance(values, list):
                        ax.plot(values, marker='o', linewidth=2, label=key)
                ax.legend()
        
        elif chart_type == "bar":
            if isinstance(data, dict):
                keys = list(data.keys())
                values = [np.mean(data[k]) if isinstance(data[k], list) else data[k] for k in keys]
                ax.bar(keys, values, color='skyblue', edgecolor='black')
            else:
                return "❌ نمودار میله‌ای نیاز به دیکشنری دارد."
        
        elif chart_type == "scatter":
            if isinstance(data, dict) and len(data) >= 2:
                keys = list(data.keys())
                x = np.array(data[keys[0]], dtype=float)
                y = np.array(data[keys[1]], dtype=float)
                ax.scatter(x, y, alpha=0.7, s=50)
                ax.set_xlabel(keys[0])
                ax.set_ylabel(keys[1])
            else:
                return "❌ نمودار scatter نیاز به 2 ستون دارد."
        
        elif chart_type == "histogram":
            if isinstance(data, list):
                values = np.array(data, dtype=float)
            elif isinstance(data, dict):
                key = list(data.keys())[0]
                values = np.array(data[key], dtype=float)
            else:
                return "❌ فرمت داده نامعتبر."
            
            ax.hist(values, bins=20, color='skyblue', edgecolor='black')
        
        elif chart_type == "pie":
            if isinstance(data, dict):
                keys = list(data.keys())
                values = [np.sum(data[k]) if isinstance(data[k], list) else data[k] for k in keys]
                ax.pie(values, labels=keys, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
            else:
                return "❌ نمودار دایره‌ای نیاز به دیکشنری دارد."
        
        else:
            return f"❌ نوع نمودار {chart_type} پشتیبانی نمی‌شود."
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # ذخیره به صورت base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        # همچنین ذخیره در فایل
        output_dir = Path("apps/ai_agents/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import time
        filename = f"chart_{int(time.time())}.png"
        filepath = output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(img_base64))
        
        output = [
            f"📊 نمودار {chart_type} تولید شد:",
            f"   📁 مسیر فایل: {filepath}",
            f"   📏 اندازه: {os.path.getsize(filepath)} bytes",
            "",
            "💡 می‌توانید فایل را در مرورگر باز کنید یا در گزارش استفاده کنید."
        ]
        
        return "\n".join(output)
    
    except ImportError as e:
        return f"❌ کتابخانه matplotlib نصب نیست. دستور: pip install matplotlib\nخطا: {e}"
    except Exception as e:
        logger.error(f"❌ Chart generation error: {e}")
        return f"❌ خطا در تولید نمودار: {str(e)}"

# ==========================================
# Data Summary Tool
# ==========================================
@tool
async def data_summary(data_json: str) -> str:
    """
    خلاصه کامل و سریع از داده‌ها.
    
    Args:
        data_json: داده‌ها به صورت JSON
    
    Returns:
        خلاصه جامع داده‌ها
    """
    logger.info("📋 Generating data summary")
    
    try:
        import numpy as np
        
        data = json.loads(data_json)
        
        output = ["📋 خلاصه داده‌ها:\n"]
        
        if isinstance(data, list):
            values = np.array(data, dtype=float)
            output.append(f"📊 نوع: لیست عددی")
            output.append(f"📏 تعداد: {len(values)}")
            output.append(f"📈 میانگین: {np.mean(values):.4f}")
            output.append(f"📉 انحراف معیار: {np.std(values):.4f}")
            output.append(f"⬇️ حداقل: {np.min(values):.4f}")
            output.append(f"⬆️ حداکثر: {np.max(values):.4f}")
            output.append(f"🎯 میانه: {np.median(values):.4f}")
        
        elif isinstance(data, dict):
            output.append(f"📊 نوع: دیکشنری با {len(data)} ستون\n")
            
            for col_name, col_values in data.items():
                if isinstance(col_values, list):
                    values = np.array(col_values, dtype=float)
                    output.append(f"🔹 ستون: {col_name}")
                    output.append(f"   تعداد: {len(values)}")
                    output.append(f"   میانگین: {np.mean(values):.4f}")
                    output.append(f"   انحراف معیار: {np.std(values):.4f}")
                    output.append(f"   محدوده: [{np.min(values):.4f}, {np.max(values):.4f}]")
                    output.append("")
        
        return "\n".join(output)
    
    except ImportError:
        return "❌ کتابخانه numpy نصب نیست."
    except Exception as e:
        logger.error(f"❌ Data summary error: {e}")
        return f"❌ خطا در خلاصه داده: {str(e)}"