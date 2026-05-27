// src/utils/request.js
import axios from 'axios'
import { securitiesAccountList } from '@/mock/securities'
import { fundAccountList, transactionList } from '@/mock/fund'
import { associationList } from '@/mock/association'
import { AccountStatus, AssociationStatus, TransactionStatus, TransactionType } from '@/constants/enums'
import { changeFundPassword as changeFundPasswordHttp, getFundAccountByNo as getFundAccountByNoHttp, queryAssociations as queryAssociationsHttp } from '@/services/accountService'

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
  // 过滤条件应全部满足（AND 逻辑）
  // 若提供证券账户号，则精确匹配该账户号
  if (params?.securitiesAccountNo) {
    list = list.filter(item => item.securitiesAccountNo === params.securitiesAccountNo)
  }
  // 若提供账户状态，则匹配状态
  if (params?.accountStatus) {
    list = list.filter(item => item.accountStatus === params.accountStatus)
  }
  // 若提供投资者 ID，则匹配投资者
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
  // 模拟生成新账户号
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

// 存款接口已扩展以接受 password 字段（可选），保持向后兼容
export function deposit(data) {
  if (dataSource === 'http') return httpNotImplemented()
  const account = fundAccountList.find(a => a.fundAccountNo === data.fundAccountNo)
  if (!account) return mockError('资金账户不存在')
  if (account.accountStatus !== AccountStatus.NORMAL) return mockError('账户状态异常，无法存款')

  // 若前端传递 password，则此处可进行安全校验（当前实现为直接忽略）
  // const password = data.password // 预留密码校验逻辑

  account.availableBalance += data.amount

  // 生成流水
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

  // 模拟密码校验（实际应比对 digest）
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
  if (dataSource === 'http') return httpNotImplemented()
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

// 导出默认实例
export default request
