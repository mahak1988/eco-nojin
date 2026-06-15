import type { Locale } from "../../../i18n-config";

type Props = {
  params: { locale: Locale };
};

const content = {
  fa: {
    title: "ایجاد حساب جدید",
    name: "نام کامل",
    email: "ایمیل",
    password: "رمز عبور",
    confirm: "تکرار رمز عبور",
    submit: "ثبت‌نام",
    loginHint: "حساب دارید؟",
    loginLink: "ورود به حساب",
  },
  en: {
    title: "Create a new account",
    name: "Full name",
    email: "Email",
    password: "Password",
    confirm: "Confirm password",
    submit: "Sign up",
    loginHint: "Already have an account?",
    loginLink: "Sign in",
  },
};

export default function RegisterPage({ params }: Props) {
  const t = content[params.locale];

  return (
    <section className="max-w-md mx-auto space-y-6">
      <h1 className="text-2xl font-semibold text-center">{t.title}</h1>

      <form className="space-y-4 bg-white border rounded-xl p-6 shadow-sm">
        <div className="space-y-1 text-sm">
          <label className="block font-medium">{t.name}</label>
          <input
            type="text"
            className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="space-y-1 text-sm">
          <label className="block font-medium">{t.email}</label>
          <input
            type="email"
            className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="space-y-1 text-sm">
          <label className="block font-medium">{t.password}</label>
          <input
            type="password"
            className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="space-y-1 text-sm">
          <label className="block font-medium">{t.confirm}</label>
          <input
            type="password"
            className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium"
        >
          {t.submit}
        </button>
      </form>

      <p className="text-center text-xs text-slate-600">
        {t.loginHint}{" "}
        <a href="./../login" className="text-blue-600 hover:underline">
          {t.loginLink}
        </a>
      </p>
    </section>
  );
}
