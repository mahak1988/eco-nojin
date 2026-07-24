// apps/web/src/pages/EcoCoinDashboard.tsx
import { useState, useEffect } from "react";
import { Coins, Leaf, Activity, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CONTRACTS } from "@/lib/contracts";

// داده‌های Mock برای شبیه‌سازی ارتباط MRV و EcoCoin
// (در آینده این داده‌ها از API بک‌اند که به قرارداد MRV متصل است، خوانده می‌شوند)
const MOCK_MRV_STATS = {
  verifiedCarbonTons: 1250.5,
  pendingVerifications: 3,
  totalEcoCoinMinted: 125050, // فرض: هر تن کربن = ۱۰۰ اکو کوین
  activeProjects: 12,
};

export default function EcoCoinDashboard() {
  const [balance, setBalance] = useState<string>("0.00");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // شبیه‌سازی فراخوانی قرارداد هوشمند یا API
    const fetchBalance = async () => {
      setIsLoading(true);
      // در اینجا در آینده از wagmi/viem برای خواندن balanceOf استفاده می‌کنیم
      // const { data } = useReadContract({ address: CONTRACTS.EcoCoin, abi: ECOCOIN_ABI, functionName: 'balanceOf', args: [userAddress] })
      
      setTimeout(() => {
        setBalance("12,450.00"); // مقدار Mock
        setIsLoading(false);
      }, 800);
    };

    fetchBalance();
  }, []);

  return (
    <div className="p-6 space-y-6 bg-stone-50 dark:bg-stone-950 min-h-screen">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-stone-800 dark:text-stone-100">
          داشبورد اکو نوژین (EcoCoin)
        </h1>
        <div className="text-sm text-stone-500">
          قرارداد فعال: <span className="font-mono text-emerald-600">{CONTRACTS.EcoCoin.slice(0, 6)}...{CONTRACTS.EcoCoin.slice(-4)}</span>
        </div>
      </div>

      {/* بخش ۱: آمار کلیدی مالی و زیست‌محیطی (ادغام EcoCoin + MRV) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-emerald-200 bg-emerald-50/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-emerald-800">موجودی EcoCoin</CardTitle>
            <Coins className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-900">
              {isLoading ? "..." : balance}
            </div>
            <p className="text-xs text-emerald-600 mt-1">معادل {MOCK_MRV_STATS.verifiedCarbonTons} تن کربن تأییدشده</p>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-blue-800">کربن تأییدشده (MRV)</CardTitle>
            <Leaf className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900">
              {MOCK_MRV_STATS.verifiedCarbonTons} <span className="text-sm font-normal">تن</span>
            </div>
            <p className="text-xs text-blue-600 mt-1">تبدیل خودکار به توکن</p>
          </CardContent>
        </Card>

        <Card className="border-amber-200 bg-amber-50/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-amber-800">در انتظار تأیید</CardTitle>
            <Activity className="h-4 w-4 text-amber-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-900">
              {MOCK_MRV_STATS.pendingVerifications}
            </div>
            <p className="text-xs text-amber-600 mt-1">پروژه در صف Verification Oracle</p>
          </CardContent>
        </Card>

        <Card className="border-purple-200 bg-purple-50/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-purple-800">پروژه‌های فعال</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900">
              {MOCK_MRV_STATS.activeProjects}
            </div>
            <p className="text-xs text-purple-600 mt-1">در شبکه MRV Registry</p>
          </CardContent>
        </Card>
      </div>

      {/* بخش ۲: توضیح جریان داده (Data Flow) برای کاربر */}
      <Card className="border-stone-200">
        <CardHeader>
          <CardTitle className="text-lg">چگونه EcoCoin تولید می‌شود؟</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 text-sm text-stone-600">
            <div className="flex-1 p-3 bg-stone-100 rounded-lg text-center">۱. جمع‌آوری داده‌های ماهواره‌ای (MRV)</div>
            <span className="text-stone-400">➔</span>
            <div className="flex-1 p-3 bg-stone-100 rounded-lg text-center">۲. تأیید توسط Verification Oracle</div>
            <span className="text-stone-400">➔</span>
            <div className="flex-1 p-3 bg-emerald-100 rounded-lg text-center text-emerald-800 font-semibold">۳. Mint خودکار EcoCoin</div>
          </div>
          <p className="text-xs text-stone-500 mt-2">
            * در حال حاضر سیستم در حالت شبیه‌سازی (Mock) قرار دارد. آدرس قرارداد: {CONTRACTS.EcoCoin}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}