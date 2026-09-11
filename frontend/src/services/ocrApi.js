import api from './api';

export const ocrApi = {
  /**
   * Start or fetch OCR processing for a report.
   * @param {number} reportId
   * @param {boolean} forceRetry
   * @param {string|null} engine
   */
  startOcr: async (reportId, forceRetry = false, engine = null) => {
    const params = new URLSearchParams();
    if (forceRetry) params.append('force_retry', 'true');
    if (engine) params.append('engine', engine);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    const response = await api.post(`/ocr/${reportId}${queryString}`);
    return response.data;
  },

  /**
   * Fetch completed OCR results for a report.
   * @param {number} reportId
   * @param {number|null} version
   */
  getOcr: async (reportId, version = null) => {
    const params = version ? `?version=${version}` : '';
    const response = await api.get(`/ocr/${reportId}${params}`);
    return response.data;
  },

  /**
   * Reprocess OCR with forced cache bypass and optional engine.
   * @param {number} reportId
   * @param {string|null} engine
   */
  retryOcr: async (reportId, engine = null) => {
    const params = engine ? `?engine=${encodeURIComponent(engine)}` : '';
    const response = await api.post(`/ocr/${reportId}/retry${params}`);
    return response.data;
  },

  /**
   * Get normalized OCR blocks for a report.
   * @param {number} reportId
   * @param {number|null} version
   */
  getOcrBlocks: async (reportId, version = null) => {
    const params = version ? `?version=${version}` : '';
    const response = await api.get(`/ocr/${reportId}/blocks${params}`);
    return response.data;
  }
};

export default ocrApi;
