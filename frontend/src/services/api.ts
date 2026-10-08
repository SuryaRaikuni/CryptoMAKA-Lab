const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = {
  async get(endpoint: string) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`API GET Error: ${res.statusText}`);
    return res.json();
  },
  
  async post(endpoint: string, data?: any) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!res.ok) throw new Error(`API POST Error: ${res.statusText}`);
    return res.json();
  }
};
