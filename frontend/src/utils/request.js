// src/utils/request.js
import axios from 'axios'
import { securitiesAccountList } from '@/mock/securities'
import { fundAccountList, transactionList } from '@/mock/fund'
import { associationList } from '@/mock/association'
import { AccountStatus, AssociationStatus, TransactionStatus, TransactionType } from '@/constants/enums'
import {
  changeFundPassword as changeFundPasswordHttp,
  getFundAccountByNo as getFundAccountByNoHttp,
  queryAssociations as queryAssociationsHttp,
  checkAssociationValid as checkAssociationValidHttp,
  bindAssociation as bindAssociationHttp,
  unbindAssociation as unbindAssociationHttp,
  checkStatus as checkStatusHttp,
  fetchOperationLogs as fetchOperationLogsHttp,
  writeOperationLog as writeOperationLogHttp,
} from '@/services/accountService'

const dataSource = import.meta.env.VITE_DATA_SOURCE || 'mock'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 3000
})

// 请求拦截器：标记 mock 请求
request.interceptors.request.use(config => {
  config._mock = true
  return config
})

// 响应拦截器（占位，mock 直接在接口函数中处理）
request.interceptors.response.use(
  response => response,
  error => Promise.reject(error)
)

// Mock 响应封装
function mockRequest(data, delay = 300) {
  return new Promise(resolve =>
    setTimeout(() => resolve({ code: 200, message: 'success', data }), delay)
  )
}

function mockError(message, delay = 300) {
  return new Promise((_, reject) =>
    setTimeout(() => reject({ code: 400, message, data: null }), delay)
  )
}

function httpOk(data) {
  return Promise.resolve({ code: 200, message: 'success', data })
}

function httpNotImplemented() {
  return Promise.reject(new Error('后端接口未接入'))
}

// ==================== 证券账户接口 ====================

export function getSecuritiesAccounts(params) {
  let list = [...securitiesAccountList]
  if (params?.securitiesAccountNo) {
    list = list.filter(item => item.securitiesAccountNo === params.securitiesAccountNo)
  }
  if (params?.accountStatus) {
    list = list.filter(item => item.accountStatus === params.accountStatus)
  }
  if (params?.investorId) {
    list = list.filter(item => item.investorId === params.investorId)
  }
  return mockRequest(list)
}

export function getSecuritiesAccountByNo(accountNo) {
  const item = securitiesAccountList.find(a => a.securitiesAccountNo === accountNo)
  return item ? mockRequest(item) : mockRequest(null)
}

export function openSecuritiesAccount(data) {
  const newAccountNo = 'SEC' + String(Date.now()).slice(-8)
  const newAccount = {
    securitiesAccountNo: newAccountNo,
    investorId: data.investorId || 10004,
    investorName: data.investorName,
    idType: data.idType,
    idNo: data.idNo,
    phone: data.phone,
    openTime: new Date().toISOString(),
    accountStatus: AccountStatus.NORMAL
  }
  securitiesAccountList.push(newAccount)
  return mockRequest({ accountNo: newAccountNo, account: newAccount })
}

// ==================== 资金账户接口 ====================

export function getFundAccounts(params) {
  let list = [...fundAccountList]
  if (params?.accountStatus) {
    list = list.filter(item => item.accountStatus === params.accountStatus)
  }
  return mockRequest(list)
}

export function getFundAccountByNo(accountNo) {
  if (dataSource === 'http') {
    return getFundAccountByNoHttp(accountNo).then(httpOk)
  }
  const item = fundAccountList.find(a => a.fundAccountNo === accountNo)
  return item ? mockRequest(item) : mockRequest(null)
}

export function openFundAccount(data) {
  if (dataSource === 'http') return httpNotImplemented()
  const newAccountNo = 'FND' + String(Date.now()).slice(-8)
  const newAccount = {
    fundAccountNo: newAccountNo,
    investorId: data.investorId,
    bankCardNo: data.bankCardNo,
    availableBalance: 0.00,
    frozenAmount: 0.00,
    accountStatus: AccountStatus.NORMAL,
    tradePwdDigest: 'hash_' + Date.now(),
    withdrawPwdDigest: 'hash_' + Date.now()
  }
  fundAccountList.push(newAccount)
  return mockRequest({ accountNo: newAccountNo, account: newAccount })
}

export function deposit(data) {
  if (dataSource === 'http') return httpNotImplemented()
  const account = fundAccountList.find(a => a.fundAccountNo === data.fundAccountNo)
  if (!account) return mockError('资金账户不存在')
  if (account.accountStatus !== AccountStatus.NORMAL) return mockError('账户状态异常，无法存款')

  account.availableBalance += data.amount

  const serialNo = 'SER' + String(Date.now()).slice(-8)
  const tx = {
    serialNo,
    transactionId: 'TXN' + String(Date.now()).slice(-8),
    fundAccountNo: data.fundAccountNo,
    amount: data.amount,
    transactionType: TransactionType.DEPOSIT,
    transactionStatus: TransactionStatus.SUCCESS,
    arrivedTime: new Date().toISOString(),
    operateTime: new Date().toISOString()
  }
  transactionList.push(tx)

  return mockRequest({ availableBalance: account.availableBalance, serialNo })
}

