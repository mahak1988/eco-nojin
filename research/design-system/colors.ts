/**
 * Eco Nozhin Design System - Colors
 */

export const natureColors = {
  forest: {
    50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 300: '#86efac',
    400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d',
    800: '#166534', 900: '#14532d', 950: '#052e16',
  },
  ocean: {
    50: '#f0f9ff', 100: '#e0f2fe', 200: '#bae6fd', 300: '#7dd3fc',
    400: '#38bdf8', 500: '#0ea5e9', 600: '#0284c7', 700: '#0369a1',
    800: '#075985', 900: '#0c4a6e', 950: '#082f49',
  },
  earth: {
    50: '#fdf8f3', 100: '#f9edd9', 200: '#f2d9b3', 300: '#e9be83',
    400: '#df9d52', 500: '#d88332', 600: '#c96b27', 700: '#a75322',
    800: '#864322', 900: '#6d381e', 950: '#3b1b0e',
  },
  sunset: {
    50: '#fffbeb', 100: '#fef3c7', 200: '#fde68a', 300: '#fcd34d',
    400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309',
    800: '#92400e', 900: '#78350f', 950: '#451a03',
  },
  flower: {
    50: '#fdf2f8', 100: '#fce7f3', 200: '#fbcfe8', 300: '#f9a8d4',
    400: '#f472b6', 500: '#ec4899', 600: '#db2777', 700: '#be185d',
    800: '#9d174d', 900: '#831843',
  },
  lavender: {
    50: '#faf5ff', 100: '#f3e8ff', 200: '#e9d5ff', 300: '#d8b4fe',
    400: '#c084fc', 500: '#a855f7', 600: '#9333ea', 700: '#7e22ce',
    800: '#6b21a8', 900: '#581c87',
  },
};

export const regionalColors = {
  middleEast: {
    primary: '#1C39BB', secondary: '#40E0D0', accent: '#F4C430',
    nature: '#5A7D5A', desert: '#C9A87C', pomegranate: '#C0362C',
  },
  eastAsia: {
    primary: '#BC002D', secondary: '#D4AF37', accent: '#00A86B',
    sakura: '#FFB7C5', bamboo: '#7C9A6D',
  },
  africa: {
    primary: '#8B7355', secondary: '#D4A574', accent: '#FF6B35',
    nile: '#4A90A4', earth: '#6B4423',
  },
  southAmerica: {
    primary: '#2D5016', secondary: '#FF6B35', accent: '#FFD700',
    jungle: '#228B22', orchid: '#DA1884',
  },
  europe: {
    primary: '#4A7C59', secondary: '#006994', accent: '#967BB6',
    olive: '#808000', vineyard: '#722F37',
  },
  oceania: {
    primary: '#FF7F50', secondary: '#00CED1', accent: '#F4A460',
    ocean: '#006994', palm: '#228B22',
  },
};

export const semanticColors = {
  success: natureColors.forest[500],
  warning: natureColors.sunset[500],
  error: '#EF4444',
  info: natureColors.ocean[500],
};

export const gradients = {
  nature: 'linear-gradient(135deg, #22c55e 0%, #0ea5e9 100%)',
  sunset: 'linear-gradient(135deg, #f59e0b 0%, #ec4899 100%)',
  ocean: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
  earth: 'linear-gradient(135deg, #d97706 0%, #92400e 100%)',
  forest: 'linear-gradient(135deg, #16a34a 0%, #166534 100%)',
  middleEast: 'linear-gradient(135deg, #1C39BB 0%, #40E0D0 100%)',
  eastAsia: 'linear-gradient(135deg, #BC002D 0%, #D4AF37 100%)',
  africa: 'linear-gradient(135deg, #8B7355 0%, #FF6B35 100%)',
  southAmerica: 'linear-gradient(135deg, #2D5016 0%, #FF6B35 100%)',
  europe: 'linear-gradient(135deg, #4A7C59 0%, #967BB6 100%)',
  oceania: 'linear-gradient(135deg, #FF7F50 0%, #00CED1 100%)',
};
