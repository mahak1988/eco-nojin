import { useState } from 'react';
import { Calendar, Users, MapPin, Phone, Mail, CreditCard, Check, ArrowLeft } from 'lucide-react';

interface FormData {
  destination: string; date: string; guests: number; name: string;
  phone: string; email: string; notes: string;
}

const DESTINATIONS = [
  'دره الموت', 'جنگل‌های ماسال', 'کویر لوت', 'جزیره قشم',
  'روستای کندوان', 'سواحل چابهار', 'دامنه‌های دماوند', 'تالاب انزلی',
];

export default function TourBookingPage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormData>({
    destination: '', date: '', guests: 2, name: '', phone: '', email: '', notes: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const update = (field: keyof FormData, value: string | number) => setForm(f => ({ ...f, [field]: value }));

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-stone-50 to-emerald-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-2xl font-bold text-stone-800 mb-2">رزرو با موفقیت ثبت شد!</h2>
          <p className="text-stone-600 mb-6">کارشناسان ما در اسرع وقت با شما تماس خواهند گرفت</p>
          <button onClick={() => { setSubmitted(false); setStep(1); }} className="w-full py-3 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700">
            بازگشت به صفحه اصلی
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-stone-50 to-emerald-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {step > 1 && (
            <button onClick={() => setStep(s => s - 1)} className="flex items-center gap-2 text-stone-500 hover:text-stone-700 mb-6">
              <ArrowLeft className="w-5 h-5" /> بازگشت
            </button>
          )}
          <h1 className="text-2xl font-bold text-stone-800 mb-2">رزرو تور اکوتوریسم</h1>
          <div className="flex gap-2 mb-8">
            {[1, 2, 3].map(s => (
              <div key={s} className={'flex-1 h-2 rounded-full ' + (s <= step ? 'bg-emerald-500' : 'bg-stone-200')} />
            ))}
          </div>

          {step === 1 && (
            <div className="space-y-4">
              <h3 className="font-bold text-stone-700">انتخاب مقصد و تاریخ</h3>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">مقصد</label>
                <div className="relative">
                  <MapPin className="absolute right-3 top-3 w-5 h-5 text-stone-400" />
                  <select value={form.destination} onChange={e => update('destination', e.target.value)}
                    className="w-full pr-10 pl-4 py-3 rounded-xl border border-stone-200 text-right">
                    <option value="">انتخاب مقصد...</option>
                    {DESTINATIONS.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">تاریخ</label>
                <div className="relative">
                  <Calendar className="absolute right-3 top-3 w-5 h-5 text-stone-400" />
                  <input type="date" value={form.date} onChange={e => update('date', e.target.value)}
                    className="w-full pr-10 pl-4 py-3 rounded-xl border border-stone-200 text-right" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">تعداد مهمان</label>
                <div className="relative">
                  <Users className="absolute right-3 top-3 w-5 h-5 text-stone-400" />
                  <input type="number" min={1} max={20} value={form.guests} onChange={e => update('guests', parseInt(e.target.value) || 1)}
                    className="w-full pr-10 pl-4 py-3 rounded-xl border border-stone-200 text-right" />
                </div>
              </div>
              <button onClick={() => setStep(2)} disabled={!form.destination || !form.date}
                className="w-full py-3 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700 disabled:bg-stone-300 disabled:cursor-not-allowed">
                ادامه
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h3 className="font-bold text-stone-700">اطلاعات تماس</h3>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">نام و نام خانوادگی</label>
                <input type="text" value={form.name} onChange={e => update('name', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-stone-200 text-right" placeholder="نام خود را وارد کنید" />
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">شماره تماس</label>
                <div className="relative">
                  <Phone className="absolute right-3 top-3 w-5 h-5 text-stone-400" />
                  <input type="tel" value={form.phone} onChange={e => update('phone', e.target.value)}
                    className="w-full pr-10 pl-4 py-3 rounded-xl border border-stone-200 text-right" placeholder="09xxxxxxxxx" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">ایمیل</label>
                <div className="relative">
                  <Mail className="absolute right-3 top-3 w-5 h-5 text-stone-400" />
                  <input type="email" value={form.email} onChange={e => update('email', e.target.value)}
                    className="w-full pr-10 pl-4 py-3 rounded-xl border border-stone-200 text-right" placeholder="example@email.com" />
                </div>
              </div>
              <button onClick={() => setStep(3)} disabled={!form.name || !form.phone}
                className="w-full py-3 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700 disabled:bg-stone-300 disabled:cursor-not-allowed">
                ادامه
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <h3 className="font-bold text-stone-700">تایید نهایی</h3>
              <div className="bg-stone-50 rounded-xl p-4 space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-stone-500">مقصد:</span><span className="font-medium">{form.destination}</span></div>
                <div className="flex justify-between"><span className="text-stone-500">تاریخ:</span><span className="font-medium">{form.date}</span></div>
                <div className="flex justify-between"><span className="text-stone-500">تعداد مهمان:</span><span className="font-medium">{form.guests} نفر</span></div>
                <div className="flex justify-between"><span className="text-stone-500">نام:</span><span className="font-medium">{form.name}</span></div>
                <div className="flex justify-between"><span className="text-stone-500">تلفن:</span><span className="font-medium">{form.phone}</span></div>
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-600 mb-1">یادداشت اضافی</label>
                <textarea value={form.notes} onChange={e => update('notes', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-stone-200 text-right" rows={3} placeholder="هرگونه درخواست خاص..." />
              </div>
              <button onClick={() => setSubmitted(true)}
                className="w-full py-3 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700 flex items-center justify-center gap-2">
                <CreditCard className="w-5 h-5" /> ثبت نهایی رزرو
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
