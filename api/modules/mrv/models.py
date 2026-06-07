# api/modules/mrv/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from api.core.database import Base


class CarbonProject(Base):
    """پروژه‌های جذب کربن"""
    __tablename__ = "carbon_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(2000))
    project_type = Column(String(50))  # reforestation, soil_carbon, agroforestry
    location_name = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    area_hectares = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # پارامترهای خاک
    soil_type = Column(String(50))  # clay, loam, sandy
    initial_soc = Column(Float)  # SOC اولیه (t/ha)
    clay_content = Column(Float)  # درصد رس
    pH = Column(Float)
    
    # پارامترهای اقلیمی
    annual_rainfall = Column(Float)  # mm
    mean_temperature = Column(Float)  # °C
    
    # وضعیت
    status = Column(String(20), default="active")  # active, completed, paused
    verification_status = Column(String(20), default="pending")  # pending, verified, rejected
    
    # نتایج
    total_carbon_sequestered = Column(Float, default=0)  # tCO₂e
    annual_carbon_rate = Column(Float, default=0)  # tCO₂e/سال
    eco_coins_generated = Column(Float, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class CarbonMeasurement(Base):
    """اندازه‌گیری‌های دوره‌ای کربن"""
    __tablename__ = "carbon_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"))
    
    measurement_date = Column(DateTime, nullable=False)
    measurement_method = Column(String(50))  # rothc_model, field_sample, remote_sensing
    
    # نتایج اندازه‌گیری
    soc_ton_per_hectare = Column(Float)  # تن کربن در هکتار
    biomass_ton_per_hectare = Column(Float)
    total_tco2e = Column(Float)
    
    # عدم قطعیت
    uncertainty_percent = Column(Float, default=10)
    confidence_level = Column(Float, default=0.95)
    
    # داده‌های ورودی
    input_data = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())


class FinancialAnalysis(Base):
    """تحلیل‌های مالی پروژه"""
    __tablename__ = "financial_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"))
    
    analysis_date = Column(DateTime, server_default=func.now())
    
    # پارامترهای مالی
    initial_investment = Column(Float)  # سرمایه‌گذاری اولیه
    annual_maintenance_cost = Column(Float)  # هزینه نگهداری سالانه
    carbon_price_per_ton = Column(Float)  # قیمت هر تن کربن ($)
    discount_rate = Column(Float, default=0.08)  # نرخ تنزیل
    project_lifetime_years = Column(Integer, default=30)
    
    # نتایج
    npv = Column(Float)  # ارزش فعلی خالص
    irr = Column(Float)  # نرخ بازده داخلی
    payback_period_years = Column(Float)  # دوره بازگشت
    total_revenue = Column(Float)
    total_cost = Column(Float)
    net_profit = Column(Float)
    
    # جریان نقدی سالانه
    cash_flows = Column(JSON)


class EcoCoinTransaction(Base):
    """تراکنش‌های EcoCoin"""
    __tablename__ = "ecocoin_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))
    project_id = Column(Integer, ForeignKey("carbon_projects.id"), nullable=True)
    
    transaction_type = Column(String(20))  # earn, spend, transfer, convert
    amount = Column(Float)  # مقدار EcoCoin
    balance_after = Column(Float)
    
    description = Column(String(500))
    reference_id = Column(String(100))  # ارتباط با پروژه یا تراکنش دیگر
    
    created_at = Column(DateTime, server_default=func.now())


class AuditReport(Base):
    """گزارش‌های ممیزی"""
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"))
    
    report_date = Column(DateTime, server_default=func.now())
    report_type = Column(String(50))  # annual, verification, baseline
    
    # محتوا
    report_data = Column(JSON)
    pdf_url = Column(String(500))
    
    # امنیت
    sha256_hash = Column(String(64))  # هش SHA-256
    blockchain_tx_id = Column(String(100))  # شناسه تراکنش بلاکچین
    
    # وضعیت
    auditor_name = Column(String(200))
    verification_status = Column(String(20), default="pending")
    
    created_at = Column(DateTime, server_default=func.now())
