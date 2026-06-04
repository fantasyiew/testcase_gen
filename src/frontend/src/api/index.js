import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export const featureApi = {
  getAll: () => api.get('/features'),
  uploadDoc: (formData) => api.post('/features/upload', formData),
  getUploadedDocs: () => api.get('/features/uploaded-docs'),
  extract: (docPath) => api.post('/features/extract', { doc_path: docPath }),
  delete: (id) => api.delete(`/features/${id}`),
  clear: () => api.post('/features/clear'),
  getTestCases: (featureId) => api.get(`/features/${featureId}/test-cases`),
}

export const testCaseApi = {
  generate: (featureName) => api.post('/test-cases/generate', { doc_path: featureName }),
  generateAll: () => api.post('/test-cases/generate-all'),
  save: (featureId, testCases) => api.post('/test-cases/save', { feature_id: featureId, test_cases: testCases }),
  getStats: () => api.get('/test-cases/stats'),
  delete: (caseId) => api.delete(`/test-cases/${caseId}`),
  deleteByFeature: (featureId) => api.delete(`/test-cases/feature/${featureId}`),
}

export default api
