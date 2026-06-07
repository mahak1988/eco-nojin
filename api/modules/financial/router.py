# api/modules/financial/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.financial.models import (
    Account, Transaction, Invoice, InvoiceItem,
    InventoryProduct, InventoryMovement, Budget, FinancialMetric,
    Employee, PayrollRecord, Contract, ContractItem,
    Wallet, WalletTransaction, Payment, Unit, FixedAsset,
    TransactionType, InvoiceStatus, InventoryMethod, MovementType,
    ContractStatus, ContractType, PaymentMethod, WalletTransactionType,
    EmployeeStatus
)
from api.modules.financial.calculator import FinancialCalculator



class FinancialDashboardResponse(BaseModel):
    """Auto-generated response model for /dashboard"""
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    total_employees: int = 0
    active_contracts: int = 0
    pending_invoices: int = 0


router = APIRouter(prefix="/financial", tags=["Financial Management"])


# =========================================================================
# Pydantic Models
# =========================================================================
class ProductCreate(BaseModel):
    sku: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "عدد"
    quantity: float = 0.0
    min_quantity: float = 0.0
    max_quantity: float = 0.0
    cost_price: float = 0.0
    selling_price: float = 0.0
    wholesale_price: float = 0.0
    warehouse: str = "انبار اصلی"
    location: Optional[str] = None
    shelf: Optional[str] = None
    production_date: Optional[str] = None
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_phone: Optional[str] = None
    image_url: Optional[str] = None


class MovementCreate(BaseModel):
    product_id: int
    movement_type: str
    quantity: float
    description: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None
    created_by: Optional[int] = None


class InvoiceCreate(BaseModel):
    invoice_type: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[dict]
    tax_rate: float = 9.0
    discount_rate: float = 0.0
    due_date: Optional[str] = None
    notes: Optional[str] = None


class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    national_id: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    base_salary: float = 0.0
    housing_allowance: float = 0.0
    food_allowance: float = 0.0
    child_allowance: float = 0.0


class ContractCreate(BaseModel):
    contract_type: str
    title: str
    description: Optional[str] = None
    party_a_name: Optional[str] = None
    party_b_name: Optional[str] = None
    contract_amount: float = 0.0
    tax_rate: float = 9.0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    items: List[dict] = []


class WalletDeposit(BaseModel):
    user_id: int
    amount: float
    description: Optional[str] = None


# =========================================================================
# Dashboard
# =========================================================================
@router.get("/dashboard", response_model=FinancialDashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """داشبورد مالی جامع"""
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    
    revenue = (await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.INCOME) &
            (Transaction.transaction_date >= current_month_start)
        )
    )).scalar() or 0
    
    expenses = (await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.EXPENSE) &
            (Transaction.transaction_date >= current_month_start)
        )
    )).scalar() or 0
    
    net_profit = revenue - expenses
    
    overdue = (await db.execute(
        select(func.count(Invoice.id)).where(
            (Invoice.status == InvoiceStatus.SENT) & (Invoice.due_date < datetime.now())
        )
    )).scalar() or 0
    
    low_stock = (await db.execute(
        select(func.count(InventoryProduct.id)).where(
            (InventoryProduct.quantity <= InventoryProduct.min_quantity) &
            (InventoryProduct.is_active == True)
        )
    )).scalar() or 0
    
    inventory_value = (await db.execute(
        select(func.sum(InventoryProduct.quantity * InventoryProduct.cost_price))
    )).scalar() or 0
    
    total_products = (await db.execute(
        select(func.count(InventoryProduct.id)).where(InventoryProduct.is_active == True)
    )).scalar() or 0
    
    today = datetime.now().replace(hour=0, minute=0, second=0)
    
    today_in = (await db.execute(
        select(func.sum(InventoryMovement.quantity)).where(
            (InventoryMovement.movement_type == MovementType.IN) &
            (InventoryMovement.movement_date >= today)
        )
    )).scalar() or 0
    
    today_out = (await db.execute(
        select(func.sum(InventoryMovement.quantity)).where(
            (InventoryMovement.movement_type == MovementType.OUT) &
            (InventoryMovement.movement_date >= today)
        )
    )).scalar() or 0
    
    wallet_balance = (await db.execute(select(func.sum(Wallet.balance)))).scalar() or 0
    active_contracts = (await db.execute(
        select(func.count(Contract.id)).where(Contract.status == ContractStatus.ACTIVE)
    )).scalar() or 0
    active_employees = (await db.execute(
        select(func.count(Employee.id)).where(Employee.status == EmployeeStatus.ACTIVE)
    )).scalar() or 0
    monthly_payroll = (await db.execute(
        select(func.sum(PayrollRecord.net_salary)).where(
            (PayrollRecord.year == datetime.now().year) & (PayrollRecord.month == datetime.now().month)
        )
    )).scalar() or 0
    
    return {
        "monthly_revenue": revenue,
        "monthly_expenses": expenses,
        "net_profit": net_profit,
        "profit_margin": FinancialCalculator.net_margin(net_profit, revenue) if revenue > 0 else 0,
        "overdue_invoices": overdue,
        "low_stock_products": low_stock,
        "inventory_value": inventory_value,
        "total_products": total_products,
        "today_in": today_in,
        "today_out": today_out,
        "total_wallet_balance": wallet_balance,
        "active_contracts": active_contracts,
        "active_employees": active_employees,
        "monthly_payroll": monthly_payroll,
    }


