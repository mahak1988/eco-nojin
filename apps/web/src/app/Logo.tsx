import React from 'react';
import Link from 'next/link';

interface LogoProps {
  locale?: string;
  size?: 'sm' | 'md' | 'lg';
  showTagline?: boolean;
}

function Logo({ locale = 'fa', size = 'md', showTagline = false }: LogoProps) {
  const sizes = {
    sm: { text: 'text-2xl', tag: 'text-xs', icon: 'w-6 h-6' },
    md: { text: 'text-3xl', tag: 'text-sm', icon: 'w-8 h-8' },
    lg: { text: 'text-5xl', tag: 'text-base', icon: 'w-12 h-12' },
  };
  
  const s = sizes[size];
  const isPersian = locale === 'fa';
  
  return (
    <Link href={`/${locale}`} className="inline-flex flex-col items-start group">
      <div className="flex items-center gap-2">
        {/* Leaf Icon */}
        <div className={`${s.icon} relative`}>
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="leafGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#22c55e" />
                <stop offset="100%" stopColor="#15803d" />
              </linearGradient>
            </defs>
            <path
              d="M16 2C10 6 6 12 6 18C6 24 10 28 16 30C22 28 26 24 26 18C26 12 22 6 16 2Z"
              fill="url(#leafGradient)"
            />
            <path
              d="M16 8V24M12 14L16 10L20 14"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        
        {/* Typography Logo */}
        <div className="flex flex-col leading-none">
          <span 
            className={`${s.text} font-black tracking-tight bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 bg-clip-text text-transparent group-hover:from-green-500 group-hover:to-teal-500 transition-all`}
            style={{
              fontFamily: isPersian ? 'Vazirmatn, sans-serif' : 'Inter, sans-serif',
              letterSpacing: isPersian ? '0' : '-0.02em',
            }}
          >
            {isPersian ? 'اکونوژین' : 'Econojin'}
          </span>
          {showTagline && (
            <span className={`${s.tag} text-gray-500 font-medium mt-1`}>
              {isPersian ? 'پلتفرم علمی کربن' : 'Scientific Carbon Platform'}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}


export default React.memo(Logo);
