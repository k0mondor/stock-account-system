import {
  accountChangePassword,
  changeAccountStatus,
  getAssociationHistory,
  checkAccountStatus,
  checkAssociation,
  createOperationLog,
  getAssociations,
  getFundAccount,
  jointClose as jointCloseApi,
  getOperationLogs,
  resetFundPasswordByStaff as resetFundPasswordByStaffApi,
} from '@/api/accountApi'

function toAmountNumber(value) {
  if (value === null || value === undefined || value === '') return 0
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function asArray(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.items)) return data.items
  if (Array.isArray(data?.data)) return data.data
  return []
}

function mapFundAccountFromApi(data) {
  if (!data) return null
  return {
    fundAccountNo: data.fund_account_id,
    investorId: data.investor_id,
    bankCardNo: data.bank_card_no,
    availableBalance: toAmountNumber(data.available_amount),
    frozenAmount: toAmountNumber(data.frozen_amount),
    totalAmount: toAmountNumber(data.total_amount),
    accountStatus: data.account_status || data.status
  }
}

function mapAssociationFromApi(data) {
  if (!data) return null
  return {
    associationId: data.association_id,
    investorId: data.investor_id,
    fundAccountNo: data.fund_account_id,
    securitiesAccountNo: data.security_account_id,
    associationStatus: data.association_status,
    associationTime: data.associated_at,
    disassociationTime: data.disassociated_at
  }
}

export async function getFundAccountByNo(fundAccountNo) {
  const data = await getFundAccount(fundAccountNo)
  return mapFundAccountFromApi(data)
}

export async function queryAssociations(params) {
  const apiParams = {}
  if (params?.fundAccountNo) apiParams.fund_account_id = params.fundAccountNo
  if (params?.securitiesAccountNo) apiParams.security_account_id = params.securitiesAccountNo
  if (params?.investorId) apiParams.investor_id = params.investorId

  const data = await getAssociations(apiParams)
  const assoc = mapAssociationFromApi(data)
  if (!assoc || assoc.associationStatus !== 'ACTIVE') return []
  return [assoc]
}

export async function queryAssociationDetail(params) {
  const apiParams = {}
  if (params?.fundAccountNo) apiParams.fund_account_id = params.fundAccountNo
  if (params?.securitiesAccountNo) apiParams.security_account_id = params.securitiesAccountNo
  if (params?.investorId) apiParams.investor_id = params.investorId
  const data = await getAssociations(apiParams)
  return mapAssociationFromApi(data)
}

export async function queryAssociationHistory(params) {
  const apiParams = {}
  if (params?.fundAccountNo) apiParams.fund_account_id = params.fundAccountNo
  if (params?.securitiesAccountNo) apiParams.security_account_id = params.securitiesAccountNo
  if (params?.investorId) apiParams.investor_id = params.investorId
  const data = await getAssociationHistory(apiParams)
  return asArray(data).map(mapAssociationFromApi)
}

export async function checkAssociationValid(params) {
  const apiParams = {
    fund_account_id: params.fundAccountNo,
    security_account_id: params.securitiesAccountNo,
    operation_type: params.operationType
  }
  if (params.investorId) apiParams.investor_id = params.investorId
  return await checkAssociation(apiParams)
}

export async function changeFundPassword(params) {
  const pwdType = params?.pwdType === 'withdraw' ? 'WITHDRAW' : 'TRADE'
  await accountChangePassword({
    fund_account_id: params.fundAccountNo,
    password_type: pwdType,
    old_password: params.originalPassword,
    new_password: params.newPassword
  })
}

export async function resetFundPasswordByStaff(params) {
  const pwdType = params?.pwdType === 'withdraw' ? 'WITHDRAW' : 'TRADE'
  return await resetFundPasswordByStaffApi(params.fundAccountNo, {
    staff_id: params.staffId,
    customer_id_number: params.customerIdNumber,
    password_type: pwdType,
    new_password: params.newPassword,
    reason: params.reason
  })
}

export async function jointClose(params) {
  return await jointCloseApi({
    fund_account_id: params.fundAccountNo,
    security_account_id: params.securitiesAccountNo,
    customer_id_number: params.customerIdNumber,
    operator_id: params.operatorId,
    operator_name: params.operatorName,
    reason: params.reason || null
  })
}

export async function checkStatus(data) {
  return await checkAccountStatus({
    account_type: data.accountType,
    account_id: data.accountId,
    operation_type: data.operationType,
    checked_at: data.checkedAt || new Date().toISOString()
  })
}

export async function changeStatus(data) {
  return await changeAccountStatus({
    account_type: data.accountType,
    account_id: data.accountId,
    target_status: data.targetStatus,
    reason: data.reason || null,
    operator_id: data.operatorId,
    operator_name: data.operatorName
  })
}

export async function fetchOperationLogs(params) {
  const apiParams = {
    page: params?.page || 1,
    page_size: params?.pageSize || 20
  }
  if (params?.operatorId) apiParams.operator_id = params.operatorId
  if (params?.operationType) apiParams.operation_type = params.operationType
  if (params?.targetType) apiParams.target_type = params.targetType
  if (params?.targetId) apiParams.target_id = params.targetId
  if (params?.operationResult) apiParams.operation_result = params.operationResult
  if (params?.startTime) apiParams.start_time = params.startTime
  if (params?.endTime) apiParams.end_time = params.endTime

  const data = await getOperationLogs(apiParams)
  return {
    items: asArray(data?.items ? data : data?.data ? data.data : data).map(item => ({
      logId: item.log_id,
      operatorId: item.operator_id,
      operatorName: item.operator_name,
      operationType: item.operation_type,
      targetType: item.target_type,
      targetId: item.target_id,
      operationDetail: item.operation_detail,
      operationResult: item.operation_result,
      failReason: item.fail_reason,
      clientIp: item.client_ip,
      requestId: item.request_id,
      operateTime: item.created_at
    })),
    page: data.page,
    pageSize: data.page_size,
    total: data.total
  }
}

export async function writeOperationLog(data) {
  await createOperationLog({
    operator_id: data.operatorId,
    operator_name: data.operatorName,
    operation_type: data.operationType,
    target_type: data.targetType,
    target_id: data.targetId,
    operation_detail: data.operationDetail || null,
    operation_result: data.operationResult || 'SUCCESS',
    fail_reason: data.failReason || null,
    client_ip: data.clientIp || null,
    request_id: data.requestId || null
  })
}
