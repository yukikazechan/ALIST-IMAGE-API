import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export default {
  // Auth
  login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getMe() {
    return apiClient.get('/auth/me');
  },

  // Dashboard Stats
  getDashboardStats() {
    return apiClient.get('/admin/dashboard/stats');
  },

  // Sources & AList Sync
  getSources() {
    return apiClient.get('/admin/sources');
  },
  createSource(data) {
    return apiClient.post('/admin/sources', data);
  },
  syncSource(sourceId) {
    return apiClient.post(`/admin/sources/${sourceId}/sync`);
  },

  // Images
  getImages(params) {
    return apiClient.get('/admin/images', { params });
  },
  batchTagImages(data) {
    return apiClient.post('/admin/images/batch-tag', data);
  },

  // API Keys
  getApiKeys() {
    return apiClient.get('/admin/keys');
  },
  createApiKey(data) {
    return apiClient.post('/admin/keys', data);
  },
  deleteApiKey(keyId) {
    return apiClient.delete(`/admin/keys/${keyId}`);
  }
};