# =========================================================================
# Units
# =========================================================================
@router.get("/units", response_model=Dict[str, Any])
async def list_units(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Unit).where(Unit.is_active == True))
    return {"units": [{"id": u.id, "code": u.code, "name": u.name, "category": u.category} for u in result.scalars().all()]}


@router.post("/units", response_model=Dict[str, Any])
async def create_unit(data: dict, db: AsyncSession = Depends(get_db)):
    unit = Unit(**data)
    db.add(unit)
    await db.commit()
    return {"id": unit.id, "status": "created"}


# =========================================================================
# Employees & Payroll
# =========================================================================
@router.get("/employees", response_model=IDResponse)
async def list_employees(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee))
    return {
        "employees": [
            {
                "id": e.id, "employee_code": e.employee_code, "full_name": e.full_name,
                "position": e.position, "department": e.department,
                "base_salary": e.base_salary, "status": e.status.value,
            }
            for e in result.scalars().all()
        ]
    }


@router.post("/employees", response_model=Dict[str, Any])
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    employee = Employee(**data.dict())
    db.add(employee)
    await db.commit()
    return {"id": employee.id, "status": "created"}


@router.put("/employees/{employee_id}", response_model=IDResponse)
async def update_employee(employee_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee: raise HTTPException(404, "کارمند یافت نشد")
    for k, v in data.items():
        if hasattr(employee, k): setattr(employee, k, v)
    await db.commit()
    return {"status": "updated"}


@router.delete("/employees/{employee_id}", response_model=SuccessResponse)
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee: raise HTTPException(404, "کارمند یافت نشد")
    employee.status = EmployeeStatus.TERMINATED
    await db.commit()
    return {"status": "terminated"}


@router.post("/payroll/calculate", response_model=Dict[str, Any])
async def calculate_payroll(employee_id: int, year: int, month: int, overtime_hours: float = 0, bonuses: float = 0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee: raise HTTPException(404, "کارمند یافت نشد")
    
    calc = FinancialCalculator.calculate_payroll(
        base_salary=employee.base_salary,
        housing_allowance=employee.housing_allowance,
        food_allowance=employee.food_allowance,
        child_allowance=employee.child_allowance,
        overtime_hours=overtime_hours,
        hourly_rate=employee.base_salary / 220 if employee.base_salary else 0,
        bonuses=bonuses, year=year,
    )
    
    record = PayrollRecord(
        employee_id=employee_id, year=year, month=month,
        base_salary=calc["base_salary"], overtime_hours=overtime_hours,
        overtime_pay=calc["overtime_pay"], bonuses=bonuses,
        allowances_total=calc["allowances"]["total"],
        gross_salary=calc["gross_salary"],
        insurance_employee=calc["deductions"]["insurance_employee"],
        insurance_employer=calc["deductions"]["insurance_employer"],
        tax_amount=calc["deductions"]["tax"],
        total_deductions=calc["deductions"]["total"],
        net_salary=calc["net_salary"],
    )
    db.add(record)
    await db.commit()
    return {"status": "calculated", "payroll": calc, "record_id": record.id}


@router.get("/payroll/{employee_id}", response_model=Dict[str, Any])
async def get_payroll_history(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PayrollRecord).where(PayrollRecord.employee_id == employee_id).order_by(desc(PayrollRecord.year))
    )
    return {
        "records": [
            {"id": r.id, "year": r.year, "month": r.month, "gross_salary": r.gross_salary, "net_salary": r.net_salary, "status": r.status}
            for r in result.scalars().all()
        ]
    }


# =========================================================================
# Contracts
# =========================================================================
@router.get("/contracts", response_model=Dict[str, Any])
async def list_contracts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contract).order_by(desc(Contract.created_at)))
    return {
        "contracts": [
            {
                "id": c.id, "contract_number": c.contract_number, "contract_type": c.contract_type.value,
                "title": c.title, "status": c.status.value, "contract_amount": c.contract_amount,
                "total_amount": c.total_amount, "paid_amount": c.paid_amount,
                "start_date": c.start_date, "end_date": c.end_date,
            }
            for c in result.scalars().all()
        ]
    }


