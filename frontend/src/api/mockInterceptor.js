/**
 * Mock 拦截器 - 在开发环境拦截 API 请求并返回 Mock 数据
 */
import { fundAccountList } from '@/mock/fund'
import { associationList } from '@/mock/association'
import { securitiesAccountList } from '@/mock/securities'
import { AssociationStatus } from '@/constants/enums'

export function mockInterceptor(config) {
  const { method, url } = config

  // Mock 登录
  if (method === 'post' && url.includes('/auth/login')) {
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: { token: 'mock_token_123', userId: 10001 }
      }
    })
    return config
  }

  // Mock 获取基金账户
  if (method === 'get' && url.match(/\/fund-accounts\/[^/]+$/)) {
    const fundAccountNo = url.split('/').pop()
    const account = fundAccountList.find(a => a.fundAccountNo === decodeURIComponent(fundAccountNo))
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: account ? {
          fund_account_id: account.fundAccountNo,
          investor_id: String(account.investorId),
          bank_card_no: account.bankCardNo,
          available_amount: String(account.availableBalance),
          frozen_amount: String(account.frozenAmount),
          total_amount: String(account.availableBalance + account.frozenAmount),
          account_status: account.accountStatus,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        } : null
      }
    })
    return config
  }

  // Mock 关联校验接口
  if (method === 'get' && url.includes('/associations/check')) {
    const urlObj = new URL(config.baseURL + url)
    const fundId = urlObj.searchParams.get('fund_account_id')
    const secId = urlObj.searchParams.get('security_account_id')
    const assoc = associationList.find(
      a => a.securitiesAccountNo === secId && a.fundAccountNo === fundId
    )
    const fundAccount = fundAccountList.find(a => a.fundAccountNo === fundId)
    const secAccount = securitiesAccountList.find(a => a.securitiesAccountNo === secId)

    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: {
          fund_account_id: fundId || '',
          security_account_id: secId || '',
          investor_id: assoc?.investorId || fundAccount?.investorId || 'UNKNOWN',
          is_related: !!assoc,
          is_unique_valid: !!assoc,
          allow_operation: !!assoc && fundAccount?.accountStatus === 'NORMAL',
          fund_account_status: fundAccount?.accountStatus || 'NOT_FOUND',
          security_account_status: secAccount?.accountStatus || 'NORMAL',
          reason: !assoc ? '资金账户与证券账户未建立绑定关系' : null
        }
      }
    })
    return config
  }

  // Mock 查询关联账户
  if (method === 'get' && url.includes('/associations')) {
    const urlObj = new URL(config.baseURL + url)
    const fundId = urlObj.searchParams.get('fund_account_id')
    const secId = urlObj.searchParams.get('security_account_id')
    const invId = urlObj.searchParams.get('investor_id')

    let result = [...associationList]
    if (fundId) result = result.filter(a => a.fundAccountNo === fundId)
    if (secId) result = result.filter(a => a.securitiesAccountNo === secId)
    if (invId) result = result.filter(a => a.investorId === Number(invId))

    const assoc = result[0]
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: assoc ? {
          association_id: assoc.associationId,
          investor_id: String(assoc.investorId),
          fund_account_id: assoc.fundAccountNo,
          security_account_id: assoc.securitiesAccountNo,
          association_status: assoc.associationStatus,
          associated_at: assoc.associationTime
        } : {
          association_id: null,
          investor_id: invId || 'UNKNOWN',
          fund_account_id: fundId || '',
          security_account_id: secId || '',
          association_status: AssociationStatus.UNLINKED,
          associated_at: null
        }
      }
    })
    return config
  }

  // Mock 创建关联
  if (method === 'post' && url.includes('/associations')) {
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: {
          association_id: 'ASC' + Date.now(),
          investor_id: '10001',
          fund_account_id: 'FND00000001',
          security_account_id: 'SEC00000001',
          association_status: 'ACTIVE',
          associated_at: new Date().toISOString()
        }
      }
    })
    return config
  }

  // Mock 解除关联
  if (method === 'delete' && url.includes('/associations')) {
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: {
          association_id: 'ASSOC00000001',
          association_status: 'UNLINKED',
          associated_at: null
        }
      }
    })
    return config
  }

  // Mock 状态校验
  if (method === 'post' && url.includes('/status/check')) {
    const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
    const accountType = body?.account_type?.toUpperCase()
    let account
    if (accountType === 'FUND') {
      account = fundAccountList.find(a => a.fundAccountNo === body?.account_id)
    } else {
      account = securitiesAccountList.find(a => a.securitiesAccountNo === body?.account_id)
    }

    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: {
          account_type: accountType,
          account_id: body?.account_id || '',
          status: account?.accountStatus || 'NOT_FOUND',
          allowed: account?.accountStatus === 'NORMAL',
          reason: account ? (account.accountStatus === 'NORMAL' ? null : '账户状态异常') : '账户不存在'
        }
      }
    })
    return config
  }

  // Mock 创建操作日志
  if (method === 'post' && url.includes('/operation-logs')) {
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: {
          log_id: 'LOG' + Date.now(),
          operator_id: 'staff_001',
          operator_name: '业务受理员',
          operation_type: 'QUERY',
          target_type: 'FUND',
          target_id: 'FND00000001',
          operation_detail: null,
          operation_result: 'SUCCESS',
          fail_reason: null,
          client_ip: null,
          request_id: null,
          created_at: new Date().toISOString()
        }
      }
    })
    return config
  }

  // Mock 查询操作日志
  if (method === 'get' && url.includes('/operation-logs')) {
    const mockLogs = [
      { log_id: 'LOG00000001', operator_id: 'staff_001', operator_name: '业务受理员', operation_type: 'OPEN_ACCOUNT', target_type: 'APPLICATION', target_id: 'APP000001', operation_detail: '开设证券账户', operation_result: 'SUCCESS', fail_reason: null, client_ip: null, request_id: null, created_at: '2026-05-23T10:00:00' },
      { log_id: 'LOG00000002', operator_id: 'staff_001', operator_name: '业务受理员', operation_type: 'DEPOSIT', target_type: 'FUND', target_id: 'FND00000001', operation_detail: '存款 ¥50,000.00', operation_result: 'SUCCESS', fail_reason: null, client_ip: null, request_id: null, created_at: '2026-05-23T11:30:00' },
      { log_id: 'LOG00000003', operator_id: 'APR000001', operator_name: '审批人员', operation_type: 'APPROVE', target_type: 'APPLICATION', target_id: 'APP000001', operation_detail: '审批通过', operation_result: 'SUCCESS', fail_reason: null, client_ip: null, request_id: null, created_at: '2026-05-23T10:05:00' },
      { log_id: 'LOG00000004', operator_id: 'staff_001', operator_name: '业务受理员', operation_type: 'LINK', target_type: 'ASSOCIATION', target_id: 'ASC00000001', operation_detail: '创建账户关联', operation_result: 'SUCCESS', fail_reason: null, client_ip: null, request_id: null, created_at: '2026-05-23T09:00:00' },
      { log_id: 'LOG00000005', operator_id: 'staff_001', operator_name: '业务受理员', operation_type: 'CANCEL', target_type: 'FUND', target_id: 'FND00000001', operation_detail: '注销申请', operation_result: 'FAILED', fail_reason: '账户资金不为0', client_ip: null, request_id: null, created_at: '2026-05-28T16:00:00' }
    ]
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: {
          items: mockLogs,
          page: 1,
          page_size: 20,
          total: mockLogs.length
        }
      }
    })
    return config
  }

  // 其他请求保持原样
  return config
}
