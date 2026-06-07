#!/usr/bin/env python3
"""Apply Root Layout, Real Auth, and Update Navbar"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src"

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + {path.relative_to(ROOT)}")

def main():
    print("=" * 70)
    print("🔧 Applying Root Layout, Real Auth & Updating Navbar")
    print("=" * 70)

    # =========================================================================
    # 1. ROOT LAYOUT (Ensures Header & Footer on ALL pages)
    # =========================================================================
    print("\n[1/5] Updating Root Layout...")
    layout_content = '''import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "اکو نوژین | پلتفرم جامع احیای زمین و اکو کوین",
  description: "پلتفرم علمی-فناورانه احیای مناظر خشک، ماینینگ سبز و ارز دیجیتال اکولوژیک",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <body className={`${inter.className} antialiased bg-slate-950 text-white min-h-screen flex flex-col`}>
        <Navbar />
        <main className="flex-1 pt-20">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
'''
    write_file(WEB_DIR / "app" / "layout.tsx", layout_content)

    # =========================================================================
    # 2. AUTH UTILITY (Real state management)
    # =========================================================================
    print("\n[2/5] Creating Auth Utility...")
    auth_content = '''// src/lib/auth.ts
export interface User {
  name: string;
  email: string;
  token: string;
}

export const login = (email: string, name: string) => {
  const user: User = { 
    email, 
    name, 
    token: "mock-jwt-token-" + Date.now() 
  };
  localStorage.setItem("econojin_user", JSON.stringify(user));
  window.dispatchEvent(new Event("storage")); // Trigger UI update across components
  return user;
};

export const register = (name: string, email: string, password: string) => {
  // In a real app, this would call an API
  return login(email, name);
};

export const logout = () => {
  localStorage.removeItem("econojin_user");
  window.dispatchEvent(new Event("storage"));
};

export const getUser = (): User | null => {
  if (typeof window !== "undefined") {
    const userStr = localStorage.getItem("econojin_user");
    return userStr ? JSON.parse(userStr) : null;
  }
  return null;
};
'''
    write_file(WEB_DIR / "lib" / "auth.ts", auth_content)

    # =========================================================================
    # 3. REAL LOGIN PAGE
    # =========================================================================
    print("\n[3/5] Creating Real Login Page...")
    login_content = '''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Leaf, Mail, Lock, ArrowRight, Eye, EyeOff, Loader2 } from "lucide-react";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      if (email && password.length >= 6) {
        const name = email.split("@")[0];
        login(email, name);
        router.push("/");
      } else {
        setError("ایمیل یا رمز عبور نامعتبر است (رمز باید حداقل ۶ کاراکتر باشد)");
        setIsLoading(false);
      }
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/20 to-slate-950" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl"
      >
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 mb-4">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-black text-white mb-2">خوش آمدید</h1>
          <p className="text-slate-400 text-sm">وارد حساب کاربری اکو نوژین خود شوید</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-300 mb-2">ایمیل</label>
            <div className="relative">
              <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition-colors"
                placeholder="name@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-2">رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pr-10 pl-10 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition-colors"
                placeholder="••••••••"
                required
                minLength={6}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-slate-400 cursor-pointer">
              <input type="checkbox" className="rounded border-slate-700 bg-slate-800 text-emerald-500 focus:ring-emerald-500" />
              مرا به خاطر بسپار
            </label>
            <Link href="/forgot-password" className="text-emerald-400 hover:text-emerald-300">فراموشی رمز؟</Link>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                در حال ورود...
              </>
            ) : (
              <>
                ورود به حساب
                <ArrowRight className="h-5 w-5" />
              </>
            )}
          </button>
        </form>

        <p className="text-center text-slate-400 text-sm mt-6">
          حساب کاربری ندارید؟{" "}
          <Link href="/register" className="text-emerald-400 hover:text-emerald-300 font-bold">
            ثبت‌نام کنید
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
'''
    write_file(WEB_DIR / "app" / "login" / "page.tsx", login_content)

    # =========================================================================
    # 4. REAL REGISTER PAGE
    # =========================================================================
    print("\n[4/5] Creating Real Register Page...")
    register_content = '''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Leaf, Mail, Lock, User, ArrowRight, Loader2 } from "lucide-react";
import { register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("رمز عبور و تکرار آن مطابقت ندارند");
      return;
    }

    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      register(name, email, password);
      router.push("/");
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 to-slate-950" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl"
      >
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 mb-4">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-black text-white mb-2">ایجاد حساب کاربری</h1>
          <p className="text-slate-400 text-sm">به خانواده اکو نوژین بپیوندید</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-300 mb-2">نام و نام خانوادگی</label>
            <div className="relative">
              <User className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="نام شما"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-2">ایمیل</label>
            <div className="relative">
              <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="name@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-2">رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="حداقل ۶ کاراکتر"
                required
                minLength={6}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-2">تکرار رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="تکرار رمز عبور"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                در حال ثبت‌نام...
              </>
            ) : (
              <>
                ایجاد حساب کاربری
                <ArrowRight className="h-5 w-5" />
              </>
            )}
          </button>
        </form>

        <p className="text-center text-slate-400 text-sm mt-6">
          قبلاً ثبت‌نام کرده‌اید؟{" "}
          <Link href="/login" className="text-blue-400 hover:text-blue-300 font-bold">
            وارد شوید
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
'''
    write_file(WEB_DIR / "app" / "register" / "page.tsx", register_content)

    # =========================================================================
    # 5. UPDATE NAVBAR (Smart Auth State)
    # =========================================================================
    print("\n[5/5] Updating Navbar with Auth State...")
    # We will read the existing navbar and inject auth logic
    navbar_path = WEB_DIR / "components" / "layout" / "Navbar.tsx"
    if navbar_path.exists():
        content = navbar_path.read_text(encoding="utf-8")
        
        # Add auth imports
        if "import { getUser, logout }" not in content:
            content = content.replace(
                'import {',
                'import { getUser, logout } from "@/lib/auth";\nimport {'
            )
        
        # Add user state
        if "const [user, setUser]" not in content:
            content = content.replace(
                'export default function Navbar() {',
                '''export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [isScrolled, setIsScrolled] = useState(false);'''
            )
            
        # Add useEffect for auth
        if "useEffect(() => { setUser(getUser())" not in content:
            content = content.replace(
                'useEffect(() => {\n    const handleScroll',
                '''useEffect(() => {
    const checkAuth = () => setUser(getUser());
    checkAuth();
    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  useEffect(() => {'''
            )

        # Replace Login button with User/Logout logic
        content = content.replace(
            '''<Link href="/login" className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-sm transition-all">
                <LogIn className="h-4 w-4" />
                ورود
              </Link>''',
            '''{user ? (
                <div className="hidden md:flex items-center gap-3">
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-xs font-bold text-white">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <span className="text-sm font-bold text-white">{user.name}</span>
                  </div>
                  <button 
                    onClick={() => { logout(); }} 
                    className="p-2 rounded-lg text-slate-300 hover:text-red-400 hover:bg-red-500/10 transition-all"
                    title="خروج"
                  >
                    <LogIn className="h-5 w-5 rotate-180" />
                  </button>
                </div>
              ) : (
                <Link href="/login" className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-sm transition-all">
                  <LogIn className="h-4 w-4" />
                  ورود
                </Link>
              )}'''
        )
        
        navbar_path.write_text(content, encoding="utf-8")
        print("  + Navbar updated with Auth State")

    # =========================================================================
    # 6. Clean cache
    # =========================================================================
    print("\n[6/6] Cleaning Next.js cache...")
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("  + .next cache removed")
        except Exception as e:
            print(f"  ! {e}")

    print("\n" + "=" * 70)
    print("✅ Root Layout, Real Auth & Smart Navbar applied successfully!")
    print("=" * 70)
    print("\n🎯 What's new:")
    print("  1. Header & Footer are now on EVERY page (via layout.tsx)")
    print("  2. Login & Register are REAL forms (with loading, validation, redirect)")
    print("  3. Navbar is SMART: Shows User Avatar + Logout when logged in")
    print("  4. Auth state is saved in localStorage (persists on refresh)")
    print("\n🚀 Next steps:")
    print("  1. Restart frontend:")
    print("     cd apps\\web")
    print("     pnpm run dev -- -p 3001")
    print("")
    print("  2. Test the flow:")
    print("     - Go to http://localhost:3001/login")
    print("     - Enter any email and a 6+ char password")
    print("     - Click Login -> Watch it redirect to Home")
    print("     - Look at the Navbar: Your avatar and Logout button will appear!")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())