import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || ''
const devBearerToken = import.meta.env.VITE_DEV_BEARER_TOKEN || ''
const staffSessionKey = 'current_staff_session'

function extractErrorMessage(payload) {
  if (!payload || typeof payload !== 'object') return ''
  if (typeof payload.message === 'string' && payload.message.trim()) return payload.message.trim()

  const detail = payload.detail
  if (Array.isArray(detail)) {
    return detail.map(item => item?.msg || JSON.stringify(item)).join('；')
  }
  if (detail && typeof detail === 'object') {
    return detail.message || JSON.stringify(detail)
  }
  if (typeof detail === 'string' && detail.trim()) {
    return detail.trim()
  }
  return ''
}

function buildApiError(message, payload = {}, fallback = {}) {
  const error = new Error(message || '请求失败')
  error.code = payload?.code || fallback.code
  error.requestId = payload?.request_id || fallback.requestId
  error.status = fallback.status
  return error
}

export const httpClient = axios.create({
  baseURL,
  timeout: 10000
})

httpClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token') || devBearerToken
  if (token && !config.headers?.Authorization) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  if (!config.headers?.['X-Staff-Id']) {
    try {
      const raw = localStorage.getItem(staffSessionKey)
      const staff = raw ? JSON.parse(raw) : null
      if (staff?.staff_id) {
        config.headers = config.headers || {}
        config.headers['X-Staff-Id'] = staff.staff_id
      }
    } catch {
      // Ignore malformed session cache and let backend return a clear auth error.
    }
  }
  return config
})

httpClient.interceptors.response.use(
  response => {
    const body = response?.data
    if (body && typeof body === 'object' && Object.prototype.hasOwnProperty.call(body, 'success')) {
      if (body.success) return body.data
      throw buildApiError(body.message || '请求失败', body, {
        status: response?.status
      })
    }
    return body
  },
  error => {
    const payload = error?.response?.data
    const wrapped = buildApiError(
      extractErrorMessage(payload) || error?.message || '请求失败',
      payload,
      {
        code: error?.code,
        requestId: error?.response?.headers?.['x-request-id'],
        status: error?.response?.status
      }
    )
    wrapped.cause = error
    return Promise.reject(wrapped)
  }
)

