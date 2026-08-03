// apps/web/src/pages/inventory/WarehousePage.tsx
import { Link } from "react-router-dom";
import { ArrowLeft, Warehouse, TrendingUp, AlertTriangle, Package } from "lucide-react";
import { useLang } from "../../components/eco/i18n";
import AnimatedSection from "../../components/animation/AnimatedSection";
import WarehouseMap from "../../components/inventory/WarehouseMap";
import StockCard from "../../components/inventory/StockCard";

export default function WarehousePage() {
  const { lang } = useLang();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <Link to="/inventory" className="flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          {lang === "fa" ? "بازگشت به انبارداری" : "Back to Inventory"}
        </Link>
      </div>

      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-stone-600 to-stone-800 shadow-lg shadow-stone-500/20">
            <Warehouse className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "مدیریت انبار" : "Warehouse Management"}
            </h1>
            <p className="text-sm text-stone-500">
              {lang === "fa" ? "نمای کلی وضعیت انبارها" : "Overview of warehouse status"}
            </p>
          </div>
        </div>
      </AnimatedSection>

      <div className="grid gap-4 sm:grid-cols-3">
        <AnimatedSection>
          <StockCard
            name="Total Stock" nameFa="موجودی کل" icon="📦"
            total={1250} unit={lang === "fa" ? "عدد" : "units"}
            categories={[
              { name: lang === "fa" ? "بذر" : "Seeds", count: 420 },
              { name: lang === "fa" ? "کود" : "Fertilizer", count: 180 },
              { name: lang === "fa" ? "ابزار" : "Tools", count: 350 },
            ]}
          />
        </AnimatedSection>
        <AnimatedSection>
          <StockCard
            name="Total Value" nameFa="ارزش کل" icon="💰"
            total={45_680_000} unit="IRR"
            categories={[
              { name: lang === "fa" ? "مواد اولیه" : "Raw", count: 12_500_000 },
              { name: lang === "fa" ? "محصولات" : "Products", count: 33_180_000 },
            ]}
          />
        </AnimatedSection>
        <AnimatedSection>
          <StockCard
            name="Alerts" nameFa="هشدارها" icon="⚠️"
            total={5} unit={lang === "fa" ? "مورد" : "items"}
            categories={[
              { name: lang === "fa" ? "کمبود موجودی" : "Low Stock", count: 3 },
              { name: lang === "fa" ? "نزدیک انقضا" : "Near Expiry", count: 2 },
            ]}
          />
        </AnimatedSection>
      </div>

      <AnimatedSection>
        <WarehouseMap />
      </AnimatedSection>
    </div>
  );
}
