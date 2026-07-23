// apps/web/src/components/news/newsData.ts
export type NewsCategory = "launch" | "network" | "impact" | "research" | "policy";
export type SortKey = "newest" | "oldest" | "popular";

export interface NewsItem {
  id: string;
  titleKey: string;
  excerptKey: string;
  category: NewsCategory;
  date: string;          // ISO
  image: string;         // URL — SmartImg fallback دارد (درس gamecoca)
  readMinutes: number;
  views: number;
  featured?: boolean;
}

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

// تصاویر Unsplash معتبر؛ در صورت شکست شبکه، SmartImg به گرادیان per-category fallback می‌کند
export const NEWS: NewsItem[] = [
  { id: "n1", titleKey: "t1", excerptKey: "ex1", category: "launch",   date: daysAgo(1),  image: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80", readMinutes: 4, views: 3120, featured: true },
  { id: "n2", titleKey: "t2", excerptKey: "ex2", category: "network",  date: daysAgo(3),  image: "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=800&q=80", readMinutes: 3, views: 2480 },
  { id: "n3", titleKey: "t3", excerptKey: "ex3", category: "impact",   date: daysAgo(6),  image: "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80", readMinutes: 5, views: 4210 },
  { id: "n4", titleKey: "t4", excerptKey: "ex4", category: "research", date: daysAgo(9),  image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80", readMinutes: 6, views: 1890 },
  { id: "n5", titleKey: "t5", excerptKey: "ex5", category: "policy",   date: daysAgo(12), image: "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?auto=format&fit=crop&w=800&q=80", readMinutes: 4, views: 1340 },
  { id: "n6", titleKey: "t6", excerptKey: "ex6", category: "impact",   date: daysAgo(15), image: "https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=800&q=80", readMinutes: 3, views: 2760 },
  { id: "n7", titleKey: "t7", excerptKey: "ex7", category: "network",  date: daysAgo(18), image: "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=800&q=80", readMinutes: 4, views: 1620 },
  { id: "n8", titleKey: "t8", excerptKey: "ex8", category: "research", date: daysAgo(22), image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80", readMinutes: 7, views: 980 },
];

export const CATEGORY_FILTERS: ("all" | NewsCategory)[] = ["all", "launch", "network", "impact", "research", "policy"];

// رنگ per-category (سیر، استاندارد)
export const CATEGORY_ACCENT: Record<NewsCategory, { grad: string; chip: string; text: string }> = {
  launch:   { grad: "from-green-600 to-emerald-500",  chip: "bg-green-50 text-green-700 ring-green-600/15",  text: "text-green-700" },
  network:  { grad: "from-blue-600 to-sky-500",       chip: "bg-blue-50 text-blue-700 ring-blue-600/15",     text: "text-blue-700" },
  impact:   { grad: "from-amber-600 to-orange-500",   chip: "bg-amber-50 text-amber-700 ring-amber-600/15",  text: "text-amber-700" },
  research: { grad: "from-violet-600 to-purple-500",  chip: "bg-violet-50 text-violet-700 ring-violet-600/15", text: "text-violet-700" },
  policy:   { grad: "from-rose-600 to-pink-500",      chip: "bg-rose-50 text-rose-700 ring-rose-600/15",     text: "text-rose-700" },
};

// ── helpers ──
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "long", day: "numeric" });
}
export function formatViews(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { notation: n >= 1000 ? "compact" : "standard", maximumFractionDigits: 1 }).format(n);
}