// ============================================================
// API Service — Axios client for FastAPI backend
// File: src/services/api.js
// ============================================================

import axios from 'axios'

const API = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// --- Campaigns ---
export const campaignAPI = {
  list: (page = 1, pageSize = 20) =>
    API.get(`/campaigns/?page=${page}&page_size=${pageSize}`),

  get: (id) => API.get(`/campaigns/${id}`),

  create: (data) => API.post('/campaigns/', data),

  update: (id, data) => API.patch(`/campaigns/${id}`, data),

  delete: (id) => API.delete(`/campaigns/${id}`),
}

// --- Contacts ---
export const contactAPI = {
  list: (campaignId, page = 1, pageSize = 50) =>
    API.get(`/contacts/${campaignId}?page=${page}&page_size=${pageSize}`),

  upload: (campaignId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return API.post(`/contacts/${campaignId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  addManual: (campaignId, data) =>
    API.post(`/contacts/${campaignId}/manual`, data),

  delete: (contactId) => API.delete(`/contacts/contact/${contactId}`),
}

// --- Calls ---
export const callAPI = {
  initiate: (contactId, campaignId) =>
    API.post('/calls/initiate', { contact_id: contactId, campaign_id: campaignId }),

  launchBatch: (campaignId, maxConcurrent = 10) =>
    API.post('/calls/batch', { campaign_id: campaignId, max_concurrent: maxConcurrent }),

  getStatus: (sessionId) => API.get(`/calls/status/${sessionId}`),

  listCampaignCalls: (campaignId, page = 1) =>
    API.get(`/calls/campaign/${campaignId}?page=${page}`),
}

// --- Reports ---
export const reportAPI = {
  generate: (campaignId) =>
    API.post('/reports/generate', { campaign_id: campaignId }),

  download: (filename) => `/api/v1/reports/download/${filename}`,
}

export default API
