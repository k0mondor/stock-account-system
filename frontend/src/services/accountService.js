import { accountChangePassword, getAssociations, getFundAccount } from '@/api/accountApi'

function toAmountNumber(value) {
  if (value === null || value === undefined || value === '') return 0
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function mapFundAccountFromApi(data) {
  if (!data) return null
  return {
    fundAccountNo: data.fund_account_id,
    investorId: data.investor_id,
    bankCardNo: data.bank_card_no,
    availableBalance: toAmountNumber(data.available_amount),
    frozenAmount: toAmountNumber(data.frozen_amount),
    accountStatus: data.status
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
    associationTime: data.associated_at
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

export async function changeFundPassword(params) {
  const pwdType = params?.pwdType === 'withdraw' ? 'WITHDRAW' : 'TRADE'
  await accountChangePassword({
    fund_account_id: params.fundAccountNo,
    password_type: pwdType,
    old_password: params.originalPassword,
    new_password: params.newPassword
  })
}

