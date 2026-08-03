import { useEffect, useRef, useState, type ReactNode, type CSSProperties } from "react";

interface Props {
  children: ReactNode;
  speed?: number;       // smaller = more parallax (default 0.5)
  className?: string;
  style?: CSSProperties;
}

export default function ParallaxSection({ children, speed = 0.5, className = "", style }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const onScroll = () => {
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const viewH = window.innerHeight;
      if (rect.top < viewH && rect.bottom > 0) {
        const center = rect.top + rect.height / 2;
        const viewCenter = viewH / 2;
        setOffset((center - viewCenter) * speed);
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, [speed]);

  return (
    <div ref={ref} className={`relative overflow-hidden ${className}`} style={style}>
      <div
        className="relative"
        style={{ transform: `translateY(${offset * -0.3}px)` }}
      >
        {children}
      </div>
    </div>
  );
}
