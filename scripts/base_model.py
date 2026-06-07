"""
مدل پایه - نسخه امن
استفاده از SafeModuleLoader به جای exec
"""
import sys
from pathlib import Path

# افزودن مسیر scripts به path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.safety import SafeModuleLoader


def load_model_class(module_name: str, class_name: str):
    """
    بارگذاری امن کلاس مدل

    Args:
        module_name: نام ماژول (مثلاً 'scripts.models.soil_carbon.rothc')
        class_name: نام کلاس (مثلاً 'RothCModel')

    Returns:
        کلاس درخواستی
    """
    return SafeModuleLoader.load_class(module_name, class_name)


class BaseModel:
    """کلاس پایه برای همه مدل‌ها"""

    def __init__(self, **kwargs):
        self.config = kwargs

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")
