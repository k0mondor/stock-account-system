<!-- src/views/staff/FundQuery.vue -->
<template>
  <div>
    <PageHeader title="资金账户查询" />

    <PagePanel>
      <PageFormBlock>
        <el-form class="page-form-stack" @submit.prevent>
          <el-form-item label="资金账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="searchNo" placeholder="FUND000001" style="width: 100%;" />
          </el-form-item>
        </el-form>
        <PageActionRow primary-text="查询" secondary-text="重置" @primary="handleSearch" @secondary="resetSearch" />
      </PageFormBlock>

      <PageInfoCard v-if="accountInfo">
        <PageDetailGrid>
          <div><strong>账户号：</strong>{{ accountInfo.fundAccountNo }}</div>
          <div><strong>投资者ID：</strong>{{ accountInfo.investorId }}</div>
          <div><strong>银行卡：</strong>{{ accountInfo.bankCardNo }}</div>
          <div><strong>可用资金：</strong><span style="font-size: 18px; font-weight: 600;">¥ {{ accountInfo.availableBalance.toFixed(2) }}</span></div>
          <div><strong>冻结资金：</strong><span style="font-size: 18px; font-weight: 600;">¥ {{ accountInfo.frozenAmount.toFixed(2) }}</span></div>
          <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
        </PageDetailGrid>
      </PageInfoCard>

      <div v-if="accountInfo" style="margin-top: 32px;">
        <h4 style="margin: 0 0 16px; font-weight: 600;">关联证券账户</h4>
        <el-table :data="associations" :empty-text="associationEmptyText" stripe style="width: 100%;">
          <el-table-column prop="securitiesAccountNo" label="证券账户号" />
          <el-table-column prop="associationStatus" label="关联状态" />
          <el-table-column prop="associationTime" label="关联时间" />
        </el-table>
      </div>

      <div v-if="accountInfo" style="margin-top: 32px;">
        <h4 style="margin: 0 0 16px; font-weight: 600;">资金流水</h4>
        <el-table :data="transactions" :empty-text="transactionEmptyText" stripe style="width: 100%;">
          <el-table-column prop="serialNo" label="流水号" width="140" />
          <el-table-column prop="transactionType" label="类型" width="100" />
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="transactionStatus" label="状态" width="100" />
          <el-table-column prop="operateTime" label="操作时间" />
        </el-table>
      </div>

      <div v-if="hasSearched && !accountInfo" class="page-empty-state">
        未查询到符合条件的资金账户
      </div>
    </PagePanel>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getFundAccountByNo, getAssociations, getFundTransactions } from '@/utils/request'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageActionRow from '@/components/PageActionRow.vue'
import PageDetailGrid from '@/components/PageDetailGrid.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PageHeader from '@/components/PageHeader.vue'
import PagePanel from '@/components/PagePanel.vue'

const searchNo = ref('')
const accountInfo = ref(null)
const associations = ref([])
const transactions = ref([])
const hasSearched = ref(false)

const associationEmptyText = computed(() => '该资金账户暂无关联证券账户')
const transactionEmptyText = computed(() => '该资金账户暂无资金流水')

const handleSearch = async () => {
  searchNo.value = searchNo.value.trim()
  if (!searchNo.value) {
    ElMessage.error('请输入资金账户号后再查询')
    return
  }
  try {
    const fundAccountNo = searchNo.value
    const res = await getFundAccountByNo(fundAccountNo)
    accountInfo.value = res.data
    hasSearched.value = true

    const assocRes = await getAssociations({ fundAccountNo })
    associations.value = assocRes.data || []

    const txRes = await getFundTransactions({ fundAccountNo, page: 1, pageSize: 20 })
    transactions.value = txRes.data?.items || []
  } catch (e) {
    hasSearched.value = true
    accountInfo.value = null
    associations.value = []
    transactions.value = []
    ElMessage.error(e.message || '查询失败')
  }
}

const resetSearch = () => {
  searchNo.value = ''
  accountInfo.value = null
  associations.value = []
  transactions.value = []
  hasSearched.value = false
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
