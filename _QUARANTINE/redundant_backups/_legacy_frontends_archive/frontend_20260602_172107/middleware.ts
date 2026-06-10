import { NextRequest, NextResponse } from 'next/server';

export const locales = ['fa', 'en', 'ar', 'tr', 'zh', 'es', 'fr', 'de', 'ru', 'ja', 'ko', 'it', 'pt', 'nl', 'pl', 'sv', 'hi', 'ur', 'id', 'ms'];
export const defaultLocale = 'fa';

function getLocale(request: NextRequest): string {
  const localeCookie = request.cookies.get('NEXT_LOCALE')?.value;
  if (localeCookie && locales.includes(localeCookie as any)) {
    return localeCookie;
  }
  
  const acceptLanguage = request.headers.get('accept-language') || '';
  for (const locale of locales) {
    if (acceptLanguage.includes(locale)) {
      return locale;
    }
  }
  
  return defaultLocale;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') ||
    pathname.startsWith('/favicon')
  ) {
    return NextResponse.next();
  }
  
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );
  
  if (pathnameHasLocale) {
    return NextResponse.next();
  }
  
  const locale = getLocale(request);
  request.nextUrl.pathname = `/${locale}${pathname}`;
  
  const response = NextResponse.redirect(request.nextUrl);
  response.cookies.set('NEXT_LOCALE', locale, { path: '/' });
  
  return response;
}

export const config = {
  matcher: ['/((?!_next|api|favicon|.*\\..*).*)'],
};
