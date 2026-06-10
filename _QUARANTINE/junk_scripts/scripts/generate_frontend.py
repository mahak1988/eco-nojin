#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 Econojin Frontend Generator
تولید خودکار فرانت‌اند حرفه‌ای با طراحی یکپارچه، ماژولار و کاملاً فارسی
"""
import json
import os
from pathlib import Path

# مسیر ریشه پروژه
ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web"  # یا ROOT / "web" اگر ساختار ساده است

# اطمینان از وجود پوشه web
if not (ROOT / "apps" / "web").exists():
    WEB = ROOT / "web"


def write_file(path: Path, content: str) -> None:
    """نوشتن فایل با encoding UTF-8 و ایجاد پوشه‌های والد"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ ایجاد شد: {path.relative_to(ROOT)}")


# ============================================================================
# ۱. فایل‌های پیکربندی اصلی
# ============================================================================


def generate_config_files():
    """تولید فایل‌های پیکربندی Next.js و Tailwind"""

    # next.config.js
    write_file(
        WEB / "next.config.js",
        """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // output: 'export', // ← برای dev کامنت شود
  images: { unoptimized: true },
  i18n: { 
    locales: ['fa', 'en'], 
    defaultLocale: 'fa',
    localeDetection: false
  },
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' }
    ]
  },
  webpack: (config) => {
    config.resolve.fallback = { fs: false, net: false, tls: false };
    return config;
  }
};
module.exports = nextConfig;
""",
    )

    # tailwind.config.js
    write_file(
        WEB / "tailwind.config.js",
        """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/modules/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      colors: {
        primary: {
          50: '#f0f9ff', 100: '#e0f2fe', 200: '#bae6fd', 300: '#7dd3fc',
          400: '#38bdf8', 500: '#0ea5e9', 600: '#0284c7', 700: '#0369a1',
          800: '#075985', 900: '#0c4a6e',
        },
        success: { 500: '#10b981', 600: '#059669' },
        warning: { 500: '#f59e0b', 600: '#d97706' },
        danger: { 500: '#ef4444', 600: '#dc2626' },
        eco: { 500: '#22c55e', 600: '#16a34a' }, // رنگ برند اکو نوژین
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: 0 }, '100%': { opacity: 1 } },
        slideUp: { '0%': { opacity: 0, transform: 'translateY(20px)' }, '100%': { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
""",
    )

    # postcss.config.js
    write_file(
        WEB / "postcss.config.js",
        """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",
    )

    # tsconfig.json
    write_file(
        WEB / "tsconfig.json",
        json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2020",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "paths": {
                        "@/*": ["./src/*"],
                        "@/components/*": ["./src/components/*"],
                        "@/modules/*": ["./src/modules/*"],
                        "@/lib/*": ["./src/lib/*"],
                        "@/hooks/*": ["./src/hooks/*"],
                        "@/store/*": ["./src/store/*"],
                    },
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"],
            },
            indent=2,
        ),
    )

    # package.json به‌روز شده
    pkg = {
        "name": "@econojin/web",
        "version": "2.0.0",
        "private": True,
        "scripts": {
            "dev": "next dev -p 3000",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "type-check": "tsc --noEmit",
            "format": 'prettier --write "src/**/*.{ts,tsx,css}"',
        },
        "dependencies": {
            "next": "14.2.5",
            "react": "18.3.1",
            "react-dom": "18.3.1",
            # Charts & Maps
            "recharts": "^2.12.7",
            "leaflet": "^1.9.4",
            "react-leaflet": "^4.2.1",
            # UI & Animations
            "framer-motion": "^11.3.0",
            "lucide-react": "^0.400.0",
            # State & Data
            "zustand": "^4.5.4",
            "axios": "^1.7.2",
            "date-fns": "^2.30.0",
            "date-fns-jalali": "^3.6.0-0",
            # Forms & Utils
            "react-hook-form": "^7.52.0",
            "@hookform/resolvers": "^3.9.0",
            "zod": "^3.23.8",
            # RTL & i18n
            "next-intl": "^3.17.0",
        },
        "devDependencies": {
            "@types/node": "22.1.0",
            "@types/react": "18.3.3",
            "@types/react-dom": "18.3.0",
            "@types/leaflet": "^1.9.12",
            "typescript": "5.5.4",
            "tailwindcss": "^3.4.7",
            "postcss": "^8.4.39",
            "autoprefixer": "^10.4.19",
            "@tailwindcss/forms": "^0.5.7",
            "@tailwindcss/typography": "^0.5.13",
            "prettier": "^3.3.3",
            "eslint": "^8.57.0",
            "eslint-config-next": "14.2.5",
        },
    }
    write_file(WEB / "package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

    print("✅ فایل‌های پیکربندی ایجاد شدند.")


# ============================================================================
# ۲. استایل‌های سراسری و فونت
# ============================================================================


def generate_styles():
    """تولید فایل‌های CSS و فونت"""

    # globals.css
    write_file(
        WEB / "src" / "styles" / "globals.css",
        """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
  
  * { @apply border-border box-border; }
  body { @apply bg-background text-foreground antialiased; }
  html { scroll-behavior: smooth; }
  
  /* اسکرول‌بار سفارشی */
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { @apply bg-slate-800; }
  ::-webkit-scrollbar-thumb { @apply bg-slate-600 rounded-full hover:bg-slate-500 transition; }
}

