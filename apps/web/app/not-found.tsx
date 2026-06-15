export default function GlobalNotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="bg-white border rounded-xl shadow-sm px-8 py-6 text-center space-y-3">
        <h1 className="text-xl font-semibold">صفحه پیدا نشد</h1>
        <p className="text-sm text-slate-600">
          آدرس وارد شده در هیچ‌یک از زبان‌های فعال تعریف نشده است.
        </p>
      </div>
    </div>
  );
}