export function withdraw(data) {
  if (dataSource === 'http') return httpNotImplemented()
  const account = fundAccountList.find(a => a.fundAccountNo === data.fundAccountNo)
  if (!account) return mockError('资金账户不存在')
  if (account.accountStatus !== AccountStatus.NORMAL) return mockError('账户状态异常，无法取款')
  if (account.availableBalance < data.amount) return mockError('余额不足')

  if (data.password !== '123456') return mockError('取款密码错误')

  account.availableBalance -= data.amount

  const serialNo = 'SER' + String(Date.now()).slice(-8)
  const tx = {
    serialNo,
    transactionId: 'TXN' + String(Date.now()).slice(-8),
    fundAccountNo: data.fundAccountNo,
    amount: data.amount,
    transactionType: TransactionType.WITHDRAW,
    transactionStatus: TransactionStatus.SUCCESS,
    arrivedTime: new Date().toISOString(),
    operateTime: new Date().toISOString()
  }
  transactionList.push(tx)

  return mockRequest({ availableBalance: account.availableBalance, serialNo })
}

// ==================== 关联接口 ====================

export function getAssociations(params) {
  if (dataSource === 'http') {
    return queryAssociationsHttp(params).then(httpOk)
  }
  let list = [...associationList]
  if (params?.securitiesAccountNo) list = list.filter(a => a.securitiesAccountNo === params.securitiesAccountNo)
  if (params?.fundAccountNo) list = list.filter(a => a.fundAccountNo === params.fundAccountNo)
  return mockRequest(list)
}

export function createAssociation(data) {
  if (dataSource === 'http') {
    return bindAssociationHttp(data).then(httpOk)
  }
  const assoc = {
    associationId: 'ASSOC' + String(Date.now()).slice(-8),
    securitiesAccountNo: data.securitiesAccountNo,
    fundAccountNo: data.fundAccountNo,
    associationStatus: AssociationStatus.ACTIVE,
    associationTime: new Date().toISOString()
  }
  associationList.push(assoc)
  return mockRequest(assoc)
}

export function cancelSecuritiesAccount(accountNo) {
  if (dataSource === 'http') return httpNotImplemented()
  const account = securitiesAccountList.find(a => a.securitiesAccountNo === accountNo)
  if (!account) return mockError('证券账户不存在')
  if (account.accountStatus !== AccountStatus.NORMAL) return mockError('仅正常状态的账户可注销')
  account.accountStatus = AccountStatus.CLOSED
  return mockRequest({ securitiesAccountNo: accountNo, accountStatus: AccountStatus.CLOSED })
}

export function changeFundPassword(data) {
  if (dataSource === 'http') {
    return changeFundPasswordHttp(data).then(() => httpOk({ fundAccountNo: data.fundAccountNo, status: 'SUCCESS' }))
  }
  const account = fundAccountList.find(a => a.fundAccountNo === data.fundAccountNo)
  if (!account) return mockError('资金账户不存在')
  if (data.originalPassword !== '123456') return mockError('原密码错误')
  if (data.newPassword !== data.confirmPassword) return mockError('两次新密码不一致')
  return mockRequest({ fundAccountNo: data.fundAccountNo, status: 'SUCCESS' })
}

export function cancelFundAccount(accountNo) {
  if (dataSource === 'http') return httpNotImplemented()
  const account = fundAccountList.find(a => a.fundAccountNo === accountNo)
  if (!account) return mockError('资金账户不存在')
  if (account.accountStatus !== AccountStatus.NORMAL) return mockError('仅正常状态的账户可注销')
  if (account.availableBalance > 0 || account.frozenAmount > 0) return mockError('账户资金不为0，请先转出/解冻后再注销')
  account.accountStatus = AccountStatus.CLOSED
  return mockRequest({ fundAccountNo: accountNo, accountStatus: AccountStatus.CLOSED })
}

// ==================== 关联校验接口（C 部分新增）====================

export function checkAssociation(data) {
  if (dataSource === 'http') {
    return checkAssociationValidHttp(data).then(httpOk)
  }
  const assoc = associationList.find(
    a => a.securitiesAccountNo === data.securitiesAccountNo && a.fundAccountNo === data.fundAccountNo
  )
  const fundAccount = fundAccountList.find(a => a.fundAccountNo === data.fundAccountNo)

  return mockRequest({
    fund_account_id: data.fundAccountNo,
    security_account_id: data.securitiesAccountNo,
    investor_id: assoc?.investorId || fundAccount?.investorId || 'UNKNOWN',
    is_related: !!assoc,
    is_unique_valid: !!assoc,
    allow_operation: !!assoc && fundAccount?.accountStatus === AccountStatus.NORMAL,
    fund_account_status: fundAccount?.accountStatus || 'NOT_FOUND',
    security_account_status: 'NORMAL',
    reason: !assoc ? '资金账户与证券账户未建立绑定关系' : null
  })
}

