import { Link } from "react-router-dom";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-[var(--border)] py-8 mt-auto bg-[var(--surface-raised)]" dir="rtl">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
        {/* لوگو و متن کپی‌رایت */}
        <div className="text-sm text-[var(--text-2)] flex items-center gap-2">
          <span className="font-bold text-[var(--v-green)]">Econojin</span>
          <span>© {currentYear} - تمامی حقوق محفوظ است.</span>
        </div>

        {/* لینک‌های مفید */}
        <div className="flex gap-4 text-sm font-medium">
          <Link 
            to="/privacy" 
            className="text-[var(--text-2)] hover:text-[var(--v-green)] transition-colors"
          >
            حریم خصوصی
          </Link>
          <Link 
            to="/terms" 
            className="text-[var(--text-2)] hover:text-[var(--v-green)] transition-colors"
          >
            شرایط استفاده
          </Link>
          <Link 
            to="/contact" 
            className="text-[var(--text-2)] hover:text-[var(--v-green)] transition-colors"
          >
            تماس با ما
          </Link>
        </div>
      </div>
    </footer>
  );
}