@layer components {
  /* کارت‌ها */
  .card { @apply bg-card rounded-xl border border-border p-6 shadow-lg shadow-black/20; }
  .card-hover { @apply hover:border-primary/50 hover:shadow-primary/10 transition-all duration-300; }
  
  /* دکمه‌ها */
  .btn { @apply inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed; }
  .btn-primary { @apply btn bg-primary-600 hover:bg-primary-500 text-white shadow-lg shadow-primary-500/25; }
  .btn-secondary { @apply btn bg-slate-700 hover:bg-slate-600 text-slate-100; }
  .btn-outline { @apply btn border border-slate-600 hover:border-primary-500 hover:text-primary-400 text-slate-300; }
  .btn-ghost { @apply btn hover:bg-slate-800 text-slate-300; }
  
  /* فرم‌ها */
  .input { @apply w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition; }
  .label { @apply block text-sm font-medium text-slate-300 mb-1.5; }
  
  /* جدول‌ها */
  .table-container { @apply overflow-x-auto rounded-xl border border-slate-700; }
  .table { @apply w-full text-sm text-right; }
  .table th { @apply bg-slate-800/50 px-4 py-3 font-semibold text-slate-300 border-b border-slate-700; }
  .table td { @apply px-4 py-3 border-b border-slate-800 text-slate-300; }
  .table tr:hover { @apply bg-slate-800/30; }
  
  /* وضعیت‌ها */
  .badge { @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium; }
  .badge-success { @apply badge bg-success-500/10 text-success-400 border border-success-500/20; }
  .badge-warning { @apply badge bg-warning-500/10 text-warning-400 border border-warning-500/20; }
  .badge-danger { @apply badge bg-danger-500/10 text-danger-400 border border-danger-500/20; }
  .badge-info { @apply badge bg-primary-500/10 text-primary-400 border border-primary-500/20; }
  
  /* انیمیشن‌های صفحه */
  .page-enter { animation: fade-in 0.4s ease-out, slide-up 0.5s ease-out; }
}

@layer utilities {
  .text-balance { text-wrap: balance; }
  .text-gradient { @apply bg-gradient-to-r from-primary-400 to-eco-400 bg-clip-text text-transparent; }
}
""",
    )

    # layout.tsx با فونت Vazirmatn
    write_file(
        WEB / "src" / "app" / "layout.tsx",
        """import "@/styles/globals.css";
import { Vazirmatn } from "next/font/google";
import { Metadata, Viewport } from "next";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { Toaster } from "@/components/ui/toaster";

const vazir = Vazirmatn({
  subsets: ["arabic", "latin"],
  variable: "--font-vazir",
  display: "swap",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: {
    default: "🌍 Econojin | ابرپروژه خدمات جامع رایگان",
    template: "%s | Econojin",
  },
  description: "پلتفرم رایگان کشاورزی، آموزش، محیط زیست، حسابداری و جامعه با هوش مصنوعی",
  keywords: ["کشاورزی", "هوش مصنوعی", "محیط زیست", "آموزش", "اقتصاد", "ایران"],
  authors: [{ name: "Econojin Team" }],
  manifest: "/manifest.json",
  icons: {
    icon: "/icons/icon-192.png",
    apple: "/icons/icon-192.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#0f172a",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" className={vazir.variable} suppressHydrationWarning>
      <body className="font-sans bg-slate-900 text-slate-100 antialiased min-h-screen">
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
""",
    )


# ============================================================================
# ۳. کامپوننت‌های UI پایه (مشابه Shadcn/UI اما ساده‌شده)
# ============================================================================


def generate_ui_components():
    """تولید کتابخانه کامپوننت‌های UI"""

    components_dir = WEB / "src" / "components" / "ui"

    # Button
    write_file(
        components_dir / "button.tsx",
        """import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary-600 text-white hover:bg-primary-500 shadow-lg shadow-primary-500/25",
        secondary: "bg-slate-700 text-slate-100 hover:bg-slate-600",
        outline: "border border-slate-600 bg-transparent hover:border-primary-500 hover:text-primary-400",
        ghost: "hover:bg-slate-800 text-slate-300",
        link: "text-primary-400 underline-offset-4 hover:underline",
        eco: "bg-eco-600 text-white hover:bg-eco-500 shadow-lg shadow-eco-500/25",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-6 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
""",
    )

    # Card
    write_file(
        components_dir / "card.tsx",
        """import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("rounded-xl border border-slate-700 bg-card text-card-foreground shadow-lg", className)} {...props} />
  )
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6 pb-3", className)} {...props} />
  )
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
  )
);
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn("text-sm text-slate-400", className)} {...props} />
  )
);
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  )
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-6 pt-0", className)} {...props} />
  )
);
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
""",
    )

    # Input
    write_file(
        components_dir / "input.tsx",
        """import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
""",
    )

    # Badge
    write_file(
        components_dir / "badge.tsx",
        """import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary-600 text-white hover:bg-primary-500",
        secondary: "border-transparent bg-slate-700 text-slate-100 hover:bg-slate-600",
        success: "border-transparent bg-success-500/10 text-success-400 hover:bg-success-500/20",
        warning: "border-transparent bg-warning-500/10 text-warning-400 hover:bg-warning-500/20",
        danger: "border-transparent bg-danger-500/10 text-danger-400 hover:bg-danger-500/20",
        outline: "text-slate-300 border-slate-600",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
