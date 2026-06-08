import { httpClient } from '@/api/httpClient'

const prefix = import.meta.env.VITE_ACCOUNT_PREFIX || '/api/v1/account'

export function accountLogin(data) {
  return httpClient.post(`${prefix}/auth/login`, data)
}

export function accountChangePassword(data) {
  return httpClient.post(`${prefix}/auth/password`, data)
}

export function resetFundPasswordByStaff(fundAccountId, data) {
  return httpClient.post(`${prefix}/fund-accounts/${encodeURIComponent(fundAccountId)}/password/reset`, data)
}

export function resetSecurityPasswordByStaff(securityAccountId, data) {
  return httpClient.post(`${prefix}/security-accounts/${encodeURIComponent(securityAccountId)}/password/reset`, data)
}

export function getFundAccount(fundAccountId) {
  return httpClient.get(`${prefix}/fund-accounts/${encodeURIComponent(fundAccountId)}`)
}

export function getAssociations(params) {
  return httpClient.get(`${prefix}/associations`, { params })
}

export function getAssociationHistory(params) {
  return httpClient.get(`${prefix}/associations/history`, { params })
}

export function checkAssociation(params) {
  return httpClient.get(`${prefix}/associations/check`, { params })
}

export function jointClose(data) {
  return httpClient.post(`${prefix}/joint-accounts/close`, data)
}

export function checkAccountStatus(data) {
  return httpClient.post(`${prefix}/status/check`, data)
}

export function changeAccountStatus(data) {
  return httpClient.post(`${prefix}/status/change`, data)
}

export function getOperationLogs(params) {
  return httpClient.get(`${prefix}/operation-logs`, { params })
}

export function createOperationLog(data) {
  return httpClient.post(`${prefix}/operation-logs`, data)
}
