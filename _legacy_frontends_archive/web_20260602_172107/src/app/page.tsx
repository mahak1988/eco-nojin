// src/app/page.tsx
export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 text-white p-8" dir="rtl">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 text-cyan-400">🌍 Econojin</h1>
        <p className="text-xl text-slate-300">ابرپروژه خدمات جامع رایگان</p>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto">
        <div className="p-6 bg-slate-800 rounded-xl hover:bg-slate-700 transition cursor-pointer">
          <h3 className="text-xl font-bold mb-2">🌤️ هواشناسی</h3>
          <p className="text-slate-400">پیش‌بینی و هشدارهای کشاورزی</p>
        </div>
        <div className="p-6 bg-slate-800 rounded-xl hover:bg-slate-700 transition cursor-pointer">
          <h3 className="text-xl font-bold mb-2">💰 حسابداری</h3>
          <p className="text-slate-400">مدیریت مالی شخصی و کسب‌وکار</p>
        </div>
        <div className="p-6 bg-slate-800 rounded-xl hover:bg-slate-700 transition cursor-pointer">
          <h3 className="text-xl font-bold mb-2">🗺️ GIS</h3>
          <p className="text-slate-400">نقشه‌کشی و تحلیل مکانی</p>
        </div>
      </div>
    </main>
  )
}