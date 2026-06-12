import api from '@/lib/api/client';

export const academyApi = {
  getStats: async () => {
    try {
      const response = await api.get('/api/v1/academy/statistics');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch academy stats:', error);
      throw error;
    }
  },
  
  getCourses: async (params?: { category?: string; level?: string }) => {
    try {
      const response = await api.get('/api/v1/academy/courses', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch courses:', error);
      throw error;
    }
  },
  
  getCourse: async (id: number) => {
    try {
      const response = await api.get(`/api/v1/academy/courses/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch course ${id}:`, error);
      throw error;
    }
  },
  
  getCategories: async () => {
    try {
      const response = await api.get('/api/v1/academy/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  },
  
  getStandards: async () => {
    try {
      const response = await api.get('/api/v1/academy/standards');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch standards:', error);
      throw error;
    }
  },
};
