/**
 * Fallback navigation configuration used when the API is unavailable.
 */

// Define the structure for navigation items
export interface NavigationItem {
  id: string;
  title: string;
  slug: string;
  url: string;
  source: string;
  order: number;
  isActive: boolean;
}

// Define the structure for grouped navigation items (like MORE_GROUPS)
export interface NavigationGroup {
  label: string;
  items: NavigationItem[];
}

// Define the overall fallback navigation structure
export interface FallbackNavigationConfig {
  primaryMenu: NavigationItem[];
  topicCategories: NavigationItem[];
  moreGroups: NavigationGroup[];
}

// The actual fallback configuration
export const NAVIGATION_FALLBACK_CONFIG: FallbackNavigationConfig = {
  primaryMenu: [
    { id: 'home', title: 'Home', slug: 'home', url: '/', source: 'static', order: 0, isActive: true },
    { id: 'courses', title: 'Courses', slug: 'courses', url: '/education', source: 'static', order: 1, isActive: true },
    { id: 'library', title: 'Library', slug: 'library', url: '/library', source: 'static', order: 2, isActive: true },
  ],
  topicCategories: [
    // Example topics - these would ideally match the default DB values
    { id: 'course:general', title: 'General', slug: 'general', url: '/education?category=general', source: 'course', order: 0, isActive: true },
    { id: 'library:resources', title: 'Resources', slug: 'resources', url: '/library?category=resources', source: 'library', order: 1, isActive: true },
  ],
  moreGroups: [
    {
      label: 'Topics',
      items: [
        { id: 'topic:general', title: 'General', slug: 'general', url: '/topics/general', source: 'static', order: 0, isActive: true },
        { id: 'topic:resources', title: 'Resources', slug: 'resources', url: '/topics/resources', source: 'static', order: 1, isActive: true },
      ]
    },
    {
      label: 'Monitoring',
      items: [
        { id: 'analytics', title: 'Analytics', slug: 'analytics', url: '/analytics', source: 'static', order: 0, isActive: true },
        { id: 'alerts', title: 'Alerts', slug: 'alerts', url: '/alerts', source: 'static', order: 1, isActive: true },
      ]
    },
    // Add more groups as needed
  ]
};

// Export a function to get the config, allowing for potential dynamic overrides later
export const getFallbackNavigation = (): FallbackNavigationConfig => {
  return NAVIGATION_FALLBACK_CONFIG;
};