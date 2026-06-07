import createIntlMiddleware from "next-intl/middleware";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { routing } from "@/i18n/routing";

const intlMiddleware = createIntlMiddleware(routing);

const PROTECTED = ["farmers", "accounting", "calendar", "settings"];

export default function middleware(request: NextRequest) {
  const response = intlMiddleware(request);
  const pathname = request.nextUrl.pathname;
  const segments = pathname.split("/").filter(Boolean);
  const locale = segments[0];
  const pathAfterLocale =
    routing.locales.includes(locale as "fa" | "en")
      ? "/" + segments.slice(1).join("/")
      : pathname;

  const isAuthPage =
    pathAfterLocale.startsWith("/login") ||
    pathAfterLocale.startsWith("/register");
  const isHome = pathAfterLocale === "/" || pathAfterLocale === "";

  if (!isAuthPage && !isHome) {
    const needsAuth = PROTECTED.some(
      (p) =>
        pathAfterLocale === `/${p}` || pathAfterLocale.startsWith(`/${p}/`)
    );
    const token = request.cookies.get("econojin_token")?.value;
    if (needsAuth && !token) {
      const loginUrl = new URL(`/${locale || "fa"}/login`, request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  if (response) {
    response.headers.set("X-Frame-Options", "DENY");
    response.headers.set("X-Content-Type-Options", "nosniff");
  }
  return response;
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
