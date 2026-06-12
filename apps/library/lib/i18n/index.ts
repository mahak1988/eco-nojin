import fa from './fa.json';
import en from './en.json';
import ar from './ar.json';
import tr from './tr.json';
import zh from './zh.json';
import es from './es.json';
import fr from './fr.json';
import de from './de.json';
import ru from './ru.json';
import ja from './ja.json';
import ko from './ko.json';
import it from './it.json';
import pt from './pt.json';
import nl from './nl.json';
import pl from './pl.json';
import sv from './sv.json';
import hi from './hi.json';
import ur from './ur.json';
import id from './id.json';
import ms from './ms.json';

export const dictionaries = {
  fa, en, ar, tr, zh, es, fr, de, ru, ja,
  ko, it, pt, nl, pl, sv, hi, ur, id, ms
}

export type Locale = keyof typeof dictionaries
export const defaultLocale: Locale = 'fa'
export const rtlLocales: Locale[] = ['fa', 'ar', 'ur']

export function getDictionary(locale: Locale) {
  return dictionaries[locale] || dictionaries[defaultLocale]
}

export function isRTL(locale: Locale): boolean {
  return rtlLocales.includes(locale)
}
