import Link from 'next/link';
import { Leaf, Mail, Phone, MapPin } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-ocean-500 to-forest-500 rounded-lg flex items-center justify-center">
                <Leaf className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="font-bold text-lg">هیدروما نوژین</div>
                <div className="text-xs text-gray-400">Hydroma Nozhin</div>
              </div>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              مدیریت هوشمند منظر برای احیای آب، خاک و معیشت در ایران و منطقه منا
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-bold text-lg mb-4">دسترسی سریع</h3>
            <ul className="space-y-2 text-sm">
              <li><Link href="/about" className="text-gray-400 hover:text-white transition-colors">درباره ما</Link></li>
              <li><Link href="/models" className="text-gray-400 hover:text-white transition-colors">مدل‌های علمی</Link></li>
              <li><Link href="/pilots" className="text-gray-400 hover:text-white transition-colors">پایلوت‌ها</Link></li>
              <li><Link href="/dashboard" className="text-gray-400 hover:text-white transition-colors">داشبورد</Link></li>
            </ul>
          </div>

          {/* SDGs */}
          <div>
            <h3 className="font-bold text-lg mb-4">اهداف توسعه پایدار</h3>
            <div className="flex flex-wrap gap-2">
              {[2, 6, 8, 13, 15].map((sdg) => (
                <div
                  key={sdg}
                  className="w-10 h-10 bg-gradient-to-br from-ocean-500 to-forest-500 rounded-lg flex items-center justify-center font-bold text-sm"
                >
                  {sdg}
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-400 mt-2">
              هم‌سویی با اهداف ۲، ۶، ۸، ۱۳ و ۱۵
            </p>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-bold text-lg mb-4">تماس با ما</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center gap-2 text-gray-400">
                <Mail className="w-4 h-4" />
                <span>dashteomidenarvan@gmail.com</span>
              </li>
              <li className="flex items-center gap-2 text-gray-400">
                <Phone className="w-4 h-4" />
                <span dir="ltr">0912-890-5771</span>
              </li>
              <li className="flex items-center gap-2 text-gray-400">
                <MapPin className="w-4 h-4" />
                <span>شرکت کشت و صنعت دشت امید نارون</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>© {new Date().getFullYear()} هیدروما نوژین. تمامی حقوق محفوظ است.</p>
          <p className="mt-2 text-xs">
            طرح ملی احیای مناظر خشک ایران | شرکت کشت و صنعت دشت امید نارون
          </p>
        </div>
      </div>
    </footer>
  );
}