import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  console.log('Interceptor running. Token:', token); // Debugging line
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('Authorization header set:', config.headers.Authorization); // Debugging line
  }
  return config;
});

export const getImages = async (params) => {
  // Filter out null or empty params before sending
  const filteredParams = Object.entries(params).reduce((acc, [key, value]) => {
    if (value !== null && value !== '' && value !== undefined) {
      acc[key] = value;
    }
    return acc;
  }, {});

  const response = await apiClient.get('/images/', { params: filteredParams });
  return response.data;
};

export const getApiKeys = async () => {
  const response = await apiClient.get('/keys/');
  return response.data;
};

export const addApiKey = async (keyData) => {
  const response = await apiClient.post('/keys/', keyData);
  return response.data;
};

export const updateImageTags = async (id, tags) => {
  const response = await apiClient.put(`/images/${id}/tags`, { tags });
  return response.data;
};

export const deleteApiKey = async (id) => {
  const response = await apiClient.delete(`/keys/${id}`);
  return response.data;
};

export const addImage = async (imageData) => {
  const response = await apiClient.post('/images/', imageData);
  return response.data;
};

export const addBulkImages = async (bulkData) => {
  const response = await apiClient.post('/images/bulk', bulkData);
  return response.data;
};

export const deleteImage = async (id) => {
  const response = await apiClient.delete(`/images/${id}`);
  return response.data;
};

export const deleteImagesBulk = async (imageIds) => {
  const response = await apiClient.post('/images/bulk-delete', { image_ids: imageIds });
  return response.data;
};

export const addTagsToImagesBulk = async (imageIds, tags) => {
  const response = await apiClient.post('/images/bulk-add-tags', { image_ids: imageIds, tags: tags });
  return response.data;
};

export const getUsers = async () => {
  const response = await apiClient.get('/users/');
  return response.data;
};

export const deleteUser = async (userId) => {
  const response = await apiClient.delete(`/users/${userId}`);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get('/users/me');
  return response.data;
};

export const updateCurrentUser = async (userData) => {
  const response = await apiClient.put('/users/me', userData);
  return response.data;
};

export const renameImage = async (imageId, newFilename) => {
  const response = await apiClient.put(`/images/${imageId}/rename`, { filename: newFilename });
  return response.data;
};