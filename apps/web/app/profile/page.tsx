"use client";

export default function ProfilePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black pt-20">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-4xl font-black text-white mb-2">پروفایل کاربر</h1>
          <p className="text-gray-400">مدیریت اطلاعات شخصی و تنظیمات حساب کاربری</p>
        </div>
        
        <div className="glass rounded-2xl p-8 border border-white/10 mb-6">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-5xl">
                👤
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-black text-white mb-2">دکتر حسن رضایی</h2>
              <p className="text-gray-400 mb-1">hasan.rezaei@econojin.com</p>
              <p className="text-gray-400 mb-1">🏢 دانشگاه تهران</p>
              <p className="text-gray-300 mt-3">پژوهشگر هیدرولوژی و مدل‌سازی محیطی</p>
              <div className="flex gap-3 mt-4">
                <button className="px-6 py-2 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30">
                  ✏️ ویرایش پروفایل
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="glass rounded-2xl p-5 border border-blue-500/20">
            <div className="text-3xl mb-2">🧠</div>
            <div className="text-2xl font-black text-blue-400">۴۷</div>
            <div className="text-xs text-gray-400">شبیه‌سازی</div>
          </div>
          <div className="glass rounded-2xl p-5 border border-emerald-500/20">
            <div className="text-3xl mb-2">⭐</div>
            <div className="text-2xl font-black text-emerald-400">۱۲</div>
            <div className="text-xs text-gray-400">علاقه‌مندی</div>
          </div>
          <div className="glass rounded-2xl p-5 border border-purple-500/20">
            <div className="text-3xl mb-2">📊</div>
            <div className="text-2xl font-black text-purple-400">۱۵۶</div>
            <div className="text-xs text-gray-400">ساعت استفاده</div>
          </div>
          <div className="glass rounded-2xl p-5 border border-amber-500/20">
            <div className="text-3xl mb-2">🏆</div>
            <div className="text-2xl font-black text-amber-400">۸</div>
            <div className="text-xs text-gray-400">دستاوردها</div>
          </div>
        </div>
        
        <div className="glass rounded-2xl p-6 border border-white/10">
          <h3 className="text-xl font-bold text-white mb-4">اطلاعات حساب</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-3 border-b border-white/5">
              <span className="text-gray-400">نقش کاربری</span>
              <span className="text-white">پژوهشگر</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-white/5">
              <span className="text-gray-400">تاریخ عضویت</span>
              <span className="text-white">۱۴۰۲/۱۰/۲۵</span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-gray-400">اشتراک</span>
              <span className="text-emerald-400 font-bold">حرفه‌ای</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
