import React, { useEffect, useState } from 'react';
import { TrendingUp, Plus, Loader2, RefreshCw, BarChart3, DollarSign } from 'lucide-react';

interface EconomicAnalysis {
  id: number;
  title?: string;
  description?: string;
  created_at?: string;
  [key: string]: unknown;
}

interface CostBenefitResult {
  npv?: number;
  irr?: number;
  benefit_cost_ratio?: number;
  payback_period_years?: number;
  [key: string]: unknown;
}

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

const EconomicsPage: React.FC = () => {
  const [analyses, setAnalyses] = useState<EconomicAnalysis[]>([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, size: 20, pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [calcResult, setCalcResult] = useState<CostBenefitResult | null>(null);
  const [calcLoading, setCalcLoading] = useState(false);
  const [calcForm, setCalcForm] = useState({
    initial_investment: '1000000',
    annual_benefits: '300000',
    annual_costs: '50000',
    years: '10',
    discount_rate: '0.1',
  });

  const fetchAnalyses = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${BASE}/economics/analyses?page=${page}&size=20`, { credentials: 'include' });
      if (!r.ok) throw new Error(`خطا: ${r.status}`);
      const body = await r.json();
      setAnalyses(body.data ?? body);
      if (body.meta) setMeta(body.meta);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'خطا در بارگذاری');
    } finally {
      setLoading(false);
    }
  };

  const runCostBenefit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalcLoading(true);
    try {
      const r = await fetch(`${BASE}/economics/cost-benefit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          initial_investment: parseFloat(calcForm.initial_investment),
          annual_benefits: parseFloat(calcForm.annual_benefits),
          annual_costs: parseFloat(calcForm.annual_costs),
          years: parseInt(calcForm.years),
          discount_rate: parseFloat(calcForm.discount_rate),
        }),
      });
      if (!r.ok) throw new Error(`خطا: ${r.status}`);
      setCalcResult(await r.json());
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'خطا در محاسبه');
    } finally {
      setCalcLoading(false);
    }
  };

  useEffect(() => { fetchAnalyses(); }, []);

  const fmt = (v: number | undefined) =>
    v != null ? v.toLocaleString('fa-IR', { maximumFractionDigits: 2 }) : '—';

  return (
    <div className="space-y-6 p-1" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">اقتصاد سبز</h1>
          <p className="text-sm text-muted-foreground">تحلیل هزینه-فایده و EcoCoin</p>
        </div>
        <button
          onClick={() => fetchAnalyses()}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm hover:bg-muted transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> بارگذاری مجدد
        </button>
      </div>

      {/* Cost-Benefit Calculator */}
      <div className="rounded-xl border bg-card p-5">
        <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-violet-500" /> ماشین‌حساب هزینه-فایده
        </h2>
        <form onSubmit={runCostBenefit} className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { key: 'initial_investment', label: 'سرمایه‌گذاری اولیه (تومان)', placeholder: '1000000' },
              { key: 'annual_benefits', label: 'درآمد سالانه (تومان)', placeholder: '300000' },
              { key: 'annual_costs', label: 'هزینه سالانه (تومان)', placeholder: '50000' },
              { key: 'years', label: 'دوره (سال)', placeholder: '10' },
              { key: 'discount_rate', label: 'نرخ تنزیل (مثال: 0.1)', placeholder: '0.1' },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="text-xs text-muted-foreground block mb-1">{label}</label>
                <input
                  type="number" step="any"
                  value={calcForm[key as keyof typeof calcForm]}
                  onChange={(e) => setCalcForm((f) => ({ ...f, [key]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            ))}
          </div>
          <button
            type="submit"
            disabled={calcLoading}
            className="flex items-center gap-1.5 px-5 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 disabled:opacity-50"
          >
            {calcLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            محاسبه
          </button>
        </form>

        {calcResult && (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'NPV', value: fmt(calcResult.npv), icon: <DollarSign className="w-4 h-4 text-green-500" />, color: 'bg-green-50' },
              { label: 'IRR', value: calcResult.irr != null ? `${(calcResult.irr * 100).toFixed(1)}٪` : '—', icon: <TrendingUp className="w-4 h-4 text-blue-500" />, color: 'bg-blue-50' },
              { label: 'نسبت B/C', value: fmt(calcResult.benefit_cost_ratio), icon: <BarChart3 className="w-4 h-4 text-violet-500" />, color: 'bg-violet-50' },
              { label: 'دوره بازگشت (سال)', value: fmt(calcResult.payback_period_years), icon: <RefreshCw className="w-4 h-4 text-amber-500" />, color: 'bg-amber-50' },
            ].map((item) => (
              <div key={item.label} className={`${item.color} rounded-xl p-3 flex items-center gap-3`}>
                {item.icon}
                <div>
                  <p className="text-xs text-muted-foreground">{item.label}</p>
                  <p className="font-bold text-sm">{item.value}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analyses List */}
      <div>
        <h2 className="text-sm font-semibold mb-3">تحلیل‌های ذخیره‌شده ({meta.total})</h2>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">{error}</div>
        ) : analyses.length === 0 ? (
          <div className="rounded-xl border bg-card p-8 text-center text-muted-foreground text-sm">
            هنوز تحلیلی ذخیره نشده.
          </div>
        ) : (
          <div className="rounded-xl border bg-card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-right px-4 py-3 font-medium text-muted-foreground">شناسه</th>
                  <th className="text-right px-4 py-3 font-medium text-muted-foreground">عنوان</th>
                  <th className="text-right px-4 py-3 font-medium text-muted-foreground hidden sm:table-cell">تاریخ ایجاد</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map((a, i) => (
                  <tr key={a.id} className={`border-b last:border-0 hover:bg-muted/30 ${i % 2 === 0 ? '' : 'bg-muted/10'}`}>
                    <td className="px-4 py-3 text-muted-foreground">#{a.id}</td>
                    <td className="px-4 py-3 font-medium">{a.title ?? `تحلیل #${a.id}`}</td>
                    <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell text-xs">
                      {a.created_at ? new Date(a.created_at).toLocaleDateString('fa-IR') : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default EconomicsPage;
