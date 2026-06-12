export default function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  return (
    <div dir={params.locale === "fa" ? "rtl" : "ltr"}>
      {children}
    </div>
  );
}