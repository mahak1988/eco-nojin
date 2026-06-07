#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Econojin Module Generator (اصلاح‌شده)
ایجاد سریع ماژول‌های جدید - نسخه بدون خطای f-string
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web"
if not WEB.exists():
    WEB = ROOT / "web"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path.relative_to(ROOT)}")


def create_module(module_id: str, module_name: str, icon: str, description: str):
    """ایجاد کامل یک ماژول جدید - با escape صحیح برای JSX"""

    app_dir = WEB / "src" / "app" / module_id
    components_dir = WEB / "src" / "modules" / module_id

    # نکته کلیدی: در f-string، {{ و }} برای نمایش { و } در JSX استفاده می‌شود

    # ۱. صفحه اصلی ماژول
    page_content = f'''"""use client";

import {{ MainLayout }} from "@/components/layout/main-layout";
import {{ Card, CardContent, CardHeader, CardTitle }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ {icon} }} from "lucide-react";

export default function {module_name.replace(" ", "")}Page() {{
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{icon} {module_name}</h1>
            <p className="text-slate-400">{description}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">⚙️ تنظیمات</Button>
            <Button size="sm">✨ اقدام جدید</Button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-slate-400">مجموع</p>
              <p className="text-2xl font-bold">۰</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-slate-400">فعال</p>
              <p className="text-2xl font-bold">۰</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-slate-400">در انتظار</p>
              <p className="text-2xl font-bold">۰</p>
            </CardContent>
          </Card>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>📋 لیست {module_name}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-slate-500">
              <{icon} className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">هنوز داده‌ای ثبت نشده</p>
              <Button variant="outline">+ افزودن اولین مورد</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}}
'''
    write_file(app_dir / "page.tsx", page_content)

    # ۲. کامپوننت کارت ماژول
    card_content = f"""import {{ Card, CardContent, CardHeader, CardTitle }} from "@/components/ui/card";
import {{ Badge }} from "@/components/ui/badge";
import {{ {icon} }} from "lucide-react";

interface Props {{
  id: string;
  title: string;
  description: string;
  status?: "active" | "pending" | "completed";
  date: string;
}}

export function {module_name.replace(" ", "")}Card({{ id, title, description, status = "pending", date }}: Props) {{
  return (
    <Card className="card-hover cursor-pointer">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="p-2 rounded-lg bg-primary-500/10">
            <{icon} className="h-5 w-5 text-primary-400" />
          </div>
          {{status && (
            <Badge variant={{status === "active" ? "success" : status === "completed" ? "default" : "warning"}}>
              {{status === "active" ? "فعال" : status === "completed" ? "تکمیل" : "در انتظار"}}
            </Badge>
          )}}
        </div>
        <CardTitle className="mt-2 text-base">{{title}}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-400 mb-3">{{description}}</p>
        <p className="text-xs text-slate-500">{{date}}</p>
      </CardContent>
    </Card>
  );
}}
"""
    write_file(components_dir / f"{module_id}-card.tsx", card_content)

    print(f"\n🎉 ماژول '{module_name}' ایجاد شد! 🔗 http://localhost:3000/{module_id}")


def main():
    parser = argparse.ArgumentParser(description="🚀 ایجاد ماژول جدید")
    parser.add_argument("id", help="شناسه ماژول: e.g., 'inventory'")
    parser.add_argument("name", help="نام فارسی: e.g., 'انبارداری'")
    parser.add_argument("icon", help="آیکون lucide-react: e.g., 'Package'")
    parser.add_argument("desc", help="توضیح: e.g., 'مدیریت موجودی'")

    args = parser.parse_args()

    print(f"⚡ Econojin Module Generator")
    print(f"   ماژول: {{args.name}} ({{args.id}})")
    print("=" * 50)

    try:
        create_module(args.id, args.name, args.icon, args.desc)
        return 0
    except Exception as e:
        print(f"\n❌ خطا: {{e}}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
