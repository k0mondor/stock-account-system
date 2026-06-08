<template>
  <div>
    <PageHeader title="联合销户" />

    <PagePanel>
      <PageInfoCard title="办理说明" style="margin-bottom: 24px;">
        <p class="inline-tip">联合销户会在同一流程内同时关闭资金账户、证券账户并结束当前唯一有效绑定。只要任一前置条件不满足，页面会直接展示拒绝原因。</p>
      </PageInfoCard>

      <PageFormBlock>
        <el-form class="page-form-stack" @submit.prevent>
          <el-form-item label="资金账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FUND000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证券账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="客户证件号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.customerIdNumber" placeholder="110101200001010001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="工作人员号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.operatorId" placeholder="STAFF000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="销户原因" label-position="top" style="margin-bottom: 0;">
            <el-input
              v-model="form.reason"
              type="textarea"
              :rows="3"
              maxlength="256"
              show-word-limit
              placeholder="请输入联合销户原因"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>

        <PageActionRow
          primary-text="查询校验"
          secondary-text="重置"
          :primary-disabled="loading"
          @primary="handleQuery"
          @secondary="resetAll"
        />

        <PageActionRow
          primary-text="执行联合销户"
          :primary-disabled="loading || !canJointClose"
          @primary="handleJointClose"
        />
      </PageFormBlock>

      <PageInfoCard v-if="result" title="账户对信息" style="margin-top: 24px;">
        <PageDetailGrid>
          <div><strong>当前绑定是否有效：</strong>{{ result.associationActive ? '是' : '否' }}</div>
          <div><strong>投资者编号：</strong>{{ result.investorId || '--' }}</div>
          <div><strong>投资者姓名：</strong>{{ result.investorName || '--' }}</div>
          <div><strong>资金状态：</strong><AccountStatusTag :status="result.fundStatus" /></div>
          <div><strong>证券状态：</strong><AccountStatusTag :status="result.securityStatus" /></div>
          <div><strong>可用余额：</strong>¥ {{ formatAmount(result.availableBalance) }}</div>
          <div><strong>冻结金额：</strong>¥ {{ formatAmount(result.frozenAmount) }}</div>
          <div><strong>总金额：</strong>¥ {{ formatAmount(result.totalAmount) }}</div>
          <div><strong>持仓数量：</strong>{{ result.positionQuantity }}</div>
          <div><strong>冻结持仓数量：</strong>{{ result.frozenPositionQuantity }}</div>
          <div><strong>是否允许联合销户：</strong>{{ canJointClose ? '允许' : '不允许' }}</div>
        </PageDetailGrid>

        <div class="reason-block">
          <div class="reason-title">拒绝原因</div>
          <div v-if="refusalReasons.length" class="reason-list">
            <div v-for="item in refusalReasons" :key="item">{{ item }}</div>
          </div>
          <div v-else class="reason-pass">当前账户对满足联合销户前置条件。</div>
        </div>
      </PageInfoCard>

      <PageInfoCard v-if="result?.positions?.length" title="持仓明细" style="margin-top: 24px;">
        <el-table :data="result.positions" stripe style="width: 100%;">
          <el-table-column prop="stockCode" label="证券代码" min-width="120" />
          <el-table-column prop="stockName" label="证券名称" min-width="140" />
          <el-table-column prop="totalQuantity" label="总持仓" min-width="100" />
          <el-table-column prop="availableQuantity" label="可用持仓" min-width="100" />
          <el-table-column prop="frozenQuantity" label="冻结持仓" min-width="100" />
        </el-table>
      </PageInfoCard>

      <PageInfoCard v-if="closeResult" title="办理结果" style="margin-top: 24px;">
        <PageDetailGrid>
          <div><strong>资金账户号：</strong>{{ closeResult.fundAccountId }}</div>
          <div><strong>证券账户号：</strong>{{ closeResult.securitiesAccountId }}</div>
          <div><strong>联合销户结果：</strong>成功</div>
          <div><strong>绑定状态：</strong>{{ closeResult.associationStatus }}</div>
          <div><strong>资金账户状态：</strong><AccountStatusTag :status="closeResult.fundAccountStatus" /></div>
          <div><strong>证券账户状态：</strong><AccountStatusTag :status="closeResult.securityAccountStatus" /></div>
        </PageDetailGrid>
      </PageInfoCard>
    </PagePanel>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { AccountStatus } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageActionRow from '@/components/PageActionRow.vue'
import PageDetailGrid from '@/components/PageDetailGrid.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'
import { DEFAULT_OPERATOR_ID, DEFAULT_OPERATOR_NAME } from '@/utils/request/core'
import {
  getAssociationDetail,
  getFundAccountByNo,
  getSecuritiesAccountByNo,
  getSecuritiesPositions,
  jointClose
} from '@/utils/request'

const buildInitialForm = () => ({
  fundAccountNo: '',
  securitiesAccountNo: '',
  customerIdNumber: '',
  operatorId: DEFAULT_OPERATOR_ID,
  reason: '客户申请联合销户'
})

const form = reactive(buildInitialForm())
const loading = ref(false)
const result = ref(null)
const closeResult = ref(null)

const normalizeForm = () => {
  form.fundAccountNo = String(form.fundAccountNo || '').trim()
  form.securitiesAccountNo = String(form.securitiesAccountNo || '').trim()
  form.customerIdNumber = String(form.customerIdNumber || '').trim()
  form.operatorId = String(form.operatorId || '').trim()
  form.reason = String(form.reason || '').trim()
}

const formatAmount = (value) => Number(value || 0).toFixed(2)

