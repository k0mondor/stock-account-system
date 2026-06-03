// src/constants/enums.js

export const AccountStatus = {
  NORMAL: 'NORMAL',
  LOST: 'LOST',
  FROZEN: 'FROZEN',
  CLOSED: 'CLOSED'
}

export const AccountStatusLabel = {
  NORMAL: '正常',
  LOST: '挂失',
  FROZEN: '冻结',
  CLOSED: '销户'
}

export const AccountType = {
  SECURITIES: 'SECURITIES',
  FUND: 'FUND'
}

export const ApplyStatus = {
  PENDING_SUBMIT: 'PENDING_SUBMIT',
  PENDING_APPROVE: 'PENDING_APPROVE',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
  WITHDRAWN: 'WITHDRAWN'
}

export const ApplyStatusLabel = {
  PENDING_SUBMIT: '待提交',
  PENDING_APPROVE: '待审批',
  APPROVED: '已通过',
  REJECTED: '已驳回',
  WITHDRAWN: '已撤销'
}

export const ProcessStatus = {
  WAITING: 'WAITING',
  PROCESSING: 'PROCESSING',
  DONE: 'DONE',
  FAILED: 'FAILED'
}

export const ApprovalStatus = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED'
}

export const AssociationStatus = {
  ACTIVE: 'ACTIVE',
  UNLINKED: 'UNLINKED'
}

export const TransactionType = {
  DEPOSIT: 'DEPOSIT',
  WITHDRAW: 'WITHDRAW'
}

export const TransactionStatus = {
  PROCESSING: 'PROCESSING',
  SUCCESS: 'SUCCESS',
  FAILED: 'FAILED',
  REVERSED: 'REVERSED'
}

export const OperationType = {
  OPEN_ACCOUNT: 'OPEN_ACCOUNT',
  LOST: 'LOST',
  REISSUE: 'REISSUE',
  CANCEL: 'CANCEL',
  QUERY: 'QUERY',
  DEPOSIT: 'DEPOSIT',
  WITHDRAW: 'WITHDRAW',
  CHANGE_PWD: 'CHANGE_PWD',
  LINK: 'LINK',
  UNLINK: 'UNLINK',
  APPROVE: 'APPROVE',
  REJECT: 'REJECT',
  STATUS_CHANGE: 'STATUS_CHANGE',
  ID_VERIFY: 'ID_VERIFY'
}

export const OperationTypeLabel = {
  OPEN_ACCOUNT: '开户',
  LOST: '挂失',
  REISSUE: '补办',
  CANCEL: '注销',
  QUERY: '查询',
  DEPOSIT: '存款',
  WITHDRAW: '取款',
  CHANGE_PWD: '修改密码',
  LINK: '账户关联',
  UNLINK: '解除关联',
  APPROVE: '审批通过',
  REJECT: '审批拒绝',
  STATUS_CHANGE: '状态变更',
  ID_VERIFY: '身份核验'
}

export const TargetType = {
  FUND: 'FUND',
  SECURITIES: 'SECURITIES',
  ASSOCIATION: 'ASSOCIATION',
  APPLICATION: 'APPLICATION'
}

export const TargetTypeLabel = {
  FUND: '资金账户',
  SECURITIES: '证券账户',
  ASSOCIATION: '账户关联',
  APPLICATION: '开户申请'
}

export const IdType = {
  ID_CARD: 'ID_CARD',
  PASSPORT: 'PASSPORT',
  HK_MACAO_TAIWAN: 'HK_MACAO_TAIWAN'
}

export const IdTypeLabel = {
  ID_CARD: '居民身份证',
  PASSPORT: '护照',
  HK_MACAO_TAIWAN: '港澳台证件'
}
