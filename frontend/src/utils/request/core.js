import { AccountStatus, AccountStatusLabel, TransactionStatus } from '@/constants/enums'
import { httpClient } from '@/api/httpClient'

export const accountApiPrefix = import.meta.env.VITE_ACCOUNT_PREFIX || '/api/v1/account'
export const DEFAULT_OPERATOR_ID = 'STAFF000001'
export const DEFAULT_OPERATOR_NAME = '业务受理员'
export const STAFF_SESSION_KEY = 'current_staff_session'

const DEMO_STAFF_SESSIONS = {
  STAFF: {
    staff_id: 'STAFF000001',
    staff_name: '业务受理员',
    role: 'STAFF',
    staff_status: 'ACTIVE'
  },
  APPROVER: {
    staff_id: 'APR000001',
    staff_name: '审批人员',
    role: 'APPROVER',
    staff_status: 'ACTIVE'
  },
  ADMIN: {
    staff_id: 'ADMIN000001',
    staff_name: '系统管理员',
    role: 'ADMIN',
    staff_status: 'ACTIVE'
  }
}

const customerCache = new Map()

export function readCurrentStaffSession() {
  try {
    const raw = localStorage.getItem(STAFF_SESSION_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed?.staff_id || !parsed?.role) return null
    return parsed
  } catch {
    return null
  }
}

export function writeCurrentStaffSession(staff) {
  if (!staff?.staff_id || !staff?.role) return
  localStorage.setItem(STAFF_SESSION_KEY, JSON.stringify(staff))
}

export function clearCurrentStaffSession() {
  localStorage.removeItem(STAFF_SESSION_KEY)
}

export async function ensureCurrentStaffSession(roles = []) {
  const normalizedRoles = roles.map(role => String(role).toUpperCase())
  const current = readCurrentStaffSession()
  if (
    current
    && (!normalizedRoles.length || normalizedRoles.includes(String(current.role).toUpperCase()))
  ) {
    return current
  }

  const fallbackRole = normalizedRoles.find(role => DEMO_STAFF_SESSIONS[role])
  if (fallbackRole) {
    const fallback = DEMO_STAFF_SESSIONS[fallbackRole]
    writeCurrentStaffSession(fallback)
    return fallback
  }

  const staffList = await httpClient.get(`${accountApiPrefix}/staff`)
  const matched = (Array.isArray(staffList) ? staffList : [])
    .find(item => {
      const role = String(item?.role || '').toUpperCase()
      const status = String(item?.staff_status || '').toUpperCase()
      return status === 'ACTIVE' && normalizedRoles.includes(role)
    })

  if (!matched) {
    throw new Error(`未找到可用的${normalizedRoles.join('/')}工作人员`)
  }

  writeCurrentStaffSession(matched)
  return matched
}

export function httpOk(data) {
  return Promise.resolve({ code: 200, message: 'success', data })
}

export function normalizeHttpError(error) {
  const payload = error?.response?.data
  const message = payload?.message ?? payload?.detail ?? error?.message ?? '请求失败'
  const detail = message
  if (Array.isArray(detail)) {
    return new Error(detail.map(item => item?.msg || JSON.stringify(item)).join('；'))
  }
  if (detail && typeof detail === 'object') {
    return new Error(detail.message || JSON.stringify(detail))
  }
  const normalized = new Error(String(detail))
  normalized.code = error?.code ?? payload?.code
  normalized.requestId = error?.requestId ?? payload?.request_id
  normalized.status = error?.status ?? error?.response?.status
  return normalized
}

export async function wrapHttp(loader) {
  try {
    const data = await loader()
    return httpOk(data)
  } catch (error) {
    throw normalizeHttpError(error)
  }
}

export function toNumber(value) {
  if (typeof value === 'number') return value
  const num = Number(value)
  return Number.isNaN(num) ? 0 : num
}

export function normalizeArrayResponse(result) {
  if (Array.isArray(result)) return result
  if (Array.isArray(result?.items)) return result.items
  if (Array.isArray(result?.data)) return result.data
  return []
}

export function normalizeAccountStatusValue(value) {
  if (!value) return ''
  const raw = String(value).trim()
  if (!raw) return ''
  if (Object.values(AccountStatus).includes(raw)) return raw
  const matched = Object.entries(AccountStatusLabel).find(([, label]) => label === raw)
  if (matched) return matched[0]
  return raw.toUpperCase()
}