const refusalReasons = computed(() => {
  if (!result.value) return []
  const reasons = []
  if (!result.value.fundExists) reasons.push('资金账户不存在')
  if (!result.value.securityExists) reasons.push('证券账户不存在')
  if (result.value.fundExists && result.value.securityExists && !result.value.sameInvestor) {
    reasons.push('资金账户与证券账户不属于同一投资者')
  }
  if (form.customerIdNumber && result.value.customerIdNumber && form.customerIdNumber !== result.value.customerIdNumber) {
    reasons.push('客户证件号与账户归属不一致')
  }
  if (!result.value.associationActive) reasons.push('当前账户对不存在唯一有效绑定')
  if (result.value.fundStatus !== AccountStatus.NORMAL) reasons.push('联合销户前，资金账户状态必须为 NORMAL')
  if (result.value.securityStatus !== AccountStatus.NORMAL) reasons.push('联合销户前，证券账户状态必须为 NORMAL')
  if (
    Number(result.value.availableBalance) !== 0 ||
    Number(result.value.frozenAmount) !== 0 ||
    Number(result.value.totalAmount) !== 0
  ) {
    reasons.push('联合销户前，资金账户余额、冻结金额、总金额必须全部清零')
  }
  if (result.value.positionQuantity > 0 || result.value.frozenPositionQuantity > 0) {
    reasons.push('联合销户前，证券账户必须无持仓、无冻结证券')
  }
  return reasons
})

const canJointClose = computed(() => result.value && refusalReasons.value.length === 0)

const handleQuery = async ({ preserveCloseResult = false } = {}) => {
  normalizeForm()
  if (!form.fundAccountNo || !form.securitiesAccountNo) {
    ElMessage.error('请同时输入资金账户号和证券账户号')
    return
  }
  loading.value = true
  if (!preserveCloseResult) {
    closeResult.value = null
  }
  try {
    const [fundRes, securityRes, associationRes, positionsRes] = await Promise.allSettled([
      getFundAccountByNo(form.fundAccountNo),
      getSecuritiesAccountByNo(form.securitiesAccountNo),
      getAssociationDetail({
        fundAccountNo: form.fundAccountNo,
        securitiesAccountNo: form.securitiesAccountNo
      }),
      getSecuritiesPositions({
        securitiesAccountNo: form.securitiesAccountNo
      })
    ])

    const fund = fundRes.status === 'fulfilled' ? fundRes.value.data : null
    const security = securityRes.status === 'fulfilled' ? securityRes.value.data : null
    const association = associationRes.status === 'fulfilled' ? associationRes.value.data : null
    const positions = positionsRes.status === 'fulfilled' ? (positionsRes.value.data || []) : []

    result.value = {
      fundExists: !!fund,
      securityExists: !!security,
      sameInvestor: !!(fund && security && fund.investorId === security.investorId),
      associationActive: association?.associationStatus === 'ACTIVE',
      investorId: security?.investorId || fund?.investorId || association?.investorId || '',
      investorName: security?.investorName || fund?.investorName || '',
      customerIdNumber: security?.idNo || fund?.idNo || '',
      fundStatus: fund?.accountStatus || 'NOT_FOUND',
      securityStatus: security?.accountStatus || 'NOT_FOUND',
      availableBalance: fund?.availableBalance || 0,
      frozenAmount: fund?.frozenAmount || 0,
      totalAmount: fund?.totalAmount || 0,
      positionQuantity: positions.reduce((sum, item) => sum + Number(item.totalQuantity || 0), 0),
      frozenPositionQuantity: positions.reduce((sum, item) => sum + Number(item.frozenQuantity || 0), 0),
      positions
    }
    ElMessage.success('账户对校验信息已更新')
  } catch (error) {
    result.value = null
    ElMessage.error(error.message || '查询失败')
  } finally {
    loading.value = false
  }
}

const handleJointClose = async () => {
  normalizeForm()
  if (!canJointClose.value) {
    ElMessage.error('当前账户对不满足联合销户条件')
    return
  }
  if (!form.customerIdNumber) {
    ElMessage.error('请输入客户证件号')
    return
  }
  if (!form.operatorId) {
    ElMessage.error('请输入工作人员号')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认对资金账户 ${form.fundAccountNo} 与证券账户 ${form.securitiesAccountNo} 执行联合销户？`,
      '联合销户确认',
      {
        confirmButtonText: '确认联合销户',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    loading.value = true
    const res = await jointClose({
      fundAccountNo: form.fundAccountNo,
      securitiesAccountNo: form.securitiesAccountNo,
      customerIdNumber: form.customerIdNumber,
      operatorId: form.operatorId,
      operatorName: DEFAULT_OPERATOR_NAME,
      reason: form.reason
    })
    closeResult.value = {
      fundAccountId: res.data.fund_account_id,
      securitiesAccountId: res.data.security_account_id,
      associationStatus: res.data.association_status,
      fundAccountStatus: res.data.fund_account_status,
      securityAccountStatus: res.data.security_account_status
    }
    await handleQuery({ preserveCloseResult: true })
    ElMessage.success('联合销户成功')
  } catch (error) {
    if (error !== 'cancel' && error?.message) {
      ElMessage.error(error.message || '联合销户失败')
    }
  } finally {
    loading.value = false
  }
}

const resetAll = () => {
  Object.assign(form, buildInitialForm())
  result.value = null
  closeResult.value = null
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

.reason-block {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-gray-200);
}

.reason-title {
  margin-bottom: 8px;
  font-weight: 600;
}

.reason-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--color-text-muted);
}

.reason-pass {
  color: var(--color-text-muted);
}
</style>
