import api from './api';

/**
 * Upload a file with real upload progress tracking.
 * @param {File} file - The file to upload
 * @param {string} uploadSource - 'upload' | 'camera'
 * @param {function} onProgress - (percent: number) => void
 * @returns {Promise<ReportOut>}
 */
export const uploadFile = (file, uploadSource = 'upload', onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('upload_source', uploadSource);

  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(Math.min(percent, 99)); // Hold at 99 until server confirms
      }
    },
  }).then((res) => {
    if (onProgress) onProgress(100);
    return res.data;
  });
};

export default { uploadFile };
