<!-- src/views/staff/FundQuery.vue -->
<template>
  <div>
    <PageHeader title="资金账户查询" />

    <el-card style="margin-top: 24px; max-width: 1100px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <el-form @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="资金账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="searchNo" placeholder="FND00000001" style="width: 100%;" />
          </el-form-item>
        </el-form>
        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleSearch">查询</button>
        </div>
      </div>

      <div v-if="accountInfo" style="margin-top: 32px; padding: 24px; border: 1px solid var(--color-gray-200); background: var(--color-white); text-align: left;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px 32px;">
          <div><strong>账户号：</strong>{{ accountInfo.fundAccountNo }}</div>
          <div><strong>投资者ID：</strong>{{ accountInfo.investorId }}</div>
          <div><strong>银行卡：</strong>{{ accountInfo.bankCardNo }}</div>
          <div><strong>余额：</strong><span style="font-size: 18px; font-weight: 600;">¥ {{ accountInfo.balance.toFixed(2) }}</span></div>
          <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
        </div>
      </div>

      <div v-if="accountInfo" style="margin-top: 32px;">
        <h4 style="margin: 0 0 16px; font-weight: 600;">关联证券账户</h4>
        <el-table :data="associations" stripe style="width: 100%;">
          <el-table-column prop="securitiesAccountNo" label="证券账户号" />
          <el-table-column prop="associationStatus" label="关联状态" />
          <el-table-column prop="associationTime" label="关联时间" />
        </el-table>
      </div>

      <div v-if="accountInfo" style="margin-top: 32px;">
        <h4 style="margin: 0 0 16px; font-weight: 600;">资金流水</h4>
        <el-table :data="transactions" stripe style="width: 100%;">
          <el-table-column prop="serialNo" label="流水号" width="140" />
          <el-table-column prop="transactionType" label="类型" width="100" />
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="transactionStatus" label="状态" width="100" />
          <el-table-column prop="operateTime" label="操作时间" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getFundAccountByNo, getAssociations } from '@/utils/request'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageHeader from '@/components/PageHeader.vue'

const searchNo = ref('')
const accountInfo = ref(null)
const associations = ref([])
const transactions = ref([])

const handleSearch = async () => {
  if (!searchNo.value) return
  try {
    const res = await getFundAccountByNo(searchNo.value)
    accountInfo.value = res.data

    const assocRes = await getAssociations({ fundAccountNo: searchNo.value })
    associations.value = assocRes.data || []

    transactions.value = []
  } catch (e) {
    ElMessage.error('查询失败')
  }
}
</script>

<style scoped>
.btn-primary {
  padding: 10px 28px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 0;
  cursor: pointer;
}
</style>