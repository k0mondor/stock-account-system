import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || ''

export const httpClient = axios.create({
  baseURL,
  timeout: 10000
})

httpClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token && !config.headers?.Authorization) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

httpClient.interceptors.response.use(
  response => {
    const body = response?.data
    if (body && typeof body === 'object' && Object.prototype.hasOwnProperty.call(body, 'success')) {
      if (body.success) return body.data
      const err = new Error(body.message || '请求失败')
      err.code = body.code
      err.requestId = body.request_id
      throw err
    }
    return body
  },
  error => Promise.reject(error)
)

