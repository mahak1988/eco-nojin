import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function VerifyOtpPage() {
  const [otp, setOtp] = useState("");
  const navigate = useNavigate();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (otp.length >= 4) navigate("/dashboard");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-50 p-4">
      <form onSubmit={onSubmit} className="w-full max-w-md space-y-4 rounded-3xl border bg-white p-8 shadow-lg">
        <h1 className="font-display text-2xl">Verify OTP</h1>
        <p className="text-sm text-stone-500">Enter the code sent to your email/phone (local: any 4+ digits).</p>
        <input
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          className="w-full rounded-xl border px-3 py-2.5 tracking-widest"
          placeholder="••••"
        />
        <button type="submit" className="w-full rounded-xl bg-emerald-600 py-2.5 font-bold text-white">
          Verify
        </button>
        <Link to="/login" className="block text-center text-sm font-bold text-emerald-700">
          Login
        </Link>
      </form>
    </div>
  );
}
