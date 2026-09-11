import api from './api';

export const userApi = {
  getProfile: async () => {
    const response = await api.get('/users/me');
    return response.data;
  }
};

export default userApi;
