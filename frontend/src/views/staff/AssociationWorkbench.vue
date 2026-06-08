<template>
  <div>
    <PageHeader title="关联查询/校验" />

    <PagePanel>
      <PageInfoCard title="办理说明" style="margin-bottom: 24px;">
        <p class="inline-tip">账户绑定关系仅允许在联合开户与联合销户流程中维护，本页仅支持关联查询、关联校验与历史追踪。</p>
        <div class="inline-rule-list">
          <p><strong>查询关联：</strong>查看当前是否存在有效绑定，同时带出这对账户的关联历史。</p>
          <p><strong>执行校验：</strong>按所选业务类型校验当前账户对是否允许办理，并返回拒绝原因。</p>
        </div>
      </PageInfoCard>

      <PageFormBlock>
        <el-form class="page-form-stack" @submit.prevent>
          <el-form-item label="投资者编号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.investorId" placeholder="CUST000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="资金账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FUND000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证券账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="业务类型" label-position="top" style="margin-bottom: 0;">
            <el-select v-model="form.operationType" style="width: 100%;">
              <el-option v-for="item in operationOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="action-toolbar">
          <button class="btn-primary" :disabled="loading" @click="handleQuery">查询关联</button>
          <button class="btn-primary" :disabled="loading" @click="handleCheck">执行校验</button>
          <button class="btn-secondary" :disabled="loading" @click="resetAll">重置</button>
        </div>
      </PageFormBlock>

      <PageInfoCard v-if="associationDetail" title="当前关联" style="margin-top: 24px;">
        <PageDetailGrid>
          <div><strong>关联编号：</strong>{{ associationDetail.associationId || '--' }}</div>
          <div><strong>投资者编号：</strong>{{ associationDetail.investorId || '--' }}</div>
          <div><strong>资金账户号：</strong>{{ associationDetail.fundAccountNo || '--' }}</div>
          <div><strong>证券账户号：</strong>{{ associationDetail.securitiesAccountNo || '--' }}</div>
          <div><strong>关联状态：</strong>{{ associationStatusLabel[associationDetail.associationStatus] || associationDetail.associationStatus || '--' }}</div>
          <div><strong>建立时间：</strong>{{ associationDetail.associationTime || '--' }}</div>
        </PageDetailGrid>
      </PageInfoCard>

      <PageInfoCard v-if="checkResult" title="校验结果" style="margin-top: 24px;">
        <PageDetailGrid>
          <div><strong>资金账户号：</strong>{{ checkResult.fundAccountId }}</div>
          <div><strong>证券账户号：</strong>{{ checkResult.securitiesAccountId }}</div>
          <div><strong>投资者编号：</strong>{{ checkResult.investorId }}</div>
          <div><strong>当前关联：</strong>{{ checkResult.isRelated ? '已关联' : '未关联' }}</div>
          <div><strong>唯一有效：</strong>{{ checkResult.isUniqueValid ? '满足' : '不满足' }}</div>
          <div><strong>业务放行：</strong>{{ checkResult.allowOperation ? '允许' : '拒绝' }}</div>
          <div><strong>资金账户状态：</strong><AccountStatusTag :status="checkResult.fundAccountStatus" /></div>
          <div><strong>证券账户状态：</strong><AccountStatusTag :status="checkResult.securityAccountStatus" /></div>
        </PageDetailGrid>
        <p v-if="checkResult.reason" class="result-reason">拒绝原因：{{ checkResult.reason }}</p>
      </PageInfoCard>

      <PageInfoCard v-if="historyList.length" title="关联历史" style="margin-top: 24px;">
        <el-table :data="historyList" stripe style="width: 100%;">
          <el-table-column prop="associationId" label="关联编号" min-width="150" />
          <el-table-column prop="fundAccountNo" label="资金账户号" min-width="140" />
          <el-table-column prop="securitiesAccountNo" label="证券账户号" min-width="140" />
          <el-table-column prop="associationStatus" label="状态" min-width="120">
            <template #default="{ row }">
              {{ associationStatusLabel[row.associationStatus] || row.associationStatus }}
            </template>
          </el-table-column>
          <el-table-column prop="associationTime" label="建立时间" min-width="180" />
        </el-table>
      </PageInfoCard>
    </PagePanel>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { checkAssociation, getAssociationDetail, getAssociationHistory } from '@/utils/request'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageDetailGrid from '@/components/PageDetailGrid.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'

