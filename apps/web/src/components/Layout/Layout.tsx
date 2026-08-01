/** App shell: Header + main + Footer + global AI assistant + demo RoleSwitcher. */
import { Outlet } from "react-router-dom";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { useLang, getLanguageDir } from "../eco/i18n";
import { GlobalAiAssistant } from "../ai/GlobalAiAssistant";
import { RoleSwitcher } from "../rbac/RoleSwitcher";

export default function Layout() {
  const { lang } = useLang();
  const dir = getLanguageDir(lang);

  return (
    <div
      className="flex min-h-screen flex-col bg-stone-50 text-stone-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100"
      dir={dir}
    >
      <Header />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-12 pt-20 md:px-8">
        <Outlet />
      </main>
      <Footer />
      <GlobalAiAssistant />
      <RoleSwitcher />
    </div>
  );
}
