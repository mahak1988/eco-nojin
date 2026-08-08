import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@econojin/ui';
import { Label } from '@econojin/ui';
import { Switch } from '@econojin/ui';
import { Slider } from '@econojin/ui';
import { Input } from '@econojin/ui';
import { Button } from '@econojin/ui';
import { useTheme } from '../contexts/ThemeContext';
import ThemeSelector from '../components/ThemeSelector';
import { Palette, Monitor } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Settings() {
  const {
    themeColors,
    setCustomColors,
    toggleRTL,
    isRTL,
  } = useTheme();

  const [fontSize, setFontSize] = useState<number>(() => {
    const savedSize = localStorage.getItem('font-size');
    return savedSize ? parseInt(savedSize, 10) : 16;
  });

  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    return saved === 'true';
  });

  const [customPrimaryColor, setCustomPrimaryColor] = useState<string>(themeColors.primary || '#15803d');
  const [customSecondaryColor, setCustomSecondaryColor] = useState<string>(themeColors.secondary || '#bbf7d0');
  const [customAccentColor, setCustomAccentColor] = useState<string>(themeColors.accent || '#22c55e');

  useEffect(() => {
    document.documentElement.style.fontSize = `${fontSize}px`;
    localStorage.setItem('font-size', fontSize.toString());
  }, [fontSize]);

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', sidebarCollapsed.toString());
    if (sidebarCollapsed) {
      document.body.classList.add('sidebar-collapsed');
    } else {
      document.body.classList.remove('sidebar-collapsed');
    }
  }, [sidebarCollapsed]);

  const handleSaveCustomColors = () => {
    setCustomColors({
      primary: customPrimaryColor,
      secondary: customSecondaryColor,
      accent: customAccentColor,
    });
  };

  const resetToDefault = () => {
    setCustomColors({});
    setCustomPrimaryColor('#15803d');
    setCustomSecondaryColor('#bbf7d0');
    setCustomAccentColor('#22c55e');
    setFontSize(16);
    setSidebarCollapsed(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">تنظیمات ظاهر</h1>
        <p className="text-muted-foreground">
          تنظیم تم، زبان و سایر تنظیمات رابط کاربری
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5" />
              تنظیمات ظاهر
            </CardTitle>
            <CardDescription>
              تنظیم تم، رنگ‌ها و سایر ویژگی‌های ظاهری
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>انتخاب تم</Label>
              <ThemeSelector />
            </div>

            <div className="space-y-4">
              <Label>رنگ‌های سفارشی</Label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="primary-color">رنگ اصلی</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="primary-color"
                      type="color"
                      value={customPrimaryColor}
                      onChange={(e) => setCustomPrimaryColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      type="text"
                      value={customPrimaryColor}
                      onChange={(e) => setCustomPrimaryColor(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="secondary-color">رنگ ثانویه</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="secondary-color"
                      type="color"
                      value={customSecondaryColor}
                      onChange={(e) => setCustomSecondaryColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      type="text"
                      value={customSecondaryColor}
                      onChange={(e) => setCustomSecondaryColor(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="accent-color">رنگ لهجه</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="accent-color"
                      type="color"
                      value={customAccentColor}
                      onChange={(e) => setCustomAccentColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      type="text"
                      value={customAccentColor}
                      onChange={(e) => setCustomAccentColor(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              <Button onClick={handleSaveCustomColors} className="w-full">
                ذخیره رنگ‌های سفارشی
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Monitor className="w-5 h-5" />
              تنظیمات دسترسی‌پذیری
            </CardTitle>
            <CardDescription>
              تنظیمات مربوط به دسترسی‌پذیری و کاربرپذیری
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">چینش راست به چپ</Label>
                <p className="text-sm text-muted-foreground">
                  فعال‌سازی چینش راست به چپ برای زبان‌های فارسی/عربی
                </p>
              </div>
              <Switch
                checked={isRTL}
                onCheckedChange={toggleRTL}
                aria-label="تغییر وضعیت چینش راست به چپ"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">اندازه فونت</Label>
                  <p className="text-sm text-muted-foreground">
                    تغییر اندازه فونت پایه سیستم ({fontSize}px)
                  </p>
                </div>
              </div>
              <Slider
                defaultValue={[fontSize]}
                max={24}
                min={12}
                step={1}
                onValueChange={([value]) => setFontSize(value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>کوچک</span>
                <span>متوسط</span>
                <span>بزرگ</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">جمع شدن نوار کناری</Label>
                <p className="text-sm text-muted-foreground">
                  جمع کردن نوار کناری برای فضای بیشتر
                </p>
              </div>
              <Switch
                checked={sidebarCollapsed}
                onCheckedChange={setSidebarCollapsed}
                aria-label="تغییر وضعیت جمع شدن نوار کناری"
              />
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>بازنشانی تنظیمات</CardTitle>
            <CardDescription>
              بازنشانی تمام تنظیمات ظاهر به مقادیر پیش‌فرض
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="destructive" onClick={resetToDefault}>
              بازنشانی همه تنظیمات
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
