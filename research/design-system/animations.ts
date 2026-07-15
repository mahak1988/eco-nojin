/**
 * Eco Nozhin Design System - Animations
 */

export const durations = {
  instant: '50ms', fast: '150ms', normal: '300ms',
  slow: '500ms', slower: '700ms', slowest: '1000ms',
};

export const easings = {
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  breeze: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  growth: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  water: 'cubic-bezier(0.45, 0.05, 0.55, 0.95)',
};

export const keyframes = {
  float: { '0%, 100%': { transform: 'translateY(0px)' }, '50%': { transform: 'translateY(-20px)' } },
  sway: { '0%, 100%': { transform: 'rotate(-2deg)' }, '50%': { transform: 'rotate(2deg)' } },
  grow: { '0%': { transform: 'scale(0.95)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
  pulse: { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.5' } },
  glow: { '0%, 100%': { boxShadow: '0 0 5px currentColor' }, '50%': { boxShadow: '0 0 20px currentColor' } },
  gradient: { '0%, 100%': { backgroundPosition: '0% 50%' }, '50%': { backgroundPosition: '100% 50%' } },
  rotate360: { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } },
  sdgGlow: { '0%, 100%': { boxShadow: '0 0 0 0 currentColor' }, '50%': { boxShadow: '0 0 20px 5px currentColor' } },
  harvest: { '0%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-10px) rotate(5deg)' }, '100%': { transform: 'translateY(0)' } },
  seedGrow: { '0%': { transform: 'scale(0)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
};

export const animations = {
  float: 'float 6s ease-in-out infinite',
  sway: 'sway 4s ease-in-out infinite',
  grow: 'grow 0.6s ease-out forwards',
  pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  glow: 'glow 2s ease-in-out infinite alternate',
  gradient: 'gradient 8s ease infinite',
  rotate360: 'rotate360 20s linear infinite',
  sdgGlow: 'sdgGlow 2s ease-in-out infinite',
  harvest: 'harvest 3s ease-in-out infinite',
  seedGrow: 'seedGrow 1s ease-out forwards',
};
