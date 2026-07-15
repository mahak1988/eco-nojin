from langchain_core.tools import tool
from sqlalchemy import text
from apps.shared_core.database.session import async_session_maker
import logging

logger = logging.getLogger(__name__)

@tool
async def query_database(sql_query: str) -> str:
    """
    اجرای کوئری SQL خواندنی (SELECT) در دیتابیس.
    
    Args:
        sql_query: کوئری SQL که باید با SELECT شروع شود.
    
    Returns:
        نتایج کوئری به صورت متنی.
    """
    if not sql_query.strip().upper().startswith("SELECT"):
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
    try:
        async with async_session_maker() as session:
            # کوئری برای دریافت اطلاعات جدول (SQLite-specific)
            query = f"PRAGMA table_info({table_name})"
            result = await session.execute(text(query))
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