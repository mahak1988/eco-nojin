# api/modules/financial/calculator.py
"""
موتور محاسبات مالی پیشرفته
شامل تمام فرمول‌های استاندارد حسابداری، مالی، بانکی و اقتصادی
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
import math


class FinancialCalculator:
    """ماشین حساب مالی پیشرفته"""

    # =========================================================================
    # شاخص‌های سودآوری (Profitability Ratios)
    # =========================================================================

    @staticmethod
    def gross_margin(revenue: float, cogs: float) -> float:
        """حاشیه سود ناخالص"""
        if revenue == 0: return 0
        return ((revenue - cogs) / revenue) * 100

    @staticmethod
    def net_margin(net_income: float, revenue: float) -> float:
        """حاشیه سود خالص"""
        if revenue == 0: return 0
        return (net_income / revenue) * 100

    @staticmethod
    def operating_margin(operating_income: float, revenue: float) -> float:
        """حاشیه سود عملیاتی"""
        if revenue == 0: return 0
        return (operating_income / revenue) * 100

    @staticmethod
    def roa(net_income: float, total_assets: float) -> float:
        """بازگشت دارایی‌ها (ROA)"""
        if total_assets == 0: return 0
        return (net_income / total_assets) * 100

    @staticmethod
    def roe(net_income: float, equity: float) -> float:
        """بازگشت حقوق صاحبان سهام (ROE)"""
        if equity == 0: return 0
        return (net_income / equity) * 100

    @staticmethod
    def roic(nopat: float, invested_capital: float) -> float:
        """بازگشت سرمایه سرمایه‌گذاری‌شده (ROIC)"""
        if invested_capital == 0: return 0
        return (nopat / invested_capital) * 100

    @staticmethod
    def dupont_analysis(net_income: float, revenue: float, total_assets: float, equity: float) -> Dict:
        """تحلیل دوپونت"""
        net_margin = (net_income / revenue * 100) if revenue else 0
        asset_turnover = (revenue / total_assets) if total_assets else 0
        equity_multiplier = (total_assets / equity) if equity else 0
        roe = net_margin * asset_turnover * equity_multiplier / 100

        return {
            "net_margin": round(net_margin, 2),
            "asset_turnover": round(asset_turnover, 2),
            "equity_multiplier": round(equity_multiplier, 2),
            "roe": round(roe, 2),
        }

    # =========================================================================
    # شاخص‌های نقدینگی (Liquidity Ratios)
    # =========================================================================

    @staticmethod
    def current_ratio(current_assets: float, current_liabilities: float) -> float:
        """نسبت جاری"""
        if current_liabilities == 0: return 0
        return current_assets / current_liabilities

    @staticmethod
    def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
        """نسبت آنی"""
        if current_liabilities == 0: return 0
        return (current_assets - inventory) / current_liabilities

    @staticmethod
    def cash_ratio(cash: float, current_liabilities: float) -> float:
        """نسبت وجه نقد"""
        if current_liabilities == 0: return 0
        return cash / current_liabilities

    @staticmethod
    def working_capital(current_assets: float, current_liabilities: float) -> float:
        """سرمایه در گردش"""
        return current_assets - current_liabilities

    # =========================================================================
    # شاخص‌های اهرمی (Leverage Ratios)
    # =========================================================================

    @staticmethod
    def debt_to_equity(total_debt: float, equity: float) -> float:
        """نسبت بدهی به حقوق"""
        if equity == 0: return 0
        return total_debt / equity

    @staticmethod
    def debt_to_assets(total_debt: float, total_assets: float) -> float:
        """نسبت بدهی به دارایی"""
        if total_assets == 0: return 0
        return total_debt / total_assets

    @staticmethod
    def interest_coverage(ebit: float, interest_expense: float) -> float:
        """نسبت پوشش بهره"""
        if interest_expense == 0: return 0
        return ebit / interest_expense

    @staticmethod
    def equity_multiplier(total_assets: float, equity: float) -> float:
        """ضریب فزاینده حقوق"""
        if equity == 0: return 0
        return total_assets / equity

    # =========================================================================
    # شاخص‌های کارایی (Efficiency Ratios)
    # =========================================================================

    @staticmethod
    def inventory_turnover(cogs: float, avg_inventory: float) -> float:
        """گردش موجودی"""
        if avg_inventory == 0: return 0
        return cogs / avg_inventory

    @staticmethod
    def days_sales_outstanding(ar: float, revenue: float, days: int = 365) -> float:
        """دوره وصول مطالبات"""
        if revenue == 0: return 0
        return (ar / revenue) * days

    @staticmethod
    def days_payable_outstanding(ap: float, cogs: float, days: int = 365) -> float:
        """دوره پرداخت بدهی‌ها"""
        if cogs == 0: return 0
        return (ap / cogs) * days

    @staticmethod
    def days_inventory_outstanding(cogs: float, avg_inventory: float, days: int = 365) -> float:
        """دوره گردش موجودی"""
        if cogs == 0: return 0
        return (avg_inventory / cogs) * days

    @staticmethod
    def cash_conversion_cycle(dso: float, dio: float, dpo: float) -> float:
        """چرخه تبدیل وجه نقد"""
        return dso + dio - dpo

    @staticmethod
    def asset_turnover(revenue: float, total_assets: float) -> float:
        """گردش دارایی‌ها"""
        if total_assets == 0: return 0
        return revenue / total_assets

    # =========================================================================
    # شاخص‌های سرمایه‌گذاری (Investment Ratios)
    # =========================================================================

    @staticmethod
    def npv(cash_flows: List[float], discount_rate: float) -> float:
        """ارزش فعلی خالص (NPV)"""
        return sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows))

    @staticmethod
    def irr(cash_flows: List[float], max_iterations: int = 100) -> Optional[float]:
        """نرخ بازگشت داخلی (IRR)"""
        guess = 0.1
        for _ in range(max_iterations):
            npv = sum(cf / ((1 + guess) ** t) for t, cf in enumerate(cash_flows))
            derivative = sum(-t * cf / ((1 + guess) ** (t + 1)) for t, cf in enumerate(cash_flows))
            if abs(derivative) < 1e-10: break
            new_guess = guess - npv / derivative
            if abs(new_guess - guess) < 1e-6: return new_guess
            guess = new_guess
        return None

    @staticmethod
    def payback_period(cash_flows: List[float]) -> Optional[float]:
        """دوره بازگشت سرمایه"""
        cumulative = 0
        for t, cf in enumerate(cash_flows):
            cumulative += cf
            if cumulative >= 0:
                return t + (cumulative - cf) / abs(cf) if cf != 0 else t
        return None

    @staticmethod
    def discounted_payback(cash_flows: List[float], discount_rate: float) -> Optional[float]:
        """دوره بازگشت تنزیل‌شده"""
        discounted = [cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows)]
        return FinancialCalculator.payback_period(discounted)

    @staticmethod
    def roi(net_profit: float, investment: float) -> float:
        """نرخ بازگشت سرمایه"""
        if investment == 0: return 0
        return (net_profit / investment) * 100

    @staticmethod
    def profitability_index(npv: float, initial_investment: float) -> float:
        """شاخص سودآوری"""
        if initial_investment == 0: return 0
        return (npv + initial_investment) / initial_investment

    # =========================================================================
    # مدل‌های بانکی و وام (Banking & Loans)
    # =========================================================================

    @staticmethod
    def loan_payment(principal: float, annual_rate: float, years: int, payments_per_year: int = 12) -> float:
        """قسط وام (فرمول استاندارد)"""
        r = annual_rate / 100 / payments_per_year
        n = years * payments_per_year
        if r == 0: return principal / n
        return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    @staticmethod
    def loan_amortization_schedule(principal: float, annual_rate: float, years: int) -> List[Dict]:
        """جدول استهلاک وام"""
        schedule = []
        monthly_rate = annual_rate / 100 / 12
        months = years * 12
        payment = FinancialCalculator.loan_payment(principal, annual_rate, years)

        balance = principal
        for month in range(1, months + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest
            balance -= principal_paid

            schedule.append({
                "month": month,
                "payment": round(payment, 2),
                "principal": round(principal_paid, 2),
                "interest": round(interest, 2),
                "balance": round(max(0, balance), 2),
            })

        return schedule

    @staticmethod
    def effective_annual_rate(nominal_rate: float, compounding_periods: int) -> float:
        """نرخ مؤثر سالانه"""
        return ((1 + nominal_rate / 100 / compounding_periods) ** compounding_periods - 1) * 100

    # =========================================================================
    # استهلاک دارایی ثابت (Depreciation)
    # =========================================================================

    @staticmethod
    def straight_line_depreciation(cost: float, salvage: float, years: int) -> float:
        """استهلاک خط مستقیم"""
        if years == 0: return 0
        return (cost - salvage) / years

    @staticmethod
    def declining_balance_depreciation(cost: float, salvage: float, years: int, rate: float = 2.0) -> List[Dict]:
        """استهلاک نزولی"""
        schedule = []
        book_value = cost
        annual_rate = rate / years

        for year in range(1, years + 1):
            depreciation = book_value * annual_rate
            if book_value - depreciation < salvage:
                depreciation = book_value - salvage
            book_value -= depreciation
            schedule.append({
                "year": year,
                "depreciation": round(depreciation, 2),
                "book_value": round(book_value, 2),
            })

        return schedule

    @staticmethod
    def sum_of_years_depreciation(cost: float, salvage: float, years: int) -> List[Dict]:
        """استهلاک مجموع سنوات"""
        schedule = []
        sum_of_years = years * (years + 1) / 2
        depreciable = cost - salvage

        for year in range(1, years + 1):
            fraction = (years - year + 1) / sum_of_years
            depreciation = depreciable * fraction
            schedule.append({
                "year": year,
                "depreciation": round(depreciation, 2),
                "fraction": round(fraction, 4),
            })

        return schedule

    # =========================================================================
    # حقوق و دستمزد (Payroll)
    # =========================================================================

    @staticmethod
    def calculate_iranian_tax(annual_income: float, year: int = 1403) -> float:
        """محاسبه مالیات بر حقوق ایران (پلکانی)"""
        # نرخ‌های 1403 (تومان)
        brackets = [
            (120_000_000, 0.0),       # معاف
            (168_000_000, 0.10),      # 10%
            (276_000_000, 0.15),      # 15%
            (408_000_000, 0.20),      # 20%
            (float("inf"), 0.30),     # 30%
        ]

        tax = 0
        prev_limit = 0

        for limit, rate in brackets:
            if annual_income <= limit:
                tax += (annual_income - prev_limit) * rate
                break
            else:
                tax += (limit - prev_limit) * rate
                prev_limit = limit

        return tax

    @staticmethod
    def calculate_payroll(
        base_salary: float,
        housing_allowance: float = 0,
        food_allowance: float = 0,
        child_allowance: float = 0,
        overtime_hours: float = 0,
        hourly_rate: float = 0,
        bonuses: float = 0,
        insurance_rate_employee: float = 7.0,
        insurance_rate_employer: float = 23.0,
        year: int = 1403
    ) -> Dict:
        """محاسبه کامل حقوق و دستمزد"""
        # مزایا
        allowances = housing_allowance + food_allowance + child_allowance
        overtime_pay = overtime_hours * hourly_rate
        gross_salary = base_salary + allowances + overtime_pay + bonuses

        # بیمه
        insurance_employee = gross_salary * (insurance_rate_employee / 100)
        insurance_employer = gross_salary * (insurance_rate_employer / 100)

        # مالیات (سالانه / 12)
        annual_income = gross_salary * 12
        annual_tax = FinancialCalculator.calculate_iranian_tax(annual_income, year)
        monthly_tax = annual_tax / 12

        # کسورات
        total_deductions = insurance_employee + monthly_tax
        net_salary = gross_salary - total_deductions

        return {
            "base_salary": round(base_salary, 2),
            "allowances": {
                "housing": round(housing_allowance, 2),
                "food": round(food_allowance, 2),
                "child": round(child_allowance, 2),
                "total": round(allowances, 2),
            },
            "overtime_pay": round(overtime_pay, 2),
            "bonuses": round(bonuses, 2),
            "gross_salary": round(gross_salary, 2),
            "deductions": {
                "insurance_employee": round(insurance_employee, 2),
                "insurance_employer": round(insurance_employer, 2),
                "tax": round(monthly_tax, 2),
                "total": round(total_deductions, 2),
            },
            "net_salary": round(net_salary, 2),
        }

    # =========================================================================
    # انبارداری (Inventory)
    # =========================================================================

    @staticmethod
    def eoq(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
        """مقدار اقتصادی سفارش (EOQ)"""
        if holding_cost == 0: return 0
        return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

    @staticmethod
    def reorder_point(daily_demand: float, lead_time: float, safety_stock: float = 0) -> float:
        """نقطه سفارش"""
        return (daily_demand * lead_time) + safety_stock

    @staticmethod
    def safety_stock(daily_demand: float, lead_time: float, service_level: float = 0.95) -> float:
        """ذخیره احتیاطی"""
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z = z_scores.get(service_level, 1.65)
        return z * daily_demand * math.sqrt(lead_time)

    @staticmethod
    def inventory_recommendations(
        current_stock: float,
        min_stock: float,
        max_stock: float,
        reorder_point: float,
        daily_demand: float,
        lead_time: float
    ) -> List[Dict]:
        """توصیه‌های هوشمند انبارداری"""
        recommendations = []

        days_of_stock = current_stock / daily_demand if daily_demand > 0 else 0

        if current_stock <= min_stock:
            recommendations.append({
                "level": "critical",
                "title": "موجودی بحرانی",
                "message": f"موجودی به حداقل رسیده. سفارش فوری {reorder_point} واحد توصیه می‌شود.",
                "action": "order_now",
                "quantity": reorder_point,
            })
        elif current_stock <= reorder_point:
            recommendations.append({
                "level": "warning",
                "title": "نقطه سفارش",
                "message": f"موجودی به نقطه سفارش رسیده. زمان سفارش‌گذاری است.",
                "action": "order_soon",
                "quantity": reorder_point,
            })
        elif days_of_stock > 90:
            recommendations.append({
                "level": "info",
                "title": "موجودی بیش از حد",
                "message": f"موجودی برای {days_of_stock:.0f} روز کافی است. کاهش سفارش توصیه می‌شود.",
                "action": "reduce_order",
            })

        if current_stock >= max_stock:
            recommendations.append({
                "level": "warning",
                "title": "تکمیل ظرفیت",
                "message": "انبار در حداکثر ظرفیت. از سفارش جدید خودداری کنید.",
                "action": "stop_order",
            })

        return recommendations

    @staticmethod
    def abc_analysis(products: List[Dict]) -> Dict:
        """تحلیل ABC موجودی"""
        sorted_products = sorted(products, key=lambda x: x.get("annual_value", 0), reverse=True)
        total_value = sum(p.get("annual_value", 0) for p in sorted_products)

        a_items, b_items, c_items = [], [], []
        cumulative = 0

        for product in sorted_products:
            cumulative += product.get("annual_value", 0)
            percentage = (cumulative / total_value * 100) if total_value > 0 else 0

            if percentage <= 80:
                a_items.append(product)
            elif percentage <= 95:
                b_items.append(product)
            else:
                c_items.append(product)

        return {
            "a_items": {"count": len(a_items), "value_percent": 80, "items": a_items},
            "b_items": {"count": len(b_items), "value_percent": 15, "items": b_items},
            "c_items": {"count": len(c_items), "value_percent": 5, "items": c_items},
        }

    # =========================================================================
    # تحلیل هزینه-فایده (CBA)
    # =========================================================================

    @staticmethod
    def cost_benefit_analysis(
        initial_investment: float,
        annual_benefits: List[float],
        annual_costs: List[float],
        discount_rate: float,
        years: int
    ) -> Dict:
        """تحلیل هزینه-فایده"""
        benefits_pv = sum(b / ((1 + discount_rate) ** t) for t, b in enumerate(annual_benefits))
        costs_pv = initial_investment + sum(c / ((1 + discount_rate) ** t) for t, c in enumerate(annual_costs))

        npv = benefits_pv - costs_pv
        bcr = benefits_pv / costs_pv if costs_pv > 0 else 0

        return {
            "npv": round(npv, 2),
            "bcr": round(bcr, 2),
            "benefits_pv": round(benefits_pv, 2),
            "costs_pv": round(costs_pv, 2),
            "recommendation": "پذیرش" if npv > 0 and bcr > 1 else "رد",
        }

    # =========================================================================
    # محاسبات فاکتور
    # =========================================================================

    @staticmethod
    def calculate_invoice(items: List[Dict], tax_rate: float = 9.0, discount_rate: float = 0.0) -> Dict:
        """محاسبه فاکتور"""
        subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
        discount_amount = subtotal * (discount_rate / 100)
        subtotal_after_discount = subtotal - discount_amount
        tax_amount = subtotal_after_discount * (tax_rate / 100)
        total_amount = subtotal_after_discount + tax_amount

        return {
            "subtotal": round(subtotal, 2),
            "discount_rate": discount_rate,
            "discount_amount": round(discount_amount, 2),
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total_amount": round(total_amount, 2),
        }

    # =========================================================================
    # تحلیل نقطه سربه‌سر
    # =========================================================================

    @staticmethod
    def break_even_point(fixed_costs: float, price: float, variable_cost: float) -> Dict:
        """نقطه سربه‌سر"""
        contribution = price - variable_cost
        if contribution == 0:
            return {"units": 0, "revenue": 0, "contribution_margin": 0}

        units = fixed_costs / contribution
        revenue = units * price
        cm_ratio = (contribution / price * 100) if price else 0

        return {
            "units": round(units, 2),
            "revenue": round(revenue, 2),
            "contribution_margin": round(contribution, 2),
            "contribution_margin_ratio": round(cm_ratio, 2),
        }

    # =========================================================================
    # WACC & CAPM
    # =========================================================================

    @staticmethod
    def wacc(
        equity: float, debt: float,
        cost_of_equity: float, cost_of_debt: float,
        tax_rate: float
    ) -> float:
        """میانگین موزون هزینه سرمایه (WACC)"""
        total = equity + debt
        if total == 0: return 0
        we = equity / total
        wd = debt / total
        return (we * cost_of_equity + wd * cost_of_debt * (1 - tax_rate / 100))

    @staticmethod
    def capm(risk_free_rate: float, beta: float, market_return: float) -> float:
        """مدل قیمت‌گذاری دارایی سرمایه‌ای (CAPM)"""
        return risk_free_rate + beta * (market_return - risk_free_rate)

    # =========================================================================
    # شاخص‌های بورسی
    # =========================================================================

    @staticmethod
    def pe_ratio(price: float, eps: float) -> float:
        """نسبت قیمت به سود"""
        if eps == 0: return 0
        return price / eps

    @staticmethod
    def pb_ratio(price: float, book_value_per_share: float) -> float:
        """نسبت قیمت به ارزش دفتری"""
        if book_value_per_share == 0: return 0
        return price / book_value_per_share

    @staticmethod
    def dividend_yield(dividend_per_share: float, price: float) -> float:
        """بازده سود سهام"""
        if price == 0: return 0
        return (dividend_per_share / price) * 100

    @staticmethod
    def eps(net_income: float, preferred_dividends: float, shares_outstanding: float) -> float:
        """سود هر سهم"""
        if shares_outstanding == 0: return 0
        return (net_income - preferred_dividends) / shares_outstanding

    # =========================================================================
    # تحلیل جامع
    # =========================================================================

    @classmethod
    def comprehensive_analysis(cls, data: Dict) -> Dict:
        """تحلیل جامع مالی"""
        results = {}

        if all(k in data for k in ["revenue", "cogs", "net_income"]):
            results["profitability"] = {
                "gross_margin": cls.gross_margin(data["revenue"], data["cogs"]),
                "net_margin": cls.net_margin(data["net_income"], data["revenue"]),
                "roa": cls.roa(data["net_income"], data.get("total_assets", 0)),
                "roe": cls.roe(data["net_income"], data.get("equity", 0)),
            }

        if all(k in data for k in ["current_assets", "current_liabilities"]):
            results["liquidity"] = {
                "current_ratio": cls.current_ratio(data["current_assets"], data["current_liabilities"]),
                "quick_ratio": cls.quick_ratio(data["current_assets"], data.get("inventory", 0), data["current_liabilities"]),
                "working_capital": cls.working_capital(data["current_assets"], data["current_liabilities"]),
            }

        if all(k in data for k in ["total_debt", "equity"]):
            results["leverage"] = {
                "debt_to_equity": cls.debt_to_equity(data["total_debt"], data["equity"]),
                "debt_to_assets": cls.debt_to_assets(data["total_debt"], data.get("total_assets", 0)),
            }

        return results
