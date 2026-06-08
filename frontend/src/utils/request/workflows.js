import { httpClient } from '@/api/httpClient'
import {
  changeStatus as changeStatusHttp,
  jointClose as jointCloseHttp,
  checkAssociationValid as checkAssociationValidHttp,
  queryAssociationDetail as queryAssociationDetailHttp,
  queryAssociationHistory as queryAssociationHistoryHttp,
  checkStatus as checkStatusHttp,
  fetchOperationLogs as fetchOperationLogsHttp,
  queryAssociations as queryAssociationsHttp,
  writeOperationLog as writeOperationLogHttp,
} from '@/services/accountService'
import {
  accountApiPrefix,
  ensureCustomerHttp,
  httpOk,
  normalizeArrayResponse,
  wrapHttp,
} from './core'

export function getAssociations(params) {
  return queryAssociationsHttp(params).then(httpOk)
}

export function getAssociationDetail(params) {
  return queryAssociationDetailHttp(params).then(httpOk)
}

export function getAssociationHistory(params) {
  return queryAssociationHistoryHttp(params).then(httpOk)
}

export function submitOpenApplication(data) {
  return wrapHttp(async () => {
    const applicantName = data.investorName || data.clientName || data.corporateName
    const idNumber = data.idNo || data.idCardNo || data.businessLicenseNo
    const phone = data.phone || data.legalPhone
    const customer = await ensureCustomerHttp({
      applicantName,
      idNumber,
      phone,
      idType: data.idType,
      gender: data.gender,
      address: data.address,
      occupation: data.occupation,
      educationLevel: data.educationLevel,
      employer: data.employer,
      agentIdNumber: data.agentIdNumber
    })
    const application = await httpClient.post(`${accountApiPrefix}/applications`, {
      customer_id: customer.customer_id,
      applicant_name: customer.customer_name,
      id_number: customer.id_number,
      phone: customer.phone,
      remark: data.remark || '前端提交开户申请'
    })
    return {
      applicationId: application.application_id,
      customerId: application.customer_id,
      applicantName: application.applicant_name,
      processStatus: application.proc_status,
      submittedAt: application.submitted_at
    }
  })
}

export function getApplications(params = {}) {
  return wrapHttp(async () => {
    const list = await httpClient.get(`${accountApiPrefix}/applications`, {
      params: {
        app_status: params.appStatus,
        proc_status: params.procStatus
      }
    })
    return normalizeArrayResponse(list).map(item => ({
      applyId: item.application_id,
      investorId: item.customer_id,
      applicantName: item.applicant_name,
      idNo: item.id_number,
      phone: item.phone,
      applyStatus: item.proc_status,
      appStatus: item.app_status,
      applyTime: item.submitted_at || item.created_at,
      fundAccountNo: item.fund_account_id,
      securitiesAccountNo: item.security_account_id,
      remark: item.remark
    }))
  })
}

export function approveApplication(data) {
  return wrapHttp(async () => {
    const result = await httpClient.post(`${accountApiPrefix}/applications/${data.applicationId}/approve`, {
      approval_opinion: data.comment || null,
      bank_card_no: data.bankCardNo,
      trade_password: data.tradePassword,
      withdraw_password: data.withdrawPassword
    })
    return {
      applicationId: result.application_id,
      processStatus: result.proc_status,
      fundAccountNo: result.fund_account_id,
      securitiesAccountNo: result.security_account_id
    }
  })
}

export function rejectApplication(data) {
  return wrapHttp(async () => {
    const result = await httpClient.post(`${accountApiPrefix}/applications/${data.applicationId}/reject`, {
      approval_opinion: data.comment || '审批驳回'
    })
    return {
      applicationId: result.application_id,
      processStatus: result.proc_status
    }
  })
}

export function checkAssociation(data) {
  return checkAssociationValidHttp(data).then(httpOk)
}

export function checkAccountStatus(data) {
  return checkStatusHttp(data).then(httpOk)
}

export function changeAccountStatus(data) {
  return changeStatusHttp(data).then(httpOk)
}

export function getOperationLogs(params) {
  return fetchOperationLogsHttp(params).then(httpOk)
}

export function createOperationLog(data) {
  return writeOperationLogHttp(data).then(httpOk)
}

export function jointClose(data) {
  return jointCloseHttp({
    ...data,
    operatorName: data?.operatorName || '业务受理员'
  }).then(httpOk)
}