@router.post("/contracts", response_model=Dict[str, Any])
async def create_contract(data: ContractCreate, db: AsyncSession = Depends(get_db)):
    contract_number = f"CON-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    tax_amount = data.contract_amount * (data.tax_rate / 100)
    total_amount = data.contract_amount + tax_amount
    
    contract = Contract(
        contract_number=contract_number, contract_type=ContractType(data.contract_type),
        title=data.title, description=data.description,
        party_a_name=data.party_a_name, party_b_name=data.party_b_name,
        contract_amount=data.contract_amount, tax_rate=data.tax_rate,
        tax_amount=tax_amount, total_amount=total_amount, remaining_amount=total_amount,
        start_date=date.fromisoformat(data.start_date) if data.start_date else None,
        end_date=date.fromisoformat(data.end_date) if data.end_date else None,
    )
    db.add(contract)
    await db.flush()
    
    for item_data in data.items:
        item = ContractItem(
            contract_id=contract.id, description=item_data["description"],
            quantity=item_data.get("quantity", 1), unit_price=item_data.get("unit_price", 0),
            total_price=item_data.get("quantity", 1) * item_data.get("unit_price", 0),
        )
        db.add(item)
    
    await db.commit()
    return {"id": contract.id, "contract_number": contract_number, "status": "created"}


