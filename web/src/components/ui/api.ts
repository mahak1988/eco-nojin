export const api = {
  get: async (url: string) => fetch(`http://localhost:8000${url}`).then(r => r.json()),
  post: async (url: string, data: any) => fetch(`http://localhost:8000${url}`, {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)
  }).then(r => r.json())
};
