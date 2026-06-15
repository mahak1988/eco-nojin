import {NextRequest} from "next/server";
import createIntlMiddleware from "next-intl/middleware";
import {locales, defaultLocale} from "./routing";

const intlMiddleware = createIntlMiddleware({
  locales,
  defaultLocale
});

export default function middleware(request: NextRequest) {
  return intlMiddleware(request);
}

export const config = {
  // Match only internationalized pathnames
  matcher: ["/", "/(.*)"],
};
