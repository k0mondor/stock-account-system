import { httpClient } from '@/api/httpClient'
import {
  changeFundPassword as changeFundPasswordHttp,
  getFundAccountByNo as getFundAccountByNoHttp,
} from '@/services/accountService'
import {
  accountApiPrefix,
  buildOperator,
  fetchCustomerHttp,
  generateId,
  mapFundAccountHttp,
  mapFundTransactionHttp,
  normalizeArrayResponse,
  toNumber,
  wrapHttp,
} from './core'

export function getFundAccountByNo(accountNo) {
  return wrapHttp(async () => {
    const normalizedAccountNo = String(accountNo || '').trim()
    const account = await getFundAccountByNoHttp(normalizedAccountNo)
    const customer = await fetchCustomerHttp(account.investorId)
    return mapFundAccountHttp(account, customer)
  })
}

export function getFundTransactions(params) {
  return wrapHttp(async () => {
    const fundAccountNo = String(params?.fundAccountNo || '').trim()
    const result = await httpClient.get(`${accountApiPrefix}/fund-accounts/${fundAccountNo}/transactions`, {
      params: {
        page: params?.page || 1,
        page_size: params?.pageSize || 20
      }
    })
    const items = normalizeArrayResponse(result?.items ? result : result?.data ? result.data : result)
    return {
      items: items.map(mapFundTransactionHttp),
      page: result.page,
      pageSize: result.page_size,
      total: result.total
    }
  })
}

export function deposit(data) {
  return wrapHttp(async () => {
    const fundAccountNo = String(data.fundAccountNo || '').trim()
    const payload = {
      amount: data.amount,
      business_order_id: data.businessOrderId || generateId('DEP'),
      reason: data.reason || '柜台存款',
      ...buildOperator(data)
    }
    const transaction = await httpClient.post(`${accountApiPrefix}/fund-accounts/${fundAccountNo}/deposits`, payload)
    return {
      availableBalance: toNumber(transaction.available_amount),
      serialNo: transaction.transaction_id,
      transactionId: transaction.transaction_id
    }
  })
}

export function withdraw(data) {
  return wrapHttp(async () => {
    const fundAccountNo = String(data.fundAccountNo || '').trim()
    const payload = {
      amount: data.amount,
      withdraw_password: data.password,
      business_order_id: data.businessOrderId || generateId('WTD'),
      reason: data.reason || '柜台取款',
      ...buildOperator(data)
    }
    const transaction = await httpClient.post(`${accountApiPrefix}/fund-accounts/${fundAccountNo}/withdrawals`, payload)
    return {
      availableBalance: toNumber(transaction.available_amount),
      serialNo: transaction.transaction_id,
      transactionId: transaction.transaction_id
    }
  })
}

export function reportFundAccountLost(data) {
  return wrapHttp(async () => {
    const fundAccountNo = String(data.fundAccountNo || '').trim()
    const payload = {
      customer_id_number: data.idNo,
      reason: data.reason || '客户申请挂失',
      ...buildOperator(data)
    }
    const account = await httpClient.post(`${accountApiPrefix}/fund-accounts/${fundAccountNo}/lost`, payload)
    const customer = await fetchCustomerHttp(account.investor_id)
    const mapped = await getFundAccountByNoHttp(account.fund_account_id)
    return mapFundAccountHttp(mapped, customer)
  })
}

export function reissueFundAccount(data) {
  return wrapHttp(async () => {
    const fundAccountNo = String(data.fundAccountNo || '').trim()
    const payload = {
      customer_id_number: data.idNo,
      reason: data.reason || '客户申请补办',
      ...buildOperator(data)
    }
    const account = await httpClient.post(`${accountApiPrefix}/fund-accounts/${fundAccountNo}/reissue`, payload)
    const customer = await fetchCustomerHttp(account.investor_id)
    const mapped = await getFundAccountByNoHttp(account.fund_account_id)
    return mapFundAccountHttp(mapped, customer)
  })
}

export function changeFundPassword(data) {
  return changeFundPasswordHttp(data).then(() => ({
    code: 200,
    message: 'success',
    data: { fundAccountNo: data.fundAccountNo, status: 'SUCCESS' }
  }))
}

export function cancelFundAccount(data) {
  const payload = typeof data === 'string' ? { fundAccountNo: data } : data
  return wrapHttp(async () => {
    const fundAccountNo = String(payload.fundAccountNo || '').trim()
    const result = await httpClient.delete(`${accountApiPrefix}/fund-accounts/${fundAccountNo}`, {
      data: {
        customer_id_number: payload.idNo,
        ...buildOperator(payload)
      }
    })
    const customer = await fetchCustomerHttp(result.investor_id)
    const mapped = await getFundAccountByNoHttp(result.fund_account_id)
    return mapFundAccountHttp(mapped, customer)
  })
}
