import { Link, useNavigate, useLocation } from "react-router-dom";
import { Leaf } from "lucide-react";
import { LoginForm } from "../features/auth/LoginForm";
import { LanguageSwitcher } from "../components/Layout/LanguageSwitcher";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from || "/dashboard";

  return (
    <div className="relative flex min-h-screen flex-col bg-gradient-to-b from-emerald-50/80 via-white to-amber-50/40">
      <div className="flex items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold text-slate-800">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
            <Leaf className="h-5 w-5" />
          </span>
          EcoNojin
        </Link>
        <LanguageSwitcher />
      </div>
      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md space-y-4">
          <LoginForm onSuccess={() => navigate(from, { replace: true })} />
          <p className="text-center text-sm text-stone-600">
            No account?{" "}
            <Link to="/register" className="font-bold text-emerald-700 hover:underline">
              Register
            </Link>
          </p>
          <p className="text-center">
            <Link to="/" className="text-xs font-medium text-stone-500 hover:text-stone-800">
              ← Back to home
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
