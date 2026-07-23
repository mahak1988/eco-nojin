"""
Econojin Custom Exceptions
====================================
استانداردسازی خطاهای سراسری پروژه
"""

from typing import Optional, Any


class EconojinException(Exception):
    """پایه تمام استثناهای Econojin"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        detail: Optional[Any] = None,
        headers: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """تبدیل به فرمت JSON برای API response"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "detail": self.detail,
        }


# ============================================
# Client Errors (4xx)
# ============================================

class ValidationError(EconojinException):
    """خطای اعتبارسنجی داده‌ها"""
    
    def __init__(self, message: str = "Invalid input data", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            detail=detail,
        )


class NotFoundError(EconojinException):
    """منبع درخواستی یافت نشد"""
    
    def __init__(self, resource: str = "Resource", item_id: Optional[int] = None):
        message = f"{resource} not found"
        if item_id is not None:
            message = f"{resource} with id={item_id} not found"
        super().__init__(
            message=message,
            status_code=404,
        )


class UnauthorizedError(EconojinException):
    """احراز هویت ناموفق"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(EconojinException):
    """دسترسی غیرمجاز"""
    
    def __init__(self, message: str = "You do not have permission to access this resource"):
        super().__init__(
            message=message,
            status_code=403,
        )


class ConflictError(EconojinException):
    """تضاد داده‌ها (مثلاً تکراری بودن)"""
    
    def __init__(self, message: str = "Resource conflict", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=409,
            detail=detail,
        )


class TooManyRequestsError(EconojinException):
    """تعداد درخواست بیش از حد مجاز"""
    
    def __init__(self, message: str = "Too many requests"):
        super().__init__(
            message=message,
            status_code=429,
        )


# ============================================
# Server Errors (5xx)
# ============================================

class DatabaseError(EconojinException):
    """خطای پایگاه داده"""
    
    def __init__(self, message: str = "Database operation failed", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            detail=detail,
        )


class ServiceUnavailableError(EconojinException):
    """سرویس در دسترس نیست"""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            status_code=503,
        )


class InternalServerError(EconojinException):
    """خطای داخلی سرور"""
    
    def __init__(self, message: str = "Internal server error", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            detail=detail,
        )


class SimulationError(EconojinException):
    """خطا در اجرای مدل شبیه‌سازی"""
    
    def __init__(self, model_name: str, message: str = "Simulation failed"):
        super().__init__(
            message=f"{model_name}: {message}",
            status_code=500,
        )


class DataIntegrationError(EconojinException):
    """خطا در یکپارچه‌سازی داده‌ها"""
    
    def __init__(self, source: str, message: str = "Data integration failed"):
        super().__init__(
            message=f"{source}: {message}",
            status_code=500,
        )


# ============================================
# Domain-Specific Errors
# ============================================

class AgriculturalError(EconojinException):
    """خطا در ماژول کشاورزی"""
    
    def __init__(self, message: str = "Agricultural operation failed"):
        super().__init__(
            message=message,
            status_code=500,
        )


class WaterResourceError(EconojinException):
    """خطا در ماژول منابع آب"""
    
    def __init__(self, message: str = "Water resource operation failed"):
        super().__init__(
            message=message,
            status_code=500,
        )


class CarbonCycleError(EconojinException):
    """خطا در ماژول چرخه کربن"""
    
    def __init__(self, message: str = "Carbon cycle calculation failed"):
        super().__init__(
            message=message,
            status_code=500,
        )


class BiodiversityError(EconojinException):
    """خطا در ماژول تنوع زیستی"""
    
    def __init__(self, message: str = "Biodiversity assessment failed"):
        super().__init__(
            message=message,
            status_code=500,
        )


class EconomicValuationError(EconojinException):
    """خطا در ماژول ارزش‌گذاری اقتصادی"""
    
    def __init__(self, message: str = "Economic valuation failed"):
        super().__init__(
            message=message,
            status_code=500,
        )
