import { httpClient } from '@/api/httpClient'
import { resetSecurityPasswordByStaff as resetSecurityPasswordByStaffHttp } from '@/services/accountService'
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

export function getSecuritiesPositions(data) {
  return wrapHttp(async () => {
    const securitiesAccountNo = String(data?.securitiesAccountNo || '').trim()
    const result = await httpClient.get(`${accountApiPrefix}/security-accounts/${securitiesAccountNo}/positions`)
    const positions = normalizeArrayResponse(result?.positions ? result.positions : result)
    return positions.map(item => ({
      stockCode: item.stock_code,
      stockName: item.stock_name,
      totalQuantity: Number(item.total_quantity || 0),
      availableQuantity: Number(item.available_quantity || 0),
      frozenQuantity: Number(item.frozen_quantity || 0)
    }))
  })
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

export function resetSecurityPasswordByStaff(data) {
  return resetSecurityPasswordByStaffHttp(data).then(() => ({
    code: 200,
    message: 'success',
    data: {
      securitiesAccountNo: data.securitiesAccountNo,
      status: 'SUCCESS'
    }
  }))
}
