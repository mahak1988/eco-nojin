import { useEffect, useRef, useCallback } from "react";

interface Particle {
  x: number; y: number;
  vx: number; vy: number;
  radius: number;
  alpha: number;
  delta: number;
}

interface Props {
  count?: number;
  color?: string;
  maxRadius?: number;
  speed?: number;
  className?: string;
  connectorColor?: string;
}

export default function ParticleBackground({
  count = 60,
  color = "107, 114, 128",
  maxRadius = 2.5,
  speed = 0.5,
  className = "",
  connectorColor = "rgba(107,114,128,0.06)",
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);

    // cache particles only once
    const stored = (canvas as unknown as Record<string, unknown>).__particles as Particle[] | undefined;
    let particles: Particle[];
    if (stored && stored.length === count) {
      particles = stored;
    } else {
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * speed,
        vy: (Math.random() - 0.5) * speed,
        radius: Math.random() * maxRadius + 0.5,
        alpha: Math.random() * 0.5 + 0.2,
        delta: (Math.random() - 0.5) * 0.008,
      }));
      (canvas as unknown as Record<string, unknown>).__particles = particles;
    }

    const animate = () => {
      ctx.clearRect(0, 0, w, h);

      particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha += p.delta;
        if (p.alpha <= 0.1 || p.alpha >= 0.7) p.delta *= -1;
        if (p.x < 0) p.x = w;
        if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h;
        if (p.y > h) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color},${p.alpha.toFixed(3)})`;
        ctx.fill();

        // connect nearby particles
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j];
          const dx = p.x - q.x;
          const dy = p.y - q.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = connectorColor;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      });

      animRef.current = requestAnimationFrame(animate);
    };

    animRef.current = requestAnimationFrame(animate);
  }, [count, color, maxRadius, speed, connectorColor]);

  useEffect(() => {
    draw();
    const onResize = () => {
      const canvas = canvasRef.current;
      if (canvas) (canvas as unknown as Record<string, unknown>).__particles = undefined;
      draw();
    };
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener("resize", onResize);
    };
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      aria-hidden="true"
    />
  );
}
