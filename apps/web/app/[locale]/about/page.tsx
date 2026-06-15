import type { Locale } from "../../i18n-config";

type Props = {
  params: { locale: Locale };
};

const content = {
  fa: {
    title: "درباره اکونوجین",
    body: "اکونوجین برای تحلیل‌گران، معامله‌گران و تیم‌های اقتصادی طراحی شده تا داده‌ها را از منابع مختلف جمع‌آوری و به بینش‌های قابل‌اقدام تبدیل کند.",
  },
  en: {
    title: "About econojin",
    body: "econojin is built for analysts, traders, and economic teams to aggregate data from multiple sources and turn it into actionable insights.",
  },
};

export default function AboutPage({ params }: Props) {
  const t = content[params.locale];

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">{t.title}</h1>
      <p className="text-slate-600">{t.body}</p>
    </section>
  );
}
