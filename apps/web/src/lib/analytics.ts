// Analytics placeholder
export const analytics = {
  track: (event: string, data?: any) => {
    console.log('Analytics:', event, data);
  },
  page: (name: string) => {
    console.log('Page view:', name);
  }
};

export default analytics;