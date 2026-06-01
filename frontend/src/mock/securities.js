// src/mock/securities.js
import { AccountStatus } from '@/constants/enums'

export const securitiesAccountList = [
  {
    securitiesAccountNo: 'SEC00000001',
    investorId: 10001,
    investorName: '张三',
    idType: 'ID_CARD',
    idNo: '330102199001011234',
    phone: '13800138000',
    openTime: '2026-01-10T09:00:00',
    accountStatus: AccountStatus.NORMAL
  },
  {
    securitiesAccountNo: 'SEC00000002',
    investorId: 10002,
    investorName: '李四',
    idType: 'ID_CARD',
    idNo: '310101199503152345',
    phone: '13900139000',
    openTime: '2026-02-15T10:30:00',
    accountStatus: AccountStatus.LOST
  },
  {
    securitiesAccountNo: 'SEC00000003',
    investorId: 10003,
    investorName: '王五',
    idType: 'PASSPORT',
    idNo: 'E12345678',
    phone: '13700137000',
    openTime: '2026-03-20T14:00:00',
    accountStatus: AccountStatus.FROZEN
  }
]