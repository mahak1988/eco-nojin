export const cn = (...classes: (string | undefined)[]) => classes.filter(Boolean).join(" ");
export const formatNumber = (n: number) => new Intl.NumberFormat("fa-IR").format(n);