@router.put("/contracts/{contract_id}", response_model=IDResponse)
async def update_contract(contract_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract: raise HTTPException(404, "قرارداد یافت نشد")
    for k, v in data.items():
        if hasattr(contract, k): setattr(contract, k, v)
    await db.commit()
    return {"status": "updated"}


@router.delete("/contracts/{contract_id}", response_model=SuccessResponse)
async def delete_contract(contract_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract: raise HTTPException(404, "قرارداد یافت نشد")
    contract.status = ContractStatus.TERMINATED
    await db.commit()
    return {"status": "terminated"}


# =========================================================================
# Wallet
# =========================================================================
@router.get("/wallet/{user_id}", response_model=Dict[str, Any])
async def get_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        await db.commit()
    return {"user_id": user_id, "balance": wallet.balance, "currency": wallet.currency}


@router.post("/wallet/deposit", response_model=Dict[str, Any])
async def deposit_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=data.user_id, balance=0.0)
        db.add(wallet)
        await db.flush()
    
    balance_before = wallet.balance
    wallet.balance += data.amount
    
    tx = WalletTransaction(
        wallet_id=wallet.id, transaction_type=WalletTransactionType.DEPOSIT,
        amount=data.amount, balance_before=balance_before, balance_after=wallet.balance,
        description=data.description or "شارژ کیف پول",
        reference_number=f"DEP-{int(datetime.now().timestamp())}",
    )
    db.add(tx)
    await db.commit()
    return {"status": "success", "new_balance": wallet.balance}


@router.post("/wallet/withdraw", response_model=Dict[str, Any])
async def withdraw_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet or wallet.balance < data.amount:
        raise HTTPException(400, "موجودی کافی نیست")
    
    balance_before = wallet.balance
    wallet.balance -= data.amount
    
    tx = WalletTransaction(
        wallet_id=wallet.id, transaction_type=WalletTransactionType.WITHDRAWAL,
        amount=data.amount, balance_before=balance_before, balance_after=wallet.balance,
        description=data.description or "برداشت",
    )
    db.add(tx)
    await db.commit()
    return {"status": "success", "new_balance": wallet.balance}


@router.get("/wallet/{user_id}/transactions", response_model=Dict[str, Any])
async def get_wallet_transactions(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet: return {"transactions": []}
    
    tx_result = await db.execute(
        select(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id).order_by(desc(WalletTransaction.created_at))
    )
    return {
        "transactions": [
            {"id": t.id, "type": t.transaction_type.value, "amount": t.amount, "balance_after": t.balance_after, "description": t.description, "created_at": t.created_at}
            for t in tx_result.scalars().all()
        ]
    }


# =========================================================================
# Inventory (CRUD کامل)
# =========================================================================
@router.get("/inventory", response_model=Dict[str, Any])
async def list_inventory(category: Optional[str] = None, low_stock_only: bool = False, search: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(InventoryProduct).where(InventoryProduct.is_active == True)
    if category: query = query.where(InventoryProduct.category == category)
    if low_stock_only: query = query.where(InventoryProduct.quantity <= InventoryProduct.min_quantity)
    if search: query = query.where((InventoryProduct.name.ilike(f"%{search}%")) | (InventoryProduct.sku.ilike(f"%{search}%")))
    
    result = await db.execute(query.order_by(InventoryProduct.name))
    products = result.scalars().all()
    
    alerts = [
        {"product_id": p.id, "product_name": p.name, "sku": p.sku, "current": p.quantity, "min": p.min_quantity, "level": "critical" if p.quantity == 0 else "warning"}
        for p in products if p.quantity <= p.min_quantity
    ]
    
    return {
        "products": [
            {
                "id": p.id, "sku": p.sku, "name": p.name, "name_en": p.name_en, "description": p.description,
                "category": p.category, "unit": p.unit, "quantity": p.quantity,
                "min_quantity": p.min_quantity, "max_quantity": p.max_quantity,
                "cost_price": p.cost_price, "selling_price": p.selling_price, "wholesale_price": p.wholesale_price,
                "warehouse": p.warehouse, "location": p.location, "shelf": p.shelf,
                "production_date": p.production_date, "expiry_date": p.expiry_date, "batch_number": p.batch_number,
                "supplier_name": p.supplier_name, "supplier_phone": p.supplier_phone, "image_url": p.image_url,
                "total_value": p.quantity * p.cost_price, "is_low_stock": p.quantity <= p.min_quantity,
            }
            for p in products
        ],
        "total_value": sum(p.quantity * p.cost_price for p in products),
        "total_products": len(products),
        "low_stock_count": sum(1 for p in products if p.quantity <= p.min_quantity),
        "alerts": alerts,
    }


@router.post("/inventory", response_model=Dict[str, Any])
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(InventoryProduct).where(InventoryProduct.sku == data.sku))
    if existing.scalar_one_or_none(): raise HTTPException(400, "SKU تکراری است")
    
    product = InventoryProduct(
        **data.dict(),
        production_date=date.fromisoformat(data.production_date) if data.production_date else None,
        expiry_date=date.fromisoformat(data.expiry_date) if data.expiry_date else None,
    )
    db.add(product)
    await db.commit()
    return {"id": product.id, "sku": product.sku, "status": "created"}


@router.get("/inventory/{product_id}", response_model=IDResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")
    
    movements_result = await db.execute(
        select(InventoryMovement).where(InventoryMovement.product_id == product_id).order_by(desc(InventoryMovement.movement_date)).limit(20)
    )
    
    return {
        "product": {
            "id": product.id, "sku": product.sku, "name": product.name, "category": product.category,
            "unit": product.unit, "quantity": product.quantity, "min_quantity": product.min_quantity,
            "cost_price": product.cost_price, "selling_price": product.selling_price,
            "warehouse": product.warehouse, "location": product.location,
            "supplier_name": product.supplier_name, "expiry_date": product.expiry_date,
            "total_value": product.quantity * product.cost_price, "is_low_stock": product.quantity <= product.min_quantity,
        },
        "movements": [
            {"id": m.id, "movement_type": m.movement_type.value, "quantity": m.quantity, "quantity_before": m.quantity_before, "quantity_after": m.quantity_after, "description": m.description, "movement_date": m.movement_date}
            for m in movements_result.scalars().all()
        ],
    }


@router.put("/inventory/{product_id}", response_model=Dict[str, Any])
async def update_product(product_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")
    for k, v in data.items():
        if hasattr(product, k):
            if k in ["production_date", "expiry_date"] and v: v = date.fromisoformat(v)
            setattr(product, k, v)
    await db.commit()
    return {"status": "updated"}


@router.delete("/inventory/{product_id}", response_model=SuccessResponse)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")
    product.is_active = False
    await db.commit()
    return {"status": "deleted"}


@router.post("/inventory/movements", response_model=Dict[str, Any])
async def create_movement(data: MovementCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == data.product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")
    
    quantity_before = product.quantity
    
    if data.movement_type == "in": product.quantity += data.quantity
    elif data.movement_type == "out":
        if product.quantity < data.quantity: raise HTTPException(400, "موجودی کافی نیست")
        product.quantity -= data.quantity
    elif data.movement_type == "adjustment": product.quantity = data.quantity
    elif data.movement_type == "return": product.quantity += data.quantity
    
    movement = InventoryMovement(
        product_id=data.product_id, movement_type=MovementType(data.movement_type),
        quantity=data.quantity, quantity_before=quantity_before, quantity_after=product.quantity,
        description=data.description, notes=data.notes, reference_number=data.reference_number,
        created_by=data.created_by,
    )
    db.add(movement)
    await db.commit()
    
    return {"status": "success", "quantity_before": quantity_before, "quantity_after": product.quantity}


@router.get("/inventory/movements/history", response_model=IDResponse)
async def get_movements_history(product_id: Optional[int] = None, limit: int = Query(50, le=200), db: AsyncSession = Depends(get_db)):
    query = select(InventoryMovement)
    if product_id: query = query.where(InventoryMovement.product_id == product_id)
    query = query.order_by(desc(InventoryMovement.movement_date)).limit(limit)
    
    result = await db.execute(query)
    return {
        "movements": [
            {"id": m.id, "product_id": m.product_id, "movement_type": m.movement_type.value, "quantity": m.quantity, "description": m.description, "movement_date": m.movement_date}
            for m in result.scalars().all()
        ]
    }


# =========================================================================
# Invoices
# =========================================================================
@router.get("/invoices", response_model=Dict[str, Any])
async def list_invoices(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Invoice)
    if status: query = query.where(Invoice.status == InvoiceStatus(status))
    result = await db.execute(query.order_by(desc(Invoice.issue_date)))
    return {
        "invoices": [
            {
                "id": inv.id, "invoice_number": inv.invoice_number, "invoice_type": inv.invoice_type,
                "status": inv.status.value, "customer_name": inv.customer_name,
                "total_amount": inv.total_amount, "paid_amount": inv.paid_amount,
                "remaining_amount": inv.remaining_amount, "issue_date": inv.issue_date, "due_date": inv.due_date,
            }
            for inv in result.scalars().all()
        ]
    }


@router.post("/invoices", response_model=Dict[str, Any])
async def create_invoice(data: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    calculation = FinancialCalculator.calculate_invoice(data.items, data.tax_rate, data.discount_rate)
    
    invoice = Invoice(
        invoice_number=invoice_number, invoice_type=data.invoice_type, status=InvoiceStatus.DRAFT,
        customer_name=data.customer_name, customer_email=data.customer_email, customer_phone=data.customer_phone,
        subtotal=calculation["subtotal"], tax_rate=data.tax_rate, tax_amount=calculation["tax_amount"],
        discount_rate=data.discount_rate, discount_amount=calculation["discount_amount"],
        total_amount=calculation["total_amount"], remaining_amount=calculation["total_amount"],
        due_date=datetime.fromisoformat(data.due_date) if data.due_date else None, notes=data.notes,
    )
    db.add(invoice)
    await db.flush()
    
    for item_data in data.items:
        item = InvoiceItem(
            invoice_id=invoice.id, product_id=item_data.get("product_id"),
            product_name=item_data["product_name"], quantity=item_data["quantity"],
            unit_price=item_data["unit_price"], discount=item_data.get("discount", 0),
            tax_rate=item_data.get("tax_rate", data.tax_rate),
            total_price=item_data["quantity"] * item_data["unit_price"],
        )
        db.add(item)
    
    await db.commit()
    return {"id": invoice.id, "invoice_number": invoice_number, "total_amount": calculation["total_amount"]}


@router.put("/invoices/{invoice_id}", response_model=IDResponse)
async def update_invoice(invoice_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice: raise HTTPException(404, "فاکتور یافت نشد")
    for k, v in data.items():
        if hasattr(invoice, k): setattr(invoice, k, v)
    await db.commit()
    return {"status": "updated"}


@router.delete("/invoices/{invoice_id}", response_model=SuccessResponse)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice: raise HTTPException(404, "فاکتور یافت نشد")
    invoice.status = InvoiceStatus.CANCELLED
    await db.commit()
    return {"status": "cancelled"}


# =========================================================================
# Financial Calculators
# =========================================================================
@router.post("/calculate/npv", response_model=Dict[str, Any])
async def calculate_npv(cash_flows: List[float], discount_rate: float):
    npv = FinancialCalculator.npv(cash_flows, discount_rate / 100)
    return {"npv": round(npv, 2), "recommendation": "پذیرش" if npv > 0 else "رد"}


@router.post("/calculate/irr", response_model=Dict[str, Any])
async def calculate_irr(cash_flows: List[float]):
    irr = FinancialCalculator.irr(cash_flows)
    return {"irr": round(irr * 100, 2) if irr else None}


@router.post("/calculate/break-even", response_model=Dict[str, Any])
async def calculate_break_even(fixed_costs: float, price: float, variable_cost: float):
    return FinancialCalculator.break_even_point(fixed_costs, price, variable_cost)


@router.post("/calculate/eoq", response_model=Dict[str, Any])
async def calculate_eoq(annual_demand: float, ordering_cost: float, holding_cost: float):
    return {"eoq": round(FinancialCalculator.eoq(annual_demand, ordering_cost, holding_cost), 2)}


@router.post("/calculate/loan", response_model=Dict[str, Any])
async def calculate_loan(principal: float, annual_rate: float, years: int):
    payment = FinancialCalculator.loan_payment(principal, annual_rate, years)
    schedule = FinancialCalculator.loan_amortization_schedule(principal, annual_rate, years)
    return {
        "monthly_payment": round(payment, 2),
        "total_payment": round(payment * years * 12, 2),
        "total_interest": round(payment * years * 12 - principal, 2),
        "schedule": schedule[:12],
    }


@router.post("/calculate/payroll", response_model=Dict[str, Any])
async def calculate_payroll_api(base_salary: float, housing: float = 0, food: float = 0, child: float = 0, overtime_hours: float = 0, bonuses: float = 0):
    return FinancialCalculator.calculate_payroll(
        base_salary=base_salary, housing_allowance=housing, food_allowance=food,
        child_allowance=child, overtime_hours=overtime_hours, hourly_rate=base_salary / 220, bonuses=bonuses,
    )


@router.post("/calculate/depreciation", response_model=Dict[str, Any])
async def calculate_depreciation(cost: float, salvage: float, years: int, method: str = "straight_line"):
    if method == "straight_line":
        return {"method": method, "annual": round(FinancialCalculator.straight_line_depreciation(cost, salvage, years), 2)}
    elif method == "declining_balance":
        return {"method": method, "schedule": FinancialCalculator.declining_balance_depreciation(cost, salvage, years)}
    elif method == "sum_of_years":
        return {"method": method, "schedule": FinancialCalculator.sum_of_years_depreciation(cost, salvage, years)}
    raise HTTPException(400, "روش نامعتبر")


@router.post("/calculate/wacc", response_model=Dict[str, Any])
async def calculate_wacc(equity: float, debt: float, cost_equity: float, cost_debt: float, tax_rate: float):
    return {"wacc": round(FinancialCalculator.wacc(equity, debt, cost_equity, cost_debt, tax_rate), 2)}


@router.post("/calculate/capm", response_model=Dict[str, Any])
async def calculate_capm(risk_free: float, beta: float, market_return: float):
    return {"expected_return": round(FinancialCalculator.capm(risk_free, beta, market_return), 2)}


@router.post("/calculate/ratios", response_model=Dict[str, Any])
async def calculate_ratios(financial_data: dict):
    return FinancialCalculator.comprehensive_analysis(financial_data)


# =========================================================================
# Reports
# =========================================================================
@router.get("/reports/profit-loss", response_model=Dict[str, Any])
async def profit_loss_report(start_date: str, end_date: str, db: AsyncSession = Depends(get_db)):
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    revenue = (await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.INCOME) & (Transaction.transaction_date.between(start, end))
        )
    )).scalar() or 0
    
    expenses = (await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.EXPENSE) & (Transaction.transaction_date.between(start, end))
        )
    )).scalar() or 0
    
    return {
        "period": {"start": start_date, "end": end_date},
        "revenue": revenue, "expenses": expenses,
        "net_profit": revenue - expenses,
        "profit_margin": FinancialCalculator.net_margin(revenue - expenses, revenue) if revenue > 0 else 0,
    }
