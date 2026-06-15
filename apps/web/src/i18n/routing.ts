import {createSharedPathnamesNavigation} from "next-intl/navigation";

export const locales = ["fa", "en"] as const;
export const defaultLocale = "fa";

export type Locale = (typeof locales)[number];

export const {Link, redirect, usePathname, useRouter} =
  createSharedPathnamesNavigation({locales});