""",
    )

    # utils helper
    write_file(
        WEB / "src" / "lib" / "utils.ts",
        """import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number, decimals: number = 0): string {
  return new Intl.NumberFormat("fa-IR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(num);
}

export function formatCurrency(amount: number, currency: "IRR" | "USD" = "IRR"): string {
  return new Intl.NumberFormat("fa-IR", {
    style: "currency",
    currency: currency === "IRR" ? "IRR" : "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: currency === "USD" ? 2 : 0,
  }).format(amount);
}

export function formatDate(date: Date | string, format: "short" | "long" = "short"): string {
  const d = new Date(date);
  return new Intl.DateTimeFormat("fa-IR", {
    year: "numeric",
    month: "short",
    day: "numeric",
    ...(format === "long" && { hour: "2-digit", minute: "2-digit" }),
  }).format(d);
}
""",
    )

    # clsx و tailwind-merge (وابستگی‌های لازم)
    # کاربر باید این‌ها را نصب کند: npm install clsx tailwind-merge

    print("✅ کامپوننت‌های UI ایجاد شدند.")


# ============================================================================
# ۴. لایه سرویس API و مدیریت وضعیت
# ============================================================================


def generate_services_and_store():
    """تولید سرویس‌های API و Zustand store"""

    # API service base
    write_file(
        WEB / "src" / "lib" / "api.ts",
        """import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: { "Content-Type": "application/json" },
      timeout: 30000,
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("econojin_token");
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    this.client.interceptors.response.use(
      (res) => res,
      (error) => {
        const apiError: ApiError = error.response?.data || {
          type: "network_error",
          title: "خطای شبکه",
          status: 0,
          detail: error.message,
        };
        console.error("API Error:", apiError);
        return Promise.reject(apiError);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.get(url, config);
    return res.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.post(url, data, config);
    return res.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.put(url, data, config);
    return res.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.delete(url, config);
    return res.data;
  }
}

export const api = new ApiClient(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

// سرویس‌های ماژول‌ها
export const healthService = {
  check: () => api.get<{ status: string; version: string }>("/api/v1/health"),
};

export const weatherService = {
  getForecast: (location: string, days: number = 7) => 
    api.get(`/api/v1/weather/forecast?location=${encodeURIComponent(location)}&days=${days}`),
  getAlerts: (region: string) => api.get(`/api/v1/weather/alerts?region=${encodeURIComponent(region)}`),
};

export const economicService = {
  simulateProfit: (data: any) => api.post("/api/v1/economic/simulate/profit", data),
  monteCarlo: (data: any, iterations?: number) => 
    api.post(`/api/v1/economic/simulate/montecarlo${iterations ? `?iterations=${iterations}` : ""}`, data),
  sensitivity: (base: any, param: string, rangePercent: number) =>
    api.post(`/api/v1/economic/sensitivity?param=${param}&range_percent=${rangePercent}`, base),
};

export const analysisService = {
  startStream: (query: string, region: string, crop?: string, area?: number) =>
    api.post("/api/v1/analyze/stream", { query, region, crop, area_ha: area }),
  getAnalyses: (limit: number = 20, region?: string) =>
    api.get(`/api/v1/analyses?limit=${limit}${region ? `&region=${encodeURIComponent(region)}` : ""}`),
};

export const gisService = {
  calculateArea: (coordinates: [number, number][]) =>
    api.post("/api/v1/gis/calculate/area", { coordinates }),
  getMapTiles: (z: number, x: number, y: number) =>
    api.get(`/api/v1/gis/map/tiles?z=${z}&x=${x}&y=${y}`),
};

export const ecominingService = {
  mine: (actionType: string, amount: number, location: string) =>
    api.post("/api/v1/ecomining/mine", { action_type: actionType, amount, location }),
  getBalance: () => api.get("/api/v1/ecomining/balance"),
};
""",
    )

    # Zustand store
    write_file(
        WEB / "src" / "store" / "useAppStore.ts",
        """import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AnalysisEvent {
  event_type: string;
  message: string;
  data?: any;
  timestamp: number;
}

export interface AppState {
  // UI State
  sidebarOpen: boolean;
  theme: "light" | "dark";
  currentModule: string | null;
  
  // Analysis State
  activeSession: string | null;
  analysisEvents: AnalysisEvent[];
  isAnalyzing: boolean;
  lastResult: any | null;
  
  // User State
  user: { name?: string; email?: string; role?: string } | null;
  token: string | null;
  
  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
  setCurrentModule: (module: string | null) => void;
  
  setSession: (sessionId: string) => void;
  addEvent: (event: AnalysisEvent) => void;
  setAnalyzing: (status: boolean) => void;
  setResult: (result: any) => void;
  clearAnalysis: () => void;
  
  login: (token: string, user?: any) => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial State
      sidebarOpen: true,
      theme: "dark",
      currentModule: null,
      activeSession: null,
      analysisEvents: [],
      isAnalyzing: false,
      lastResult: null,
      user: null,
      token: null,
      
      // UI Actions
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setTheme: (theme) => set({ theme }),
      setCurrentModule: (module) => set({ currentModule: module }),
      
      // Analysis Actions
      setSession: (sessionId) => set({ activeSession: sessionId }),
      addEvent: (event) => set((state) => ({ 
        analysisEvents: [...state.analysisEvents.slice(-49), event] // Keep last 50
      })),
      setAnalyzing: (status) => set({ isAnalyzing: status }),
      setResult: (result) => set({ lastResult: result }),
      clearAnalysis: () => set({ activeSession: null, analysisEvents: [], lastResult: null, isAnalyzing: false }),
      
      // Auth Actions
      login: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
    }),
    { name: "econojin-store", partialize: (state) => ({ theme, token, user }) }
  )
);
""",
    )

    # WebSocket hook
    write_file(
        WEB / "src" / "hooks" / "useAnalysisWebSocket.ts",
        """import { useEffect, useRef, useCallback } from "react";
