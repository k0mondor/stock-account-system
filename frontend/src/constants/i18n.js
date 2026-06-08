export function bi(zh, enUpper) {
  return `${zh}/${enUpper}`
}

export const PageTitleBi = {
  '证券账户挂失补办': bi('证券账户挂失补办', 'SECURITIES LOSS & REISSUE'),
  '证券账户密码重置': bi('证券账户密码重置', 'SECURITIES PASSWORD RESET'),
  '联合开户': bi('联合开户', 'JOINT OPENING'),
  '联合销户': bi('联合销户', 'JOINT CLOSURE'),
  '资金账户查询': bi('资金账户查询', 'FUND ACCOUNT QUERY'),
  '证券账户查询': bi('证券账户查询', 'SECURITIES ACCOUNT QUERY'),
  '存取款业务': bi('存取款业务', 'DEPOSIT & WITHDRAW'),
  '存款': bi('存款', 'DEPOSIT'),
  '取款': bi('取款', 'WITHDRAW'),
  '资金账户挂失补办': bi('资金账户挂失补办', 'FUND LOSS & REISSUE'),
  '修改密码': bi('修改密码', 'CHANGE PASSWORD'),
  '资金账户密码重置': bi('资金账户密码重置', 'FUND PASSWORD RESET'),
  '关联查询/校验': bi('关联查询/校验', 'ASSOCIATION QUERY'),
  '冻结/解冻': bi('冻结/解冻', 'FREEZE & UNFREEZE'),
  '审批列表': bi('审批列表', 'APPROVAL LIST'),
  '业务办理历史': bi('业务办理历史', 'OPERATION HISTORY')
}

export const UiText = {
  staffArea: bi('工作人员界面', 'STAFF'),
  approverArea: bi('审批人员界面', 'APPROVER'),
  help: bi('帮助', 'HELP'),
  logout: bi('退出', 'LOGOUT'),
  quickNav: bi('业务快捷导航', 'QUICK NAV'),
  securities: bi('证券账户', 'SECURITIES'),
  fund: bi('资金账户', 'FUND'),
  queryAccount: bi('查询账户', 'QUERY'),
  lost: bi('挂失补办', 'LOSS & REISSUE'),
  changePwd: bi('修改密码', 'CHANGE PWD'),
  resetPwd: bi('资金密码重置', 'FUND PWD RESET'),
  associationWorkbench: bi('关联查询/校验', 'ASSOCIATION'),
  statusWorkbench: bi('冻结/解冻', 'STATUS'),
  jointOpen: bi('联合开户', 'JOINT OPENING'),
  jointClose: bi('联合销户', 'JOINT CLOSURE'),
  depositWithdraw: bi('存取款业务', 'DEPOSIT & WITHDRAW'),
  approvalList: bi('审批列表', 'APPROVAL LIST'),
  operationLog: bi('操作日志', 'OPERATION LOG'),
  staffEntry: bi('工作人员入口', 'STAFF ENTRY'),
  approverEntry: bi('审批人员入口', 'APPROVER ENTRY')
}
