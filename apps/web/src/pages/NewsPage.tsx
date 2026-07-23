// apps/web/src/pages/NewsPage.tsx
import { useMemo, useState } from "react";
import { Newspaper, Search, FileText } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { NewsHero } from "../components/news/NewsHero";
import { NewsCard } from "../components/news/NewsCard";
import { NEWS_STR, newsText, catText, localeOf, type NewsLang } from "../components/news/newsI18n";
import { NEWS, CATEGORY_FILTERS, type NewsCategory, type NewsItem, type SortKey } from "../components/news/newsData";

const PAGE = 4;

export default function NewsPage() {
  const { lang } = useLang();
  const s = NEWS_STR[lang as NewsLang];
  const locale = localeOf(lang as NewsLang);

  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | NewsCategory>("all");
  const [sort, setSort] = useState<SortKey>("newest");
  const [visible, setVisible] = useState(PAGE);

  const featured = useMemo(() => NEWS.find((n) => n.featured) ?? null, []);
  const showHero = filter === "all" && search.trim() === "";

  // لیست grid: وقتی hero نمایش داده می‌شود، featured را حذف می‌کنیم
  const pool = useMemo(() => {
    const q = search.trim().toLowerCase();
    const base = showHero && featured ? NEWS.filter((n) => n.id !== featured.id) : NEWS;
    const list = base.filter((n) =>
      (filter === "all" || n.category === filter) &&
      (q === "" || newsText(s, n.titleKey).toLowerCase().includes(q) || newsText(s, n.excerptKey).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      if (sort === "popular") return b.views - a.views;
      if (sort === "oldest") return +new Date(a.date) - +new Date(b.date);
      return +new Date(b.date) - +new Date(a.date);
    });
    return list;
  }, [search, filter, sort, showHero, featured, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  // وقتی فیلتر/جست‌وجو تغییر کرد، pagination را ریست کن
  const resetKey = `${filter}-${sort}-${search}`;
  const [lastKey, setLastKey] = useState(resetKey);
  let shown = pool;
  if (lastKey !== resetKey) {
    // ریست lazy در رندر (الگوی رایج بدون useEffect اضافی)
    setLastKey(resetKey);
    setVisible(PAGE);
    shown = pool.slice(0, PAGE);
  } else {
    shown = pool.slice(0, visible);
  }
  const hasMore = visible < pool.length;

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
            <Newspaper className="h-5 w-5 text-green-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
          </div>
        </div>
      </SectionReveal>

      {/* hero (فقط حالت پیش‌فرض) */}
      {showHero && featured && (
        <SectionReveal delay={80}>
          <NewsHero item={featured} strings={s} lang={lang as NewsLang} />
        </SectionReveal>
      )}

      {/* toolbar */}
      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {CATEGORY_FILTERS.map((f) => (
              <button key={f} onClick={() => setFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
                  filter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
                }`}>
                {f === "all" ? s.filterAll : catText(s, f)}
              </button>
            ))}
          </div>
          <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)} className={selectCls} aria-label={s.sortLabel}>
            <option value="newest">{s.sortNewest}</option>
            <option value="oldest">{s.sortOldest}</option>
            <option value="popular">{s.sortPopular}</option>
          </select>
        </div>
      </SectionReveal>

      {/* grid / empty */}
      {shown.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <FileText className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noNews}</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {shown.map((item: NewsItem, i) => (
              <SectionReveal key={item.id} delay={Math.min(i * 60, 240)}>
                <NewsCard item={item} strings={s} lang={lang as NewsLang} />
              </SectionReveal>
            ))}
          </div>

          {hasMore && (
            <div className="flex justify-center pt-2">
              <button onClick={() => setVisible((v) => v + PAGE)}
                className="rounded-xl border border-stone-200 bg-white px-6 py-2.5 text-sm font-bold text-stone-700 shadow-sm transition-all hover:-translate-y-0.5 hover:bg-stone-50">
                {s.loadMore}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}