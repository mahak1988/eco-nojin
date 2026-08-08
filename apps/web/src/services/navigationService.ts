import { CONTENT } from '../components/eco/i18n';
import { getFallbackNavigation, type FallbackNavigationConfig } from '../config/navigationFallback';

// Define the TypeScript interfaces based on the backend response
interface NavigationItem {
  id: string;
  title: string;
  slug: string;
  url: string;
  source: string;
  order: number;
  isActive: boolean;
  count?: number;
}

interface HeaderNavigationResponse {
  primaryMenu: NavigationItem[];
  topicCategories: NavigationItem[];
  meta: {
    degraded: boolean;
    sources: string[];
    failedSources?: string[];
  };
}

/**
 * Fetches dynamic navigation data from the backend API.
 * Includes primary menu and topic categories for the header.
 * Uses fallback data if the API request fails.
 * @returns Promise<HeaderNavigationResponse>
 */
export const fetchHeaderNavigation = async (): Promise<HeaderNavigationResponse> => {
  // Get the fallback navigation data from the config file
  const fallbackConfig: FallbackNavigationConfig = getFallbackNavigation();
  // Convert FallbackNavigationConfig to HeaderNavigationResponse format
  const fallbackData: HeaderNavigationResponse = {
    primaryMenu: fallbackConfig.primaryMenu,
    topicCategories: fallbackConfig.topicCategories,
    meta: {
      degraded: true,
      sources: [],
      failedSources: ['API'],
    },
  };

  try {
    // Read the API base URL from environment variables
    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const endpoint = `${apiUrl}/api/v1/navigation/header`;

    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // Add a timeout of 5 seconds
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      console.error(`Failed to fetch navigation: ${response.status} ${response.statusText}`);
      return fallbackData;
    }

    const data: HeaderNavigationResponse = await response.json();

    // Return the fetched data, ensuring fallback if needed
    // Ensure primaryMenu is not empty by merging with fallback if necessary
    const finalPrimaryMenu = data.primaryMenu.length > 0 ? data.primaryMenu : fallbackData.primaryMenu;

    return {
      primaryMenu: finalPrimaryMenu,
      topicCategories: data.topicCategories || fallbackData.topicCategories,
      meta: data.meta || fallbackData.meta,
    };

  } catch (error: any) {
    console.error('Error fetching navigation data:', error.message || error);
    // In case of network error, timeout, or parsing error, return the fallback data
    return fallbackData;
  }
};

// Type for the combined navigation structure used in the UI
export type CombinedNavigation = {
  mainNav: NavigationItem[];
  moreGroups: { label: string; items: NavigationItem[] }[];
};

/**
 * Combines the primary menu and topic categories into a structure
 * compatible with the existing Header component's expectations.
 * @param navData The data fetched from the API
 * @param lang The current language for translations
 * @returns CombinedNavigation
 */
export const combineNavigationData = (navData: HeaderNavigationResponse, lang: string): CombinedNavigation => {
  // Use the primary menu from the API as the main navigation
  const mainNav: NavigationItem[] = navData.primaryMenu;

  // Combine topic categories and other static/dynamic groups into moreGroups
  const moreGroups = [
    {
      // Use translation key if available, otherwise default label
      label: CONTENT[lang]?.['nav_group_topics'] || CONTENT.fa?.['nav_group_topics'] || 'Topics',
      items: [...navData.topicCategories].sort((a, b) => a.order - b.order), // Sort topic categories by order
    },
    // Add other groups from the fallback config if the API data is degraded
    // This is optional, depending on the desired behavior when parts of the API fail
    // For now, we focus on the dynamic topic categories from the API or its fallback
  ];

  return {
    mainNav,
    moreGroups,
  };
};