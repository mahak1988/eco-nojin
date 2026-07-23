from langchain_core.tools import tool
from sqlalchemy import text, select
from apps.shared_core.database.session import async_session_maker
import logging
import re

logger = logging.getLogger(__name__)

# Allowed tables whitelist for security
ALLOWED_TABLES = {
    "users", "projects", "simulations", "mrv_records", 
    "carbon_credits", "transactions", "contracts"
}

def _validate_table_name(table_name: str) -> bool:
    """Validate table name to prevent SQL injection."""
    if not table_name or not isinstance(table_name, str):
        return False
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        return False
    return True

@tool
async def query_database(sql_query: str) -> str:
    """
    اجرای کوئری SQL خواندنی (SELECT) در دیتابیس.
    
    Args:
        sql_query: کوئری SQL که باید با SELECT شروع شود.
    
    Returns:
        نتایج کوئری به صورت متنی.
    """
    if not sql_query or not sql_query.strip():
        return "❌ خطا: کوئری خالی است."
    
    query_upper = sql_query.strip().upper()
    
    # Prevent multiple statements and dangerous keywords
    if ";" in sql_query:
        return "❌ خطا: چندین دستور SQL مجاز نیست."
    
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "EXEC"]
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return f"❌ خطا: دستور {keyword} مجاز نیست."
    
    if not query_upper.startswith("SELECT"):
        return "❌ خطا: فقط کوئری‌های SELECT مجاز هستند."
    
    try:
        async with async_session_maker() as session:
            result = await session.execute(text(sql_query))
            rows = result.fetchall()
            
            if not rows:
                return "✅ کوئری اجرا شد اما نتیجه‌ای یافت نشد."
            
            # تبدیل نتایج به فرمت متنی خوانا
            columns = result.keys()
            output = [f"ستون‌ها: {', '.join(columns)}"]
            output.append(f"تعداد ردیف‌ها: {len(rows)}")
            output.append("\nداده‌ها:")
            
            for i, row in enumerate(rows[:10], 1):  # محدودیت 10 ردیف برای جلوگیری از خروجی حجیم
                output.append(f"{i}. {dict(zip(columns, row))}")
            
            if len(rows) > 10:
                output.append(f"\n... و {len(rows) - 10} ردیف دیگر")
            
            return "\n".join(output)
    
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return f"❌ خطا در اجرای کوئری: {str(e)}"

@tool
async def get_table_schema(table_name: str) -> str:
    """
    دریافت ساختار (Schema) یک جدول دیتابیس.
    
    Args:
        table_name: نام جدول
    
    Returns:
        اطلاعات ساختار جدول شامل نام ستون‌ها و انواع داده.
    """
    # Validate table name to prevent SQL injection
    if not _validate_table_name(table_name):
        return f"❌ خطا: نام جدول '{table_name}' معتبر نیست."
    
    # Check against whitelist
    if table_name.lower() not in ALLOWED_TABLES:
        return f"❌ خطا: دسترسی به جدول '{table_name}' مجاز نیست. جداول مجاز: {', '.join(ALLOWED_TABLES)}"
    
    try:
        async with async_session_maker() as session:
            # Use parameterized approach with validated table name
            # PRAGMA table_info requires literal table name, but we've validated it
            query = text(f"PRAGMA table_info(:table_name)")
            result = await session.execute(query, {"table_name": table_name})
            columns = result.fetchall()
            
            if not columns:
                return f"❌ جدول '{table_name}' یافت نشد."
            
            output = [f"📊 ساختار جدول: {table_name}\n"]
            output.append("ستون‌ها:")
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else "NULLABLE"
                primary_key = "PRIMARY KEY" if col[5] else ""
                
                output.append(f"  - {col_name}: {col_type} {not_null} {primary_key}")
            
            return "\n".join(output)
    
    except Exception as e:
        logger.error(f"Error fetching schema for {table_name}: {e}")
        return f"❌ خطا در دریافت ساختار جدول: {str(e)}"