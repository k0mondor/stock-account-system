// src/mock/fund.js
import { AccountStatus, TransactionStatus, TransactionType } from '@/constants/enums'

export const fundAccountList = [
  {
    fundAccountNo: 'FND00000001',
    investorId: 10001,
    bankCardNo: '6222021234567890',
    availableBalance: 120000.00,
    frozenAmount: 30000.00,
    accountStatus: AccountStatus.NORMAL,
    tradePwdDigest: 'hash_trade_001',
    withdrawPwdDigest: 'hash_withdraw_001'
  },
  {
    fundAccountNo: 'FND00000002',
    investorId: 10002,
    bankCardNo: '6222029876543210',
    availableBalance: 0.00,
    frozenAmount: 0.00,
    accountStatus: AccountStatus.LOST,
    tradePwdDigest: 'hash_trade_002',
    withdrawPwdDigest: 'hash_withdraw_002'
  }
]

export const transactionList = [
  {
    serialNo: 'SER00000001',
    transactionId: 'TXN00000001',
    fundAccountNo: 'FND00000001',
    amount: 50000.00,
    transactionType: TransactionType.DEPOSIT,
    transactionStatus: TransactionStatus.SUCCESS,
    arrivedTime: '2026-01-10T09:05:00',
    operateTime: '2026-01-10T09:00:00'
  },
  {
    serialNo: 'SER00000002',
    transactionId: 'TXN00000002',
    fundAccountNo: 'FND00000001',
    amount: 20000.00,
    transactionType: TransactionType.WITHDRAW,
    transactionStatus: TransactionStatus.SUCCESS,
    arrivedTime: '2026-02-15T10:35:00',
    operateTime: '2026-02-15T10:30:00'
  }
]
