import { Link, useLocation } from "react-router-dom";
import { ArrowRight, Construction } from "lucide-react";

export default function ComingSoon({ title }: { title: string }) {
  const location = useLocation();
  
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/50 p-12 text-center dark:border-slate-700 dark:bg-slate-900/50">
      <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400">
        <Construction className="h-10 w-10" />
      </div>
      <h2 className="mb-2 text-2xl font-bold text-slate-800 dark:text-slate-100">
        {title}
      </h2>
      <p className="mb-8 max-w-md text-slate-500 dark:text-slate-400">
        این بخش در حال حاضر در دست توسعه است و به‌زودی با قابلیت‌های کامل در دسترس قرار خواهد گرفت.
      </p>
      <Link
        to="/dashboard"
        className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-emerald-700"
      >
        بازگشت به داشبورد
        <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}