import { useAppStore } from "@/store/useAppStore";

export function useAnalysisWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const { addEvent, setAnalyzing, setResult, clearAnalysis } = useAppStore();

  const connect = useCallback(() => {
    if (!sessionId) return;
    
    const url = `ws://localhost:8000/ws/analyze/${sessionId}`;
    wsRef.current = new WebSocket(url);
    
    wsRef.current.onopen = () => {
      console.log("✅ WebSocket connected");
      addEvent({ event_type: "connected", message: "✅ اتصال به سرور برقرار شد", timestamp: Date.now() });
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addEvent(data);
        
        if (data.event_type === "final") {
          setResult(data.data);
          setAnalyzing(false);
        } else if (data.event_type === "error") {
          setAnalyzing(false);
        }
      } catch (e) {
        console.error("WebSocket parse error:", e);
      }
    };
    
    wsRef.current.onclose = () => {
      console.log("🔌 WebSocket disconnected");
    };
    
    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      addEvent({ event_type: "error", message: "❌ خطا در اتصال WebSocket", timestamp: Date.now() });
      setAnalyzing(false);
    };
  }, [sessionId, addEvent, setAnalyzing, setResult]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (sessionId) {
      connect();
      return () => disconnect();
    }
  }, [sessionId, connect, disconnect]);

  return { connect, disconnect, isConnected: wsRef.current?.readyState === WebSocket.OPEN };
}
""",
    )

    print("✅ سرویس‌های API و Zustand store ایجاد شدند.")


# ============================================================================
# ۵. کامپوننت‌های Layout اصلی (Sidebar, Header, Navigation)
# ============================================================================


def generate_layout_components():
    """تولید کامپوننت‌های چیدمان اصلی"""

    layout_dir = WEB / "src" / "components" / "layout"

    # Sidebar
    write_file(
        layout_dir / "sidebar.tsx",
        """"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { 
  LayoutDashboard, CloudSun, Wallet, Calendar, ShoppingCart, BookOpen, 
  Monitor, GraduationCap, Map, Brain, Leaf, Users, Gamepad2, Settings, LogOut, Menu, X 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";

const modules = [
  { id: "dashboard", name: "داشبورد", icon: LayoutDashboard, href: "/" },
  { id: "weather", name: "هواشناسی", icon: CloudSun, href: "/weather" },
  { id: "accounting", name: "حسابداری", icon: Wallet, href: "/accounting" },
  { id: "calendar", name: "تقویم", icon: Calendar, href: "/calendar" },
  { id: "store", name: "فروشگاه", icon: ShoppingCart, href: "/store" },
  { id: "library", name: "کتابخانه", icon: BookOpen, href: "/library" },
  { id: "desktop", name: "میزکار", icon: Monitor, href: "/desktop" },
  { id: "education", name: "آموزش", icon: GraduationCap, href: "/education" },
  { id: "gis", name: "GIS", icon: Map, href: "/gis" },
  { id: "psychology", name: "روانشناسی", icon: Brain, href: "/psychology" },
  { id: "ecomining", name: "EcoCoin", icon: Leaf, href: "/ecomining" },
  { id: "community", name: "جامعه", icon: Users, href: "/community" },
  { id: "games", name: "بازی", icon: Gamepad2, href: "/games" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar, logout } = useAppStore();
  
  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleSidebar}
        />
      )}
      
      <motion.aside
        initial={false}
        animate={{ x: sidebarOpen ? 0 : "-100%" }}
        className={cn(
          "fixed lg:static inset-y-0 right-0 z-50 w-72 bg-slate-900 border-l border-slate-800 flex flex-col transition-transform lg:translate-x-0",
          !sidebarOpen && "lg:hidden"
        )}
      >
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🌍</span>
            <span className="font-bold text-lg text-primary-400">Econojin</span>
          </Link>
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={toggleSidebar}>
            <X className="h-5 w-5" />
          </Button>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {modules.map((mod) => {
            const Icon = mod.icon;
            const isActive = pathname === mod.href;
            return (
              <Link
                key={mod.id}
                href={mod.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-primary-600/20 text-primary-400 border border-primary-500/30" 
                    : "text-slate-300 hover:bg-slate-800 hover:text-slate-100"
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                <span>{mod.name}</span>
              </Link>
            );
          })}
        </nav>
        
        {/* Footer */}
        <div className="p-4 border-t border-slate-800 space-y-2">
          <Link href="/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800 transition">
            <Settings className="h-5 w-5" />
            <span>تنظیمات</span>
          </Link>
          <button 
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-danger-400 hover:bg-danger-500/10 transition"
          >
            <LogOut className="h-5 w-5" />
            <span>خروج</span>
          </button>
        </div>
      </motion.aside>
    </>
  );
}
""",
    )

    # Header
    write_file(
        layout_dir / "header.tsx",
        """"use client";

import { Menu, Bell, Search, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/store/useAppStore";

export function Header() {
  const { toggleSidebar } = useAppStore();
  
  return (
    <header className="sticky top-0 z-30 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Mobile menu button */}
        <Button variant="ghost" size="icon" className="lg:hidden" onClick={toggleSidebar}>
          <Menu className="h-5 w-5" />
        </Button>
        
        {/* Search */}
        <div className="flex-1 max-w-xl mx-4">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <Input 
              placeholder="جستجو در ماژول‌ها، داده‌ها، مستندات..." 
              className="pr-10 bg-slate-800/50 border-slate-700"
            />
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 left-1 h-2 w-2 bg-danger-500 rounded-full" />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
""",
    )

    # Main layout wrapper
    write_file(
        WEB / "src" / "components" / "layout" / "main-layout.tsx",
        """"use client";

import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useAppStore();
  
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex">
      <Sidebar />
      <div className={cn(
        "flex-1 flex flex-col min-w-0 transition-all duration-300",
        sidebarOpen && "lg:mr-72"
      )}>
        <Header />
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
""",
    )

    print("✅ کامپوننت‌های Layout ایجاد شدند.")


# ============================================================================
# ۶. صفحه اصلی Dashboard با کارت‌های ماژول‌ها
# ============================================================================


def generate_dashboard_page():
    """تولید صفحه داشبورد اصلی"""

    write_file(
        WEB / "src" / "app" / "page.tsx",
        """"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  CloudSun, Wallet, Map, GraduationCap, Brain, Leaf, Users, Gamepad2,
  TrendingUp, Activity, AlertTriangle, CheckCircle2
} from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

const modules = [
  { 
    id: "weather", name: "هواشناسی", icon: CloudSun, color: "from-blue-500 to-cyan-500",
    desc: "پیش‌بینی ۷ روزه، هشدارهای کشاورزی، توصیه‌های آبیاری",
    status: "active", href: "/weather"
  },
  { 
    id: "accounting", name: "حسابداری", icon: Wallet, color: "from-emerald-500 to-green-500",
    desc: "مدیریت درآمد/هزینه، فاکتور، گزارش‌گیری مالی",
    status: "active", href: "/accounting"
  },
  { 
    id: "gis", name: "GIS و نقشه", icon: Map, color: "from-violet-500 to-purple-500",
    desc: "نقشه‌کشی، تحلیل مکانی، محاسبه مساحت و فرسایش",
    status: "active", href: "/gis"
  },
  { 
    id: "education", name: "آموزش", icon: GraduationCap, color: "from-orange-500 to-amber-500",
    desc: "کلاس‌های آنلاین، آزمون، گواهی‌نامه، وبینار",
    status: "beta", href: "/education"
  },
  { 
    id: "psychology", name: "روانشناسی", icon: Brain, color: "from-pink-500 to-rose-500",
    desc: "آزمون‌های بالینی، مشاوره، مدیتیشن، ردیاب خلق",
    status: "beta", href: "/psychology"
  },
  { 
    id: "ecomining", name: "EcoCoin", icon: Leaf, color: "from-lime-500 to-green-500",
    desc: "ماینینگ سبز، کیف پول، بازار اعتبار کربن",
    status: "coming-soon", href: "/ecomining"
  },
];

const stats = [
  { label: "تحلیل‌های انجام‌شده", value: "۱۲۷", icon: Activity, trend: "+۱۲٪" },
  { label: "میانگین NDVI", value: "۰.۶۲", icon: TrendingUp, trend: "پایدار" },
  { label: "هشدارهای فعال", value: "۳", icon: AlertTriangle, trend: "کاهش", trendGood: true },
  { label: "EcoCoin دریافتی", value: "۲۴۵", icon: CheckCircle2, trend: "+۴۵" },
];

export default function DashboardPage() {
  return (
    <MainLayout>
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="card-hover">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">{stat.label}</p>
                      <p className="text-2xl font-bold mt-1">{stat.value}</p>
                    </div>
                    <div className="p-2 bg-slate-800 rounded-lg">
                      <Icon className="h-5 w-5 text-primary-400" />
                    </div>
                  </div>
                  <div className="mt-2 flex items-center gap-1 text-xs">
                    <span className={stat.trendGood !== false ? "text-success-400" : "text-warning-400"}>
                      {stat.trend}
                    </span>
                    <span className="text-slate-500">نسبت به ماه قبل</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
      
      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {modules.map((mod, i) => {
          const Icon = mod.icon;
          return (
            <motion.div
              key={mod.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + i * 0.05 }}
            >
              <Link href={mod.href}>
                <Card className="card-hover h-full cursor-pointer group">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className={`p-2 rounded-lg bg-gradient-to-br ${mod.color} text-white`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      {mod.status === "active" && <Badge variant="success">فعال</Badge>}
                      {mod.status === "beta" && <Badge variant="warning">بتا</Badge>}
                      {mod.status === "coming-soon" && <Badge variant="outline">بزودی</Badge>}
                    </div>
                    <CardTitle className="mt-3 text-lg">{mod.name}</CardTitle>
                    <CardDescription className="text-sm">{mod.desc}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button variant="ghost" size="sm" className="w-full justify-start group-hover:text-primary-400 transition">
                      ورود به ماژول →
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          );
        })}
      </div>
      
      {/* Quick Actions */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>⚡ اقدامات سریع</CardTitle>
          <CardDescription>دسترسی سریع به پرکاربردترین ابزارها</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm">📊 تحلیل جدید</Button>
          <Button variant="outline" size="sm">🌤️ پیش‌بینی منطقه</Button>
          <Button variant="outline" size="sm">💰 محاسبه سود</Button>
          <Button variant="outline" size="sm">🗺️ نقشه فرسایش</Button>
          <Button variant="outline" size="sm">🌱 استخراج EcoCoin</Button>
        </CardContent>
      </Card>
    </MainLayout>
  );
}
""",
    )

    print("✅ صفحه Dashboard ایجاد شد.")


# ============================================================================
# ۷. صفحات نمونه ماژول‌ها (الگو برای سایر صفحات)
# ============================================================================


def generate_module_pages():
    """تولید صفحات نمونه برای ماژول‌های کلیدی"""

    app_dir = WEB / "src" / "app"

    # Weather module page
    write_file(
        app_dir / "weather" / "page.tsx",
        """"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { CloudSun, Thermometer, Droplets, Wind, AlertTriangle } from "lucide-react";
import { useState } from "react";

const mockForecast = [
  { day: "شنبه", temp: 22, rain: 10, humidity: 45 },
  { day: "یکشنبه", temp: 24, rain: 5, humidity: 40 },
  { day: "دوشنبه", temp: 26, rain: 0, humidity: 35 },
  { day: "سه‌شنبه", temp: 23, rain: 30, humidity: 60 },
  { day: "چهارشنبه", temp: 20, rain: 70, humidity: 75 },
  { day: "پنجشنبه", temp: 21, rain: 20, humidity: 50 },
  { day: "جمعه", temp: 25, rain: 0, humidity: 30 },
];

export default function WeatherPage() {
  const [location, setLocation] = useState("تهران");
  
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">🌤️ هواشناسی کشاورزی</h1>
            <p className="text-slate-400">پیش‌بینی و هشدارهای تخصصی برای کشاورزان</p>
          </div>
          <div className="flex gap-2">
            <Input 
              placeholder="نام منطقه..." 
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-48"
            />
            <Button>بررسی</Button>
          </div>
        </div>
        
        {/* Current Conditions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <Thermometer className="h-8 w-8 text-orange-400" />
              <div>
                <p className="text-sm text-slate-400">دمای فعلی</p>
                <p className="text-xl font-bold">۲۴°C</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <Droplets className="h-8 w-8 text-blue-400" />
              <div>
                <p className="text-sm text-slate-400">رطوبت</p>
                <p className="text-xl font-bold">۴۵٪</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <Wind className="h-8 w-8 text-cyan-400" />
              <div>
                <p className="text-sm text-slate-400">سرعت باد</p>
                <p className="text-xl font-bold">۱۲ km/h</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <AlertTriangle className="h-8 w-8 text-warning-400" />
              <div>
                <p className="text-sm text-slate-400">هشدارها</p>
                <p className="text-xl font-bold">۲ مورد</p>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Forecast Chart */}
        <Card>
          <CardHeader>
            <CardTitle>📈 پیش‌بینی ۷ روزه</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockForecast}>
                <XAxis dataKey="day" stroke="#94a3b8" />
                <YAxis yAxisId="left" stroke="#94a3b8" />
                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                <Line yAxisId="left" type="monotone" dataKey="temp" stroke="#f97316" name="دما (°C)" strokeWidth={2} />
                <Line yAxisId="right" type="monotone" dataKey="rain" stroke="#3b82f6" name="بارش (٪)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Agricultural Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>⚠️ هشدارهای کشاورزی</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 bg-warning-500/10 border border-warning-500/20 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-warning-400 mt-0.5" />
                <div>
                  <p className="font-medium text-warning-300">احتمال یخبندان</p>
                  <p className="text-sm text-slate-400">سه‌شب آینده دمای شبانه به ۲- درجه می‌رسد. پوشش گیاهان حساس توصیه می‌شود.</p>
                </div>
              </div>
            </div>
            <div className="p-3 bg-info-500/10 border border-info-500/20 rounded-lg">
              <div className="flex items-start gap-3">
                <CloudSun className="h-5 w-5 text-primary-400 mt-0.5" />
                <div>
                  <p className="font-medium text-primary-300">زمان آبیاری بهینه</p>
                  <p className="text-sm text-slate-400">فردا صبح با بارش ۳۰٪، نیاز به آبیاری کاهش می‌یابد.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
""",
    )

    # Accounting module page
    write_file(
        app_dir / "accounting" / "page.tsx",
        """"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Wallet, TrendingUp, TrendingDown, Plus, Download } from "lucide-react";

const incomeData = [
  { month: "فروردین", amount: 12500000 },
  { month: "اردیبهشت", amount: 18200000 },
  { month: "خرداد", amount: 15800000 },
  { month: "تیر", amount: 22100000 },
  { month: "مرداد", amount: 19500000 },
  { month: "شهریور", amount: 24300000 },
];

const expenseData = [
  { name: "آب", value: 35, color: "#3b82f6" },
  { name: "بذر و کود", value: 28, color: "#22c55e" },
  { name: "نیروی کار", value: 22, color: "#f59e0b" },
  { name: "تجهیزات", value: 10, color: "#8b5cf6" },
  { name: "سایر", value: 5, color: "#64748b" },
];

const recentTransactions = [
  { id: 1, type: "income", desc: "فروش گندم", amount: 45000000, date: "۱۴۰۳/۰۳/۱۵" },
  { id: 2, type: "expense", desc: "خرید کود", amount: 8500000, date: "۱۴۰۳/۰۳/۱۴" },
  { id: 3, type: "income", desc: "فروش جو", amount: 22000000, date: "۱۴۰۳/۰۳/۱۲" },
  { id: 4, type: "expense", desc: "هزینه آبیاری", amount: 3200000, date: "۱۴۰۳/۰۳/۱۰" },
];

export default function AccountingPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">💰 حسابداری کشاورزی</h1>
            <p className="text-slate-400">مدیریت مالی، فاکتور و گزارش‌گیری</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm"><Download className="h-4 w-4 ml-1" /> خروجی Excel</Button>
            <Button size="sm"><Plus className="h-4 w-4 ml-1" /> ثبت تراکنش</Button>
          </div>
        </div>
        
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">درآمد کل</p>
                  <p className="text-2xl font-bold text-success-400">۱۱۲,۴۰۰,۰۰۰ تومان</p>
                </div>
                <TrendingUp className="h-8 w-8 text-success-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">هزینه کل</p>
                  <p className="text-2xl font-bold text-danger-400">۴۸,۷۰۰,۰۰۰ تومان</p>
                </div>
                <TrendingDown className="h-8 w-8 text-danger-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">سود خالص</p>
                  <p className="text-2xl font-bold text-primary-400">۶۳,۷۰۰,۰۰۰ تومان</p>
                </div>
                <Wallet className="h-8 w-8 text-primary-400" />
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader><CardTitle>📊 روند درآمد ماهانه</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={incomeData}>
                  <XAxis dataKey="month" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" tickFormatter={(v) => `${v/1000000}M`} />
                  <Tooltip formatter={(v: number) => [`${v.toLocaleString("fa-IR")} تومان`, "درآمد"]} />
                  <Bar dataKey="amount" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader><CardTitle>🥧 توزیع هزینه‌ها</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={expenseData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {expenseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => [`${v}٪`, "سهم"]} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
        
        {/* Recent Transactions */}
        <Card>
          <CardHeader><CardTitle>📋 تراکنش‌های اخیر</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentTransactions.map((tx) => (
                <div key={tx.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${tx.type === "income" ? "bg-success-500/10" : "bg-danger-500/10"}`}>
                      {tx.type === "income" ? <TrendingUp className="h-4 w-4 text-success-400"/> : <TrendingDown className="h-4 w-4 text-danger-400"/>}
                    </div>
                    <div>
                      <p className="font-medium">{tx.desc}</p>
                      <p className="text-xs text-slate-500">{tx.date}</p>
                    </div>
                  </div>
                  <Badge variant={tx.type === "income" ? "success" : "danger"}>
                    {tx.type === "income" ? "+" : "-"}{Math.abs(tx.amount).toLocaleString("fa-IR")} تومان
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
""",
    )

    # GIS module page
    write_file(
        app_dir / "gis" / "page.tsx",
        """"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MapContainer, TileLayer, Circle, Popup, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { Map, Ruler, AlertTriangle, Download, Layers } from "lucide-react";

// Mock data for regions
const regions = [
  { id: 1, name: "سبزوار", lat: 36.214, lon: 57.683, ndvi: 0.62, erosion: 12, crop: "گندم" },
  { id: 2, name: "نیشابور", lat: 36.214, lon: 58.800, ndvi: 0.48, erosion: 28, crop: "جو" },
  { id: 3, name: "مشهد", lat: 36.297, lon: 59.606, ndvi: 0.55, erosion: 18, crop: "پنبه" },
  { id: 4, name: "تربت", lat: 35.274, lon: 59.215, ndvi: 0.38, erosion: 42, crop: "زعفران" },
];

function getNdviColor(v: number) {
  if (v > 0.5) return "#10b981";
  if (v > 0.3) return "#f59e0b";
  return "#ef4444";
}

export default function GisPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">🗺️ GIS و تحلیل مکانی</h1>
            <p className="text-slate-400">نقشه‌کشی، NDVI، فرسایش خاک و محاسبه مساحت</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm"><Layers className="h-4 w-4 ml-1" /> لایه‌ها</Button>
            <Button variant="outline" size="sm"><Download className="h-4 w-4 ml-1" /> خروجی</Button>
            <Button size="sm"><Ruler className="h-4 w-4 ml-1" /> اندازه‌گیری</Button>
          </div>
        </div>
        
        {/* Map */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Map className="h-5 w-5" />
              نقشه مناطق تحلیل‌شده
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[500px] rounded-lg overflow-hidden border border-slate-700">
              <MapContainer center={[36.0, 58.0]} zoom={7} scrollWheelZoom={false} className="h-full w-full">
                <TileLayer
                  attribution="&copy; OpenStreetMap"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {regions.map((r) => (
                  <Circle
                    key={r.id}
                    center={[r.lat, r.lon]}
                    pathOptions={{ 
                      color: getNdviColor(r.ndvi),
                      fillColor: getNdviColor(r.ndvi),
                      fillOpacity: 0.6 
                    }}
                    radius={20000}
                  >
                    <Tooltip direction="top">{r.name}</Tooltip>
                    <Popup>
                      <div className="text-slate-800 font-sans p-2" dir="rtl">
                        <strong>{r.name}</strong><br/>
                        محصول: {r.crop}<br/>
                        NDVI: <span className="font-bold">{r.ndvi}</span><br/>
                        فرسایش: <span className="font-bold">{r.erosion} تن/هکتار</span>
                      </div>
                    </Popup>
                  </Circle>
                ))}
              </MapContainer>
            </div>
          </CardContent>
        </Card>
        
        {/* Stats & Legend */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Legend */}
          <Card>
            <CardHeader><CardTitle>🎨 راهنمای رنگ NDVI</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-green-500"></div>
                <span className="text-sm">عالی (&gt;۰.۵)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-yellow-500"></div>
                <span className="text-sm">متوسط (۰.۳-۰.۵)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-red-500"></div>
                <span className="text-sm">ضعیف (&lt;۰.۳)</span>
              </div>
            </CardContent>
          </Card>
          
          {/* Critical Areas */}
          <Card className="lg:col-span-2">
            <CardHeader><CardTitle>⚠️ مناطق بحرانی فرسایش</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {regions.filter(r => r.erosion > 25).map((r) => (
                  <div key={r.id} className="flex items-center justify-between p-3 bg-danger-500/10 border border-danger-500/20 rounded-lg">
                    <div>
                      <p className="font-medium">{r.name}</p>
                      <p className="text-sm text-slate-400">فرسایش: {r.erosion} تن/هکتار</p>
                    </div>
                    <Badge variant="danger">نیاز به اقدام</Badge>
                  </div>
                ))}
                {regions.filter(r => r.erosion <= 25).length === 0 && (
                  <p className="text-slate-500 text-center py-4">هیچ منطقه بحرانی یافت نشد ✅</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
""",
    )

    # Create directory structure for other modules (empty pages as templates)
    otherModules = [
        "calendar",
        "store",
        "library",
        "desktop",
        "education",
        "psychology",
        "ecomining",
        "community",
        "games",
        "settings",
    ]
    for mod in otherModules:
        mod_dir = app_dir / mod
        mod_dir.mkdir(parents=True, exist_ok=True)
        write_file(
            mod_dir / "page.tsx",
            f'''"""use client";

import {{ MainLayout }} from "@/components/layout/main-layout";

export default function {mod.capitalize()}Page() {{
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">🚧 {mod}</h1>
          <p className="text-slate-400">این ماژول در حال توسعه است...</p>
        </div>
        <div className="p-8 text-center text-slate-500">
          <p className="text-lg mb-4">✨ به زودی</p>
          <p className="text-sm">این صفحه در نسخه‌های آینده تکمیل خواهد شد.</p>
        </div>
      </div>
    </MainLayout>
  );
}}
''',
        )

    print("✅ صفحات ماژول‌ها ایجاد شدند.")


# ============================================================================
# ۸. فایل‌های تکمیلی (manifest, providers, etc.)
# ============================================================================


def generate_support_files():
    """تولید فایل‌های پشتیبان و پیکربندی"""

    # manifest.json for PWA
    write_file(
        WEB / "public" / "manifest.json",
        json.dumps(
            {
                "name": "Econojin - ابرپروژه خدمات جامع",
                "short_name": "Eco",
                "description": "پلتفرم رایگان کشاورزی، آموزش، محیط زیست و جامعه",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#0f172a",
                "theme_color": "#0ea5e9",
                "orientation": "any",
                "icons": [
                    {
                        "src": "/icons/icon-192.png",
                        "sizes": "192x192",
                        "type": "image/png",
                        "purpose": "any maskable",
                    },
                    {
                        "src": "/icons/icon-512.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "any maskable",
                    },
                ],
                "categories": ["agriculture", "education", "finance", "environment"],
                "lang": "fa",
            },
            indent=2,
            ensure_ascii=False,
        ),
    )

    # Theme provider
    write_file(
        WEB / "src" / "components" / "providers" / "theme-provider.tsx",
        """"use client";

import * as React from "react";
import { useAppStore } from "@/store/useAppStore";

type Theme = "dark" | "light";

interface ThemeProviderProps {
  children: React.ReactNode;
  attribute?: string;
  defaultTheme?: Theme;
  enableSystem?: boolean;
}

export function ThemeProvider({ children, attribute = "class", defaultTheme = "dark", enableSystem = false }: ThemeProviderProps) {
  const { theme } = useAppStore();
  
  React.useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
  }, [theme]);
  
  return <>{children}</>;
}
""",
    )

    # Toaster component
    write_file(
        WEB / "src" / "components" / "ui" / "toaster.tsx",
        """"use client";

import { useAppStore } from "@/store/useAppStore";
import { X } from "lucide-react";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: "default" | "success" | "warning" | "danger";
}

export function Toaster() {
  // Placeholder - in real app, use sonner or react-hot-toast
  return null;
}
""",
    )

    # .gitignore for web
    write_file(
        WEB / ".gitignore",
        """# Dependencies
node_modules/
.pnpm-store/

# Build
.next/
out/

# Cache
.cache/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Env
.env*.local
""",
    )

    print("✅ فایل‌های پشتیبان ایجاد شدند.")


# ============================================================================
# تابع اصلی
# ============================================================================


def main():
    print("🎨 شروع تولید فرانت‌اند حرفه‌ای Econojin...")
    print(f"📁 مسیر: {WEB}")

    try:
        generate_config_files()
        generate_styles()
        generate_ui_components()
        generate_services_and_store()
        generate_layout_components()
        generate_dashboard_page()
        generate_module_pages()
        generate_support_files()

        print("\n" + "=" * 60)
        print("✅ تولید فرانت‌اند با موفقیت تکمیل شد!")
        print("=" * 60)
        print("\n📋 ساختار ایجاد‌شده:")
        print("   📁 web/src/app/          ← صفحات Next.js App Router")
        print("   📁 web/src/components/   ← کامپوننت‌های UI و Layout")
        print("   📁 web/src/modules/      ← کامپوننت‌های اختصاصی ماژول‌ها")
        print("   📁 web/src/lib/          ← سرویس‌های API و utilities")
        print("   📁 web/src/store/        ← Zustand state management")
        print("   📁 web/src/hooks/        ← هوک‌های سفارشی")
        print("   📁 web/src/styles/       ← استایل‌های سراسری")
        print("\n🚀 برای اجرا:")
        print(f"   cd {WEB}")
        print("   pnpm install  # یا npm install")
        print("   pnpm run dev")
        print("\n🔗 دسترسی: http://localhost:3000")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
