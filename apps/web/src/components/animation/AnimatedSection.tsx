import { useEffect, useRef, useState, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  className?: string;
  animation?: "fade-in" | "slide-up" | "slide-in-right" | "slide-in-left" | "scale-in";
  delay?: number;       // seconds
  threshold?: number;   // 0-1
  once?: boolean;
  as?: keyof JSX.IntrinsicElements;
}

export default function AnimatedSection({
  children,
  className = "",
  animation = "slide-up",
  delay = 0,
  threshold = 0.15,
  once = true,
  as: Tag = "div",
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          if (once) observer.unobserve(el);
        } else if (!once) {
          setInView(false);
        }
      },
      { threshold }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [once, threshold]);

  const animClass = inView ? `animate-${animation}` : "opacity-0";

  return (
    <Tag
      ref={ref as never}
      className={`${animClass} ${className}`}
      style={{ animationDelay: `${delay}s`, animationFillMode: "forwards" }}
    >
      {children}
    </Tag>
  );
}
