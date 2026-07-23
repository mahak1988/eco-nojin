// apps/web/src/components/account/Toggle.tsx
// سوئیچ RTL-safe — موقعیت دستگیره با insetInlineStart کنترل می‌شود.
interface Props {
  checked: boolean;
  onChange: (v: boolean) => void;
  ariaLabel?: string;
}

export function Toggle({ checked, onChange, ariaLabel }: Props) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={ariaLabel}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500/40 ${
        checked ? "bg-green-600" : "bg-stone-300"
      }`}
    >
      <span
        className="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all duration-300"
        style={{ insetInlineStart: checked ? "calc(100% - 1.375rem)" : "0.125rem" }}
      />
    </button>
  );
}