// ==================== 状态校验接口（C 部分新增）====================

export function checkAccountStatus(data) {
  if (dataSource === 'http') {
    return checkStatusHttp(data).then(httpOk)
  }
  const accountType = data.accountType?.toUpperCase()
  let account
  if (accountType === 'FUND') {
    account = fundAccountList.find(a => a.fundAccountNo === data.accountId)
  } else {
    account = securitiesAccountList.find(a => a.securitiesAccountNo === data.accountId)
  }

  if (!account) {
    return mockRequest({
      account_type: accountType,
      account_id: data.accountId,
      status: 'NOT_FOUND',
      allowed: false,
      reason: '账户不存在'
    })
  }

  const allowed = account.accountStatus === AccountStatus.NORMAL
  return mockRequest({
    account_type: accountType,
    account_id: data.accountId,
    status: account.accountStatus,
    allowed,
    reason: allowed ? null : '账户状态异常，不允许当前操作'
  })
}

// ==================== 操作日志接口（C 部分新增）====================

const operationLogList = [
  {
    logId: 'LOG00000001',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'OPEN_ACCOUNT',
    targetType: 'APPLICATION',
    targetId: 'APP000001',
    operationDetail: '为客户张三开设证券账户 SEC00000001 和资金账户 FND00000001',
    operationResult: 'SUCCESS',
    operateTime: '2026-05-23T10:00:00'
  },
  {
    logId: 'LOG00000002',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'DEPOSIT',
    targetType: 'FUND',
    targetId: 'FND00000001',
    operationDetail: '存入金额 ¥50,000.00',
    operationResult: 'SUCCESS',
    operateTime: '2026-05-23T11:30:00'
  },
  {
    logId: 'LOG00000003',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'WITHDRAW',
    targetType: 'FUND',
    targetId: 'FND00000001',
    operationDetail: '取款金额 ¥20,000.00',
    operationResult: 'SUCCESS',
    operateTime: '2026-02-15T10:35:00'
  },
  {
    logId: 'LOG00000004',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'CHANGE_PWD',
    targetType: 'FUND',
    targetId: 'FND00000001',
    operationDetail: '修改交易密码',
    operationResult: 'SUCCESS',
    operateTime: '2026-03-10T14:20:00'
  },
  {
    logId: 'LOG00000005',
    operatorId: 'APR000001',
    operatorName: '审批人员',
    operationType: 'APPROVE',
    targetType: 'APPLICATION',
    targetId: 'APP000001',
    operationDetail: '审批通过开户申请 APP000001',
    operationResult: 'SUCCESS',
    operateTime: '2026-05-23T10:05:00'
  },
  {
    logId: 'LOG00000006',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'LINK',
    targetType: 'ASSOCIATION',
    targetId: 'ASC00000001',
    operationDetail: '关联证券账户 SEC00000001 与资金账户 FND00000001',
    operationResult: 'SUCCESS',
    operateTime: '2026-05-23T10:02:00'
  },
  {
    logId: 'LOG00000007',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'LOST',
    targetType: 'FUND',
    targetId: 'FND00000002',
    operationDetail: '资金账户挂失',
    operationResult: 'SUCCESS',
    operateTime: '2026-06-01T09:15:00'
  },
  {
    logId: 'LOG00000008',
    operatorId: 'staff_001',
    operatorName: '业务受理员',
    operationType: 'CANCEL',
    targetType: 'FUND',
    targetId: 'FND00000001',
    operationDetail: '资金账户注销申请',
    operationResult: 'FAILED',
    failReason: '账户资金不为0，无法注销',
    operateTime: '2026-05-28T16:00:00'
  }
]

export function getOperationLogs(params) {
  if (dataSource === 'http') {
    return fetchOperationLogsHttp(params).then(httpOk)
  }
  let list = [...operationLogList]
  if (params?.targetId) {
    list = list.filter(item => item.targetId === params.targetId)
  }
  if (params?.operationType) {
    list = list.filter(item => item.operationType === params.operationType)
  }
  if (params?.operatorId) {
    list = list.filter(item => item.operatorId === params.operatorId)
  }
  const page = params?.page || 1
  const pageSize = params?.pageSize || 20
  const total = list.length
  const start = (page - 1) * pageSize
  const items = list.slice(start, start + pageSize)
  return mockRequest({ items, page, pageSize, total })
}

export function createOperationLog(data) {
  if (dataSource === 'http') {
    return writeOperationLogHttp(data).then(httpOk)
  }
  const log = {
    logId: 'LOG' + String(Date.now()).slice(-8),
    operatorId: data.operatorId,
    operatorName: data.operatorName,
    operationType: data.operationType,
    targetType: data.targetType,
    targetId: data.targetId,
    operationDetail: data.operationDetail || null,
    operationResult: data.operationResult || 'SUCCESS',
    failReason: data.failReason || null,
    operateTime: new Date().toISOString()
  }
  operationLogList.unshift(log)
  return mockRequest(log)
}

// 导出默认实例
export default request
