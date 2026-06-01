export function bi(zh, enUpper) {
  return `${zh}/${enUpper}`
}

export const PageTitleBi = {
  '开设证券账户': bi('开设证券账户', 'OPEN SECURITIES ACCOUNT'),
  '证券账户挂失补办': bi('证券账户挂失补办', 'SECURITIES LOSS & REISSUE'),
  '联合开户': bi('联合开户', 'JOINT OPENING'),
  '资金账户查询': bi('资金账户查询', 'FUND ACCOUNT QUERY'),
  '证券账户查询': bi('证券账户查询', 'SECURITIES ACCOUNT QUERY'),
  '存取款业务': bi('存取款业务', 'DEPOSIT & WITHDRAW'),
  '存款': bi('存款', 'DEPOSIT'),
  '取款': bi('取款', 'WITHDRAW'),
  '资金账户挂失补办': bi('资金账户挂失补办', 'FUND LOSS & REISSUE'),
  '注销证券账户': bi('注销证券账户', 'CLOSE SECURITIES ACCOUNT'),
  '注销资金账户': bi('注销资金账户', 'CLOSE FUND ACCOUNT'),
  '修改密码': bi('修改密码', 'CHANGE PASSWORD'),
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
  openAccount: bi('开设账户', 'OPEN'),
  lost: bi('挂失', 'LOSS'),
  cancel: bi('注销', 'CLOSE'),
  changePwd: bi('修改密码', 'CHANGE PWD'),
  jointOpen: bi('联合开户', 'JOINT OPENING'),
  depositWithdraw: bi('存取款业务', 'DEPOSIT & WITHDRAW'),
  approvalList: bi('审批列表', 'APPROVAL LIST'),
  operationLog: bi('操作日志', 'OPERATION LOG'),
  staffEntry: bi('工作人员入口', 'STAFF ENTRY'),
  approverEntry: bi('审批人员入口', 'APPROVER ENTRY')
}