export function generateId(prefix) {
  return `${prefix}${Date.now().toString(36).toUpperCase()}${Math.random().toString(36).slice(2, 6).toUpperCase()}`
}

export function buildOperator(data = {}) {
  return {
    operator_id: data.operatorId || DEFAULT_OPERATOR_ID,
    operator_name: data.operatorName || DEFAULT_OPERATOR_NAME,
  }
}

function trimOptional(value) {
  if (value == null) return null
  const normalized = String(value).trim()
  return normalized || null
}

function buildCustomerPayload(data = {}) {
  return {
    customer_name: trimOptional(data.applicantName),
    id_type: trimOptional(data.idType) || 'ID_CARD',
    id_number: trimOptional(data.idNumber),
    phone: trimOptional(data.phone),
    gender: trimOptional(data.gender),
    address: trimOptional(data.address),
    occupation: trimOptional(data.occupation),
    education_level: trimOptional(data.educationLevel),
    employer: trimOptional(data.employer),
    agent_id_number: trimOptional(data.agentIdNumber),
    customer_status: 'ACTIVE'
  }
}

async function listCustomersHttp() {
  const result = await httpClient.get(`${accountApiPrefix}/customers`)
  return normalizeArrayResponse(result)
}

export async function fetchCustomerHttp(customerId) {
  if (!customerId) return null
  if (customerCache.has(customerId)) return customerCache.get(customerId)
  const customer = await httpClient.get(`${accountApiPrefix}/customers/${customerId}`)
  customerCache.set(customerId, customer)
  return customer
}

export async function ensureCustomerHttp(data) {
  const payload = buildCustomerPayload(data)
  if (
    !payload.customer_name
    || !payload.id_number
    || !payload.phone
    || !payload.gender
    || !payload.address
    || !payload.occupation
    || !payload.education_level
    || !payload.employer
  ) {
    throw new Error('开户申请缺少必要的客户信息')
  }
  const customers = await listCustomersHttp()
  const existing = customers.find(item => item.id_number === payload.id_number)
  if (existing) {
    const patch = {}
    const fieldsToSync = [
      'customer_name',
      'phone',
      'id_type',
      'gender',
      'address',
      'occupation',
      'education_level',
      'employer',
      'agent_id_number'
    ]
    for (const field of fieldsToSync) {
      const nextValue = payload[field]
      const currentValue = existing[field] ?? null
      if (nextValue !== currentValue) {
        patch[field] = nextValue
      }
    }

    const syncedCustomer = Object.keys(patch).length
      ? await httpClient.put(`${accountApiPrefix}/customers/${existing.customer_id}`, patch)
      : existing
    customerCache.set(existing.customer_id, syncedCustomer)
    return syncedCustomer
  }

  const customer = await httpClient.post(`${accountApiPrefix}/customers`, {
    customer_id: generateId('CUST'),
    ...payload
  })
  customerCache.set(customer.customer_id, customer)
  return customer
}

export function mapSecuritiesAccountHttp(account, customer) {
  return {
    securitiesAccountNo: account.security_account_id,
    investorId: account.investor_id,
    investorName: customer?.customer_name || account.investor_id,
    idType: customer?.id_type || 'ID_CARD',
    idNo: customer?.id_number || '',
    phone: customer?.phone || '',
    accountStatus: account.account_status,
    openTime: account.created_at
  }
}

export function mapFundAccountHttp(account, customer) {
  return {
    ...account,
    investorName: customer?.customer_name || account.investorId,
    idNo: customer?.id_number || ''
  }
}

export function mapFundTransactionHttp(item) {
  return {
    serialNo: item.transaction_id,
    transactionId: item.transaction_id,
    fundAccountNo: item.fund_account_id,
    amount: toNumber(item.amount),
    transactionType: item.transaction_type,
    transactionStatus: TransactionStatus.SUCCESS,
    operateTime: item.occurred_at,
    arrivedTime: item.occurred_at
  }
}

export async function fetchSecuritiesAccountHttp(accountNo) {
  const account = await httpClient.get(`${accountApiPrefix}/security-accounts/${accountNo}`)
  const customer = await fetchCustomerHttp(account.investor_id)
  return mapSecuritiesAccountHttp(account, customer)
}
