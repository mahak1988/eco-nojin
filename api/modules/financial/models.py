# api/modules/financial/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


# =========================================================================
# Enums
# =========================================================================
class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    SALARY = "salary"


class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InventoryMethod(enum.Enum):
    FIFO = "fifo"
    LIFO = "lifo"
    AVERAGE = "average"


class MovementType(enum.Enum):
    IN = "in"
    OUT = "out"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class ContractStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class ContractType(enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"
    SERVICE = "service"
    EMPLOYMENT = "employment"
    LEASE = "lease"


class PaymentMethod(enum.Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    CHECK = "check"


class WalletTransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"


class EmployeeStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class DepreciationMethod(enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    SUM_OF_YEARS = "sum_of_years"


# =========================================================================
# Units
# =========================================================================
class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    category = Column(String(50))
    conversion_factor = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)


# =========================================================================
# Employees & Payroll
# =========================================================================
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    national_id = Column(String(20))
    position = Column(String(200))
    department = Column(String(200))
    employment_date = Column(Date)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    base_salary = Column(Float, default=0.0)
    housing_allowance = Column(Float, default=0.0)
    food_allowance = Column(Float, default=0.0)
    child_allowance = Column(Float, default=0.0)
    bank_name = Column(String(100))
    bank_account = Column(String(50))
    insurance_number = Column(String(50))
    insurance_rate = Column(Float, default=7.0)
    created_at = Column(DateTime, server_default=func.now())
    payroll_records = relationship("PayrollRecord", back_populates="employee")


class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    base_salary = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    overtime_pay = Column(Float, default=0.0)
    bonuses = Column(Float, default=0.0)
    allowances_total = Column(Float, default=0.0)
    gross_salary = Column(Float, default=0.0)
    insurance_employee = Column(Float, default=0.0)
    insurance_employer = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    net_salary = Column(Float, default=0.0)
    status = Column(String(50), default="calculated")
    payment_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    employee = relationship("Employee", back_populates="payroll_records")


# =========================================================================
# Contracts
# =========================================================================
class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False)
    contract_type = Column(SQLEnum(ContractType), nullable=False)
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    party_a_name = Column(String(200))
    party_b_name = Column(String(200))
    contract_amount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)
    terms_and_conditions = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    items = relationship("ContractItem", back_populates="contract", cascade="all, delete-orphan")


class ContractItem(Base):
    __tablename__ = "contract_items"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    contract = relationship("Contract", back_populates="items")


# =========================================================================
# Wallet & Payments
# =========================================================================
class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String(10), default="IRR")
    is_frozen = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    transaction_type = Column(SQLEnum(WalletTransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_before = Column(Float)
    balance_after = Column(Float)
    description = Column(String(500))
    reference_number = Column(String(100))
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, server_default=func.now())
    wallet = relationship("Wallet", back_populates="transactions")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    fee_amount = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    status = Column(String(50), default="pending")
    reference_code = Column(String(100))
    tracking_code = Column(String(100))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    description = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)


# =========================================================================
# Financial Accounts & Transactions
# =========================================================================
class Account(Base):
    __tablename__ = "financial_accounts"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    account_type = Column(String(50))
    parent_id = Column(Integer, ForeignKey("financial_accounts.id"))
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "financial_transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    reference_number = Column(String(100))
    transaction_date = Column(DateTime, server_default=func.now())
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    created_at = Column(DateTime, server_default=func.now())
    account = relationship("Account", back_populates="transactions")
    invoice = relationship("Invoice", back_populates="transactions")


# =========================================================================
# Invoices
# =========================================================================
class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_type = Column(String(20))
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    customer_id = Column(Integer, ForeignKey("users.id"))
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    customer_address = Column(Text)
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)
    tax_amount = Column(Float, default=0.0)
    discount_rate = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    issue_date = Column(DateTime, server_default=func.now())
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    payment_method = Column(SQLEnum(PaymentMethod))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("inventory_products.id"))
    product_name = Column(String(200), nullable=False)
    description = Column(Text)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)
    total_price = Column(Float, nullable=False)
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("InventoryProduct")


# =========================================================================
# Inventory (با فیلدهای کامل)
# =========================================================================
class InventoryProduct(Base):
    __tablename__ = "inventory_products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    description = Column(Text)
    category = Column(String(100))
    unit = Column(String(50), default="عدد")
    quantity = Column(Float, default=0.0)
    min_quantity = Column(Float, default=0.0)
    max_quantity = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    wholesale_price = Column(Float, default=0.0)
    valuation_method = Column(SQLEnum(InventoryMethod), default=InventoryMethod.AVERAGE)
    warehouse = Column(String(100), default="انبار اصلی")
    location = Column(String(100))
    shelf = Column(String(50))
    production_date = Column(Date)
    expiry_date = Column(Date)
    batch_number = Column(String(50))
    supplier_name = Column(String(200))
    supplier_phone = Column(String(50))
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_low_stock = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    movements = relationship("InventoryMovement", back_populates="product")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_products.id"), nullable=False)
    movement_type = Column(SQLEnum(MovementType), nullable=False)
    quantity = Column(Float, nullable=False)
    quantity_before = Column(Float)
    quantity_after = Column(Float)
    reference_type = Column(String(50))
    reference_number = Column(String(100))
    description = Column(Text)
    notes = Column(Text)
    movement_date = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    product = relationship("InventoryProduct", back_populates="movements")


# =========================================================================
# Budget & Metrics
# =========================================================================
class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer)
    budgeted_amount = Column(Float, nullable=False)
    actual_amount = Column(Float, default=0.0)
    variance = Column(Float, default=0.0)
    category = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    category = Column(String(100))
    formula = Column(Text)
    current_value = Column(Float)
    target_value = Column(Float)
    calculation_date = Column(DateTime, server_default=func.now())


# =========================================================================
# Fixed Assets
# =========================================================================
class FixedAsset(Base):
    __tablename__ = "fixed_assets"
    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    purchase_date = Column(Date)
    purchase_cost = Column(Float, nullable=False)
    salvage_value = Column(Float, default=0.0)
    useful_life_years = Column(Integer, nullable=False)
    depreciation_method = Column(SQLEnum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)
    accumulated_depreciation = Column(Float, default=0.0)
    book_value = Column(Float, default=0.0)
    location = Column(String(200))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, server_default=func.now())
