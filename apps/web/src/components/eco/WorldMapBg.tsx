// apps/web/src/components/eco/WorldMapBg.tsx
export function WorldMapBg({ variant = "light" }: { variant?: "light" | "dark" }) {
  const opacity = variant === "light" ? 0.04 : 0.08;
  return (
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden" style={{ opacity }}>
      <svg viewBox="0 0 1000 500" className="h-full w-full" preserveAspectRatio="xMidYMid slice">
        {/* ساده‌شدهٔ قاره‌ها */}
        <ellipse cx="250" cy="180" rx="120" ry="80" fill="currentColor" className="text-green-800" />
        <ellipse cx="520" cy="160" rx="100" ry="90" fill="currentColor" className="text-green-800" />
        <ellipse cx="700" cy="200" rx="130" ry="100" fill="currentColor" className="text-green-800" />
        <ellipse cx="350" cy="320" rx="80" ry="70" fill="currentColor" className="text-green-800" />
        <ellipse cx="800" cy="350" rx="70" ry="50" fill="currentColor" className="text-green-800" />
        <ellipse cx="150" cy="350" rx="60" ry="40" fill="currentColor" className="text-green-800" />
      </svg>
    </div>
  );
}
