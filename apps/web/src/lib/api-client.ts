// API Client placeholder
const api = {
  get: async (url: string) => {
    try {
      const response = await fetch(url);
      return response.json();
    } catch {
      return null;
    }
  },
  post: async (url: string, data: any) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    } catch {
      return null;
    }
  },
  put: async (url: string, data: any) => {
    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    } catch {
      return null;
    }
  },
  delete: async (url: string) => {
    try {
      const response = await fetch(url, { method: 'DELETE' });
      return response.json();
    } catch {
      return null;
    }
  }
};

export default api;