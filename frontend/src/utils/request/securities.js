import { httpClient } from '@/api/httpClient'
import {
  accountApiPrefix,
  buildOperator,
  fetchCustomerHttp,
  fetchSecuritiesAccountHttp,
  mapSecuritiesAccountHttp,
  normalizeAccountStatusValue,
  normalizeArrayResponse,
  wrapHttp,
} from './core'
import { submitOpenApplication } from './workflows'

export function getSecuritiesAccounts(params) {
  return wrapHttp(async () => {
    const normalizedAccountNo = String(params?.securitiesAccountNo || '').trim()
    const normalizedStatus = normalizeAccountStatusValue(params?.accountStatus)

    if (normalizedAccountNo) {
      const account = await fetchSecuritiesAccountHttp(normalizedAccountNo)
      if (normalizedStatus && normalizeAccountStatusValue(account.accountStatus) !== normalizedStatus) {
        return []
      }
      return [account]
    }

    const list = await httpClient.get(`${accountApiPrefix}/security-accounts`, {
      params: {
        investor_id: params?.investorId,
        account_status: normalizedStatus || undefined
      }
    })
    return Promise.all(normalizeArrayResponse(list).map(async item => {
      const customer = await fetchCustomerHttp(item.investor_id)
      return mapSecuritiesAccountHttp(item, customer)
    }))
  })
}

export function getSecuritiesAccountByNo(accountNo) {
  return wrapHttp(() => fetchSecuritiesAccountHttp(accountNo))
}

export function openSecuritiesAccount(data) {
  return submitOpenApplication(data)
}

export function reportSecuritiesAccountLost(data) {
  return wrapHttp(async () => {
    const payload = {
      customer_id_number: data.idNo,
      reason: data.reason || '客户申请挂失',
      ...buildOperator(data)
    }
    const account = await httpClient.post(`${accountApiPrefix}/security-accounts/${data.securitiesAccountNo}/lost`, payload)
    const customer = await fetchCustomerHttp(account.investor_id)
    return mapSecuritiesAccountHttp(account, customer)
  })
}

export function reissueSecuritiesAccount(data) {
  return wrapHttp(async () => {
    const payload = {
      customer_id_number: data.idNo,
      reason: data.reason || '客户申请补办',
      ...buildOperator(data)
    }
    const account = await httpClient.post(`${accountApiPrefix}/security-accounts/${data.securitiesAccountNo}/reissue`, payload)
    const customer = await fetchCustomerHttp(account.investor_id)
    return mapSecuritiesAccountHttp(account, customer)
  })
}

export function cancelSecuritiesAccount(data) {
  const payload = typeof data === 'string' ? { securitiesAccountNo: data } : data
  return wrapHttp(async () => {
    const result = await httpClient.delete(`${accountApiPrefix}/security-accounts/${payload.securitiesAccountNo}`, {
      data: {
        customer_id_number: payload.idNo,
        ...buildOperator(payload)
      }
    })
    const customer = await fetchCustomerHttp(result.investor_id)
    return mapSecuritiesAccountHttp(result, customer)
  })
}
