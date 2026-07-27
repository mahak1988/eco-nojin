import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSent(true);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-50 p-4">
      <form onSubmit={onSubmit} className="w-full max-w-md space-y-4 rounded-3xl border bg-white p-8 shadow-lg">
        <h1 className="font-display text-2xl text-stone-800">Forgot password</h1>
        <p className="text-sm text-stone-500">We will email a reset link (stub in local).</p>
        {sent ? (
          <p className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">If the account exists, instructions were sent.</p>
        ) : (
          <>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full rounded-xl border px-3 py-2.5"
            />
            <button type="submit" className="w-full rounded-xl bg-emerald-600 py-2.5 font-bold text-white">
              Send reset
            </button>
          </>
        )}
        <Link to="/login" className="block text-center text-sm font-bold text-emerald-700">
          Back to login
        </Link>
      </form>
    </div>
  );
}
