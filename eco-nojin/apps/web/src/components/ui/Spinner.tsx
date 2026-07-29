export function Spinner({ className = "" }: { className?: string }) {
  return (
    <div
      className={`h-8 w-8 animate-spin rounded-full border-2 border-stone-200 border-t-emerald-600 ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}
