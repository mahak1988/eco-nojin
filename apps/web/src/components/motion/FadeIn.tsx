/**
 * FadeIn — reusable entrance animation (respects reduced-motion)
 */

import { motion, type HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";

export interface FadeInProps extends Omit<HTMLMotionProps<"div">, "children"> {
  children: ReactNode;
  delay?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  duration?: number;
}

const OFFSET = 24;

const directionOffset = {
  up: { y: OFFSET },
  down: { y: -OFFSET },
  left: { x: OFFSET },
  right: { x: -OFFSET },
  none: {},
};

export function FadeIn({
  children,
  delay = 0,
  direction = "up",
  duration = 0.5,
  className,
  ...props
}: FadeInProps): JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, ...directionOffset[direction] }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}