const operationOptions = [
  { label: '查询', value: 'QUERY' },
  { label: '存款', value: 'DEPOSIT' },
  { label: '取款', value: 'WITHDRAW' },
  { label: '资金账户密码重置', value: 'CHANGE_PWD' },
  { label: '挂失', value: 'LOST' },
  { label: '补办', value: 'REISSUE' },
  { label: '联合销户', value: 'CANCEL' }
]

const associationStatusLabel = {
  ACTIVE: '有效绑定',
  UNLINKED: '已解绑'
}

const buildInitialForm = () => ({
  investorId: '',
  fundAccountNo: '',
  securitiesAccountNo: '',
  operationType: 'QUERY'
})

const form = reactive(buildInitialForm())
const loading = ref(false)
const checkResult = ref(null)
const associationDetail = ref(null)
const historyList = ref([])

const normalizeForm = () => {
  form.investorId = String(form.investorId || '').trim()
  form.fundAccountNo = String(form.fundAccountNo || '').trim()
  form.securitiesAccountNo = String(form.securitiesAccountNo || '').trim()
}

const buildPayload = () => ({
  investorId: form.investorId || undefined,
  fundAccountNo: form.fundAccountNo || undefined,
  securitiesAccountNo: form.securitiesAccountNo || undefined,
  operationType: form.operationType
})

const ensureQueryCondition = () => {
  normalizeForm()
  if (!form.investorId && !form.fundAccountNo && !form.securitiesAccountNo) {
    ElMessage.error('请至少填写一个查询条件')
    return false
  }
  return true
}

const ensureAccountPair = () => {
  if (!ensureQueryCondition()) return false
  if (!form.fundAccountNo || !form.securitiesAccountNo) {
    ElMessage.error('关联校验必须同时输入资金账户号和证券账户号')
    return false
  }
  return true
}

const handleCheck = async () => {
  if (!ensureAccountPair()) return
  loading.value = true
  try {
    const res = await checkAssociation(buildPayload())
    checkResult.value = {
      fundAccountId: res.data.fund_account_id,
      securitiesAccountId: res.data.security_account_id,
      investorId: res.data.investor_id,
      isRelated: res.data.is_related,
      isUniqueValid: res.data.is_unique_valid,
      allowOperation: res.data.allow_operation,
      fundAccountStatus: res.data.fund_account_status,
      securityAccountStatus: res.data.security_account_status,
      reason: res.data.reason
    }
    ElMessage.success('关联校验完成')
  } catch (error) {
    checkResult.value = null
    ElMessage.error(error.message || '关联校验失败')
  } finally {
    loading.value = false
  }
}

const handleQuery = async () => {
  if (!ensureQueryCondition()) return
  loading.value = true
  try {
    const [detailRes, historyRes] = await Promise.all([
      getAssociationDetail(buildPayload()),
      getAssociationHistory(buildPayload())
    ])
    associationDetail.value = detailRes.data
    historyList.value = historyRes.data || []
    ElMessage.success(detailRes.data?.associationId ? '关联查询成功' : '未找到当前有效关联')
  } catch (error) {
    associationDetail.value = null
    historyList.value = []
    ElMessage.error(error.message || '关联查询失败')
  } finally {
    loading.value = false
  }
}

const resetAll = () => {
  Object.assign(form, buildInitialForm())
  checkResult.value = null
  associationDetail.value = null
  historyList.value = []
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.inline-tip {
  margin: 0;
  line-height: 1.7;
  color: var(--color-text-muted);
}

.inline-rule-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.inline-rule-list p {
  margin: 0;
  line-height: 1.7;
  color: var(--color-text-muted);
}

.result-reason {
  margin: 16px 0 0;
  font-size: 13px;
  color: var(--color-text-muted);
}

.action-toolbar {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}
</style>
