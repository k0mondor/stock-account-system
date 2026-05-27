import { httpClient } from '@/api/httpClient'

const prefix = import.meta.env.VITE_ACCOUNT_PREFIX || '/api/v1/account'

export function accountLogin(data) {
  return httpClient.post(`${prefix}/auth/login`, data)
}

export function accountChangePassword(data) {
  return httpClient.post(`${prefix}/auth/password`, data)
}

export function getFundAccount(fundAccountId) {
  return httpClient.get(`${prefix}/fund-accounts/${encodeURIComponent(fundAccountId)}`)
}

export function getAssociations(params) {
  return httpClient.get(`${prefix}/associations`, { params })
}

