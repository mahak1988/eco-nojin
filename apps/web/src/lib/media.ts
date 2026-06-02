import type { ModuleId } from "@/lib/modules";

/** Curated Unsplash imagery — agriculture / tech aesthetic */
export const MODULE_MEDIA: Record<
  ModuleId,
  { image: string; video?: string }
> = {
  weather: {
    image: "https://images.unsplash.com/photo-1504608524841-42fe6f008b4e?w=1200&q=80",
    video: "https://www.youtube.com/watch?v=1aZb5vXxV8Y",
  },
  accounting: {
    image: "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80",
  },
  calendar: {
    image: "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80",
  },
  gis: {
    image: "https://images.unsplash.com/photo-1569336321263-7174c1d5d789?w=1200&q=80",
  },
  education: {
    image: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1200&q=80",
    video: "https://www.youtube.com/watch?v=3fumBcKC6RE",
  },
  psychology: {
    image: "https://images.unsplash.com/photo-1499203531289-7f1b6f5b8f0e?w=1200&q=80",
  },
  ecomining: {
    image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200&q=80",
  },
  store: {
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80",
  },
  library: {
    image: "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=80",
  },
  desktop: {
    image: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&q=80",
  },
  community: {
    image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1200&q=80",
  },
  games: {
    image: "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1200&q=80",
  },
  settings: {
    image: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80",
  },
  farmers: {
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80",
    video: "https://www.youtube.com/watch?v=WmQl337Nqkk",
  },
};

export const HOME_HERO = {
  image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600&q=85",
  video: "https://www.youtube.com/watch?v=WmQl337Nqkk",
};
