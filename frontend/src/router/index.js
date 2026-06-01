// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/common/Login.vue')
  },
  // 工作人员路由
  {
    path: '/staff',
    component: () => import('@/views/staff/Layout.vue'),
    redirect: '/staff/securities/query',
    children: [
      { path: 'securities/query', component: () => import('@/views/staff/SecuritiesQuery.vue') },
      { path: 'securities/open', component: () => import('@/views/staff/SecuritiesOpen.vue') },
      { path: 'securities/lost-reissue', component: () => import('@/views/staff/SecuritiesLostReissue.vue') },
      { path: 'securities/cancel', component: () => import('@/views/staff/SecuritiesCancel.vue') },
      { path: 'fund/query', component: () => import('@/views/staff/FundQuery.vue') },
      { path: 'fund/transfer', component: () => import('@/views/staff/FundTransfer.vue') },
      { path: 'fund/lost-reissue', component: () => import('@/views/staff/FundLostReissue.vue') },
      { path: 'fund/cancel', component: () => import('@/views/staff/FundCancel.vue') },
      { path: 'fund/change-pwd', component: () => import('@/views/staff/FundChangePwd.vue') },
      { path: 'joint/open', component: () => import('@/views/staff/JointOpen.vue') }
    ]
  },
  // 审批人员路由
  {
    path: '/approver',
    component: () => import('@/views/approver/Layout.vue'),
    redirect: '/approver/approval',
    children: [
      { path: 'approval', component: () => import('@/views/approver/ApprovalList.vue') },
      { path: 'log', component: () => import('@/views/common/OperationLog.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router