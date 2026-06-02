'use client';

import { useState } from 'react';
import { Heart } from 'lucide-react';
import { useWishlist } from '@/lib/supabase/hooks';

interface WishlistButtonProps {
  resourceId: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function WishlistButton({ resourceId, size = 'md' }: WishlistButtonProps) {
  const { isInWishlist, toggleWishlist, loading } = useWishlist();
  const [animating, setAnimating] = useState(false);

  const inWishlist = isInWishlist(resourceId);

  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    setAnimating(true);
    await toggleWishlist(resourceId);
    setTimeout(() => setAnimating(false), 300);
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`${sizes[size]} rounded-full flex items-center justify-center transition-all ${
        inWishlist
          ? 'bg-red-500 text-white shadow-lg'
          : 'bg-white/90 text-gray-700 hover:bg-red-50 hover:text-red-500'
      } ${animating ? 'scale-125' : 'scale-100'}`}
      title={inWishlist ? 'حذف از علاقه‌مندی‌ها' : 'افزودن به علاقه‌مندی‌ها'}
    >
      <Heart className={`${iconSizes[size]} ${inWishlist ? 'fill-current' : ''}`} />
    </button>
  );
}