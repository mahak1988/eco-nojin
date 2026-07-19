import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

const sizeMap = {
  sm: { icon: 32, text: 20, tagline: 10 },
  md: { icon: 48, text: 28, tagline: 12 },
  lg: { icon: 64, text: 36, tagline: 14 },
};

const leafVariants = {
  hidden: { pathLength: 0, opacity: 0 },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: { duration: 1.5, ease: "easeInOut" as const },
  },
};

const dropVariants = {
  animate: {
    y: [0, 10, 0],
    opacity: [0.6, 0.2, 0.6],
    transition: { duration: 2, repeat: Infinity, ease: "easeInOut" as const },
  },
};

const sunVariants = {
  animate: {
    r: [6, 8, 6],
    opacity: [0.8, 1, 0.8],
    transition: { duration: 3, repeat: Infinity, ease: "easeInOut" as const },
  },
};

export const AnimatedLogo: React.FC<AnimatedLogoProps> = ({ size = 'md', showText = true }) => {
  const s = sizeMap[size];

  return (
    <motion.div
      className="flex items-center gap-3"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Animated Icon */}
      <svg
        width={s.icon}
        height={s.icon}
        viewBox="0 0 80 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Stem */}
        <motion.path
          d="M40 70 Q40 40 40 20"
          stroke="#22c55e"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
          variants={leafVariants}
          initial="hidden"
          animate="visible"
        />
        {/* Left leaf */}
        <motion.path
          d="M40 40 Q20 30 15 15 Q25 20 40 25"
          fill="#22c55e"
          opacity={0.9}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        />
        {/* Right leaf */}
        <motion.path
          d="M40 30 Q55 20 60 5 Q50 15 40 20"
          fill="#16a34a"
          opacity={0.7}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        />
        {/* Top leaf */}
        <motion.path
          d="M40 20 Q30 10 35 2 Q40 8 40 15"
          fill="#15803d"
          opacity={0.8}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.7, duration: 0.5 }}
        />
        {/* Water drop */}
        <motion.ellipse
          cx="25"
          cy="65"
          rx="4"
          ry="6"
          fill="#3b82f6"
          opacity={0.6}
          variants={dropVariants}
          animate="animate"
        />
        {/* Sun */}
        <motion.circle
          cx="55"
          cy="10"
          r="6"
          fill="#f59e0b"
          opacity={0.8}
          variants={sunVariants}
          animate="animate"
        />
      </svg>

      {/* Text */}
      {showText && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <div
            className="font-bold"
            style={{
              fontSize: s.text,
              background: 'linear-gradient(135deg, #166534, #15803d, #16a34a)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Eco<span style={{ color: '#059669', WebkitTextFillColor: '#059669' }}>Nojin</span>
          </div>
          <div
            className="text-gray-500 tracking-widest"
            style={{ fontSize: s.tagline, letterSpacing: '2px' }}
          >
            پلتفرم جامع کشاورزی و محیط زیست
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default AnimatedLogo;