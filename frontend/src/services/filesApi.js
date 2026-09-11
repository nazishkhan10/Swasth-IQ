import api from './api';

export const getFiles = (params = {}) =>
  api.get('/files', { params }).then((r) => r.data);

export const getFileStats = () =>
  api.get('/files/stats').then((r) => r.data);

export const getFile = (id) =>
  api.get(`/files/${id}`).then((r) => r.data);

export const deleteFile = (id) =>
  api.delete(`/files/${id}`);

export default { getFiles, getFileStats, getFile, deleteFile };
