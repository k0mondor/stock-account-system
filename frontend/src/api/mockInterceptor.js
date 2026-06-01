/**
 * Mock 拦截器 - 在开发环境拦截 API 请求并返回 Mock 数据
 */
import { fundAccountList } from '@/mock/fund'
import { associationList } from '@/mock/association'

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
        data: account || {
          error: 'Fund account not found',
          success: false,
          code: '404'
        }
      }
    })
    return config
  }

  // Mock 查询关联账户
  if (method === 'get' && url.includes('/associations')) {
    config.adapter = () => Promise.resolve({
      data: {
        success: true,
        data: associationList
      }
    })
    return config
  }

  // 其他请求保持原样
  return config
}
