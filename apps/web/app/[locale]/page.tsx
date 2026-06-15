import type { Locale } from "../i18n-config";

type Props = {
  params: { locale: Locale };
};

const content = {
  fa: {
    title: "اکونوجین – داشبورد اقتصادی شما",
    subtitle: "تحلیل، پایش و تصویرسازی داده‌های مالی و اقتصادی در یک پلتفرم یکپارچه.",
    ctaPrimary: "شروع کنید",
    ctaSecondary: "بیشتر بدانید",
  },
  en: {
    title: "econojin – Your economic dashboard",
    subtitle: "Analyze, monitor, and visualize financial and economic data in one place.",
    ctaPrimary: "Get started",
    ctaSecondary: "Learn more",
  },
};

export default function HomePage({ params }: Props) {
  const locale = params.locale;
  const t = content[locale];

  return (
    <section className="grid gap-8 md:grid-cols-2 items-center">
      <div className="space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold">{t.title}</h1>
        <p className="text-slate-600">{t.subtitle}</p>
        <div className="flex gap-3 mt-4">
          <button className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm">
            {t.ctaPrimary}
          </button>
          <button className="px-4 py-2 rounded-md border border-slate-300 text-sm">
            {t.ctaSecondary}
          </button>
        </div>
      </div>
      <div className="border rounded-xl bg-white shadow-sm p-4 text-sm text-slate-600">
        <p>
          این بخش می‌تواند بعداً به یک نمودار زنده، ویجت بازارها یا خلاصه وضعیت
          پرتفوی تبدیل شود.
        </p>
      </div>
    </section>
  );
}
