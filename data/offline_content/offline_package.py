"""Offline Content Package Generator

این ماژول محتوای آموزشی را برای مناطق بدون اینترنت بسته‌بندی می‌کند.
"""
import json
from pathlib import Path
from typing import List, Dict


class OfflineContentPackage:
    """Offline Content Package"""
    
    def __init__(self, pilot_site: str, languages: List[str]):
        self.pilot_site = pilot_site
        self.languages = languages
        self.content = {}
    
    def add_course(self, course_id: str, course_data: Dict):
        """Add a course to offline package"""
        self.content[course_id] = course_data
    
    def generate_package(self, output_dir: Path):
        """Generate offline package"""
        package_dir = output_dir / f"{self.pilot_site}_offline"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Save content as JSON
        content_file = package_dir / "content.json"
        content_file.write_text(
            json.dumps(self.content, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        # Generate README
        readme = f"""# بسته آموزشی آفلاین - {self.pilot_site}

## زبان‌های موجود
{', '.join(self.languages)}

## نحوه استفاده
1. فایل content.json را در دستگاه خود کپی کنید
2. اپلیکیشن Econojin Offline را نصب کنید
3. محتوای آفلاین را از تنظیمات بارگذاری کنید

## دوره‌های موجود
"""
        for course_id, course_data in self.content.items():
            readme += f"- {course_data.get('title', {}).get('fa', course_id)}
"
        
        (package_dir / "README.md").write_text(readme, encoding='utf-8')
        
        return package_dir
