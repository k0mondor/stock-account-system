<template>
  <div>
    <PageHeader title="冻结/解冻" />

    <PagePanel>
      <PageInfoCard title="办理说明" style="margin-bottom: 24px;">
        <p class="inline-tip">本页仅处理普通冻结与解冻。普通冻结不会自动修改关联账户状态，但会影响联合业务、交易业务和联合销户办理。</p>
      </PageInfoCard>

      <div class="workbench-grid">
        <PageFormBlock width="wide">
          <h4 class="section-title">业务前校验</h4>
          <el-form class="page-form-stack" @submit.prevent>
            <el-form-item label="账户类型" label-position="top" style="margin-bottom: 0;">
              <el-select v-model="checkForm.accountType" style="width: 100%;">
                <el-option v-for="item in accountTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户号" label-position="top" style="margin-bottom: 0;">
              <el-input v-model="checkForm.accountId" placeholder="FUND000001 / SEC000001" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="业务类型" label-position="top" style="margin-bottom: 0;">
              <el-select v-model="checkForm.operationType" style="width: 100%;">
                <el-option v-for="item in operationOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-form>
          <PageActionRow
            primary-text="执行校验"
            secondary-text="重置"
            :primary-disabled="loadingCheck"
            @primary="handleCheck"
            @secondary="resetCheck"
          />
        </PageFormBlock>

        <PageFormBlock width="wide">
          <h4 class="section-title">冻结 / 解冻</h4>
          <el-form class="page-form-stack" @submit.prevent>
            <el-form-item label="账户类型" label-position="top" style="margin-bottom: 0;">
              <el-select v-model="changeForm.accountType" style="width: 100%;">
                <el-option v-for="item in accountTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户号" label-position="top" style="margin-bottom: 0;">
              <el-input v-model="changeForm.accountId" placeholder="FUND000001 / SEC000001" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="目标状态" label-position="top" style="margin-bottom: 0;">
              <el-select v-model="changeForm.targetStatus" style="width: 100%;">
                <el-option label="冻结" value="FROZEN" />
                <el-option label="解冻为正常" value="NORMAL" />
              </el-select>
            </el-form-item>
            <el-form-item label="工作人员号" label-position="top" style="margin-bottom: 0;">
              <el-input v-model="changeForm.operatorId" placeholder="STAFF000001" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="办理原因" label-position="top" style="margin-bottom: 0;">
              <el-input
                v-model="changeForm.reason"
                type="textarea"
                :rows="3"
                maxlength="256"
                show-word-limit
                placeholder="请输入冻结或解冻原因"
                style="width: 100%;"
              />
            </el-form-item>
          </el-form>
          <PageActionRow
            primary-text="执行状态变更"
            :primary-disabled="loadingChange"
            @primary="handleChangeStatus"
          />
        </PageFormBlock>
      </div>

      <PageInfoCard v-if="checkResult" title="状态校验结果" style="margin-top: 24px;">
        <PageDetailGrid>
          <div><strong>账户类型：</strong>{{ accountTypeLabel[checkResult.accountType] || checkResult.accountType }}</div>
          <div><strong>账户号：</strong>{{ checkResult.accountId }}</div>
          <div><strong>当前状态：</strong><AccountStatusTag :status="checkResult.status" /></div>
          <div><strong>业务放行：</strong>{{ checkResult.allowed ? '允许' : '拒绝' }}</div>
        </PageDetailGrid>
        <p v-if="checkResult.reason" class="result-reason">原因：{{ checkResult.reason }}</p>
      </PageInfoCard>

      <PageInfoCard v-if="changeResult" title="最新状态变更" style="margin-top: 24px;">
        <PageDetailGrid>
          <div><strong>账户类型：</strong>{{ accountTypeLabel[changeResult.accountType] || changeResult.accountType }}</div>
          <div><strong>账户号：</strong>{{ changeResult.accountId }}</div>
          <div><strong>变更后状态：</strong><AccountStatusTag :status="changeResult.status" /></div>
          <div><strong>办理结果：</strong>{{ changeResult.allowed ? '成功' : '失败' }}</div>
        </PageDetailGrid>
      </PageInfoCard>
    </PagePanel>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { changeAccountStatus, checkAccountStatus } from '@/utils/request'
import { DEFAULT_OPERATOR_ID, DEFAULT_OPERATOR_NAME } from '@/utils/request/core'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageActionRow from '@/components/PageActionRow.vue'
import PageDetailGrid from '@/components/PageDetailGrid.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'

const accountTypeOptions = [
  { label: '资金账户', value: 'FUND' },
  { label: '证券账户', value: 'SECURITIES' }
]

const accountTypeLabel = {
  FUND: '资金账户',
  SECURITY: '证券账户',
  SECURITIES: '证券账户'
}

const operationOptions = computed(() => {
  const baseOptions = [
    { label: '查询', value: 'QUERY' },
    { label: '挂失', value: 'LOST' },
    { label: '补办', value: 'REISSUE' },
    { label: '冻结账户', value: 'ACCOUNT_FREEZE' }
  ]
  if (checkForm.accountType === 'FUND') {
    return [
      ...baseOptions,
      { label: '存款', value: 'DEPOSIT' },
      { label: '取款', value: 'WITHDRAW' },
      { label: '资金账户密码重置', value: 'CHANGE_PWD' },
      { label: '联合销户', value: 'CANCEL' }
    ]
  }
  return [...baseOptions, { label: '联合销户', value: 'CANCEL' }]
})

const buildCheckForm = () => ({
  accountType: 'FUND',
  accountId: '',
  operationType: 'QUERY'
})

const buildChangeForm = () => ({
  accountType: 'FUND',
  accountId: '',
  targetStatus: 'FROZEN',
  operatorId: DEFAULT_OPERATOR_ID,
  reason: '柜台人工办理'
})

const checkForm = reactive(buildCheckForm())
const changeForm = reactive(buildChangeForm())
const loadingCheck = ref(false)
const loadingChange = ref(false)
const checkResult = ref(null)
const changeResult = ref(null)

const normalizeCheckForm = () => {
  checkForm.accountId = String(checkForm.accountId || '').trim()
}

const normalizeChangeForm = () => {
  changeForm.accountId = String(changeForm.accountId || '').trim()
  changeForm.operatorId = String(changeForm.operatorId || '').trim()
  changeForm.reason = String(changeForm.reason || '').trim()
}

const handleCheck = async () => {
  normalizeCheckForm()
  if (!checkForm.accountId) {
    ElMessage.error('请输入账户号后再校验')
    return
  }
  loadingCheck.value = true
  try {
    const res = await checkAccountStatus({
      accountType: checkForm.accountType,
      accountId: checkForm.accountId,
      operationType: checkForm.operationType
    })
    checkResult.value = {
      accountType: res.data.account_type,
      accountId: res.data.account_id,
      status: res.data.status,
      allowed: res.data.allowed,
      reason: res.data.reason
    }
    ElMessage.success('状态校验完成')
  } catch (error) {
    checkResult.value = null
    ElMessage.error(error.message || '状态校验失败')
  } finally {
    loadingCheck.value = false
  }
}

const handleChangeStatus = async () => {
  normalizeChangeForm()
  if (!changeForm.accountId) {
    ElMessage.error('请输入账户号后再办理状态变更')
    return
  }
  if (!changeForm.operatorId) {
    ElMessage.error('请输入工作人员号')
    return
  }
  loadingChange.value = true
  try {
    const res = await changeAccountStatus({
      accountType: changeForm.accountType,
      accountId: changeForm.accountId,
      targetStatus: changeForm.targetStatus,
      operatorId: changeForm.operatorId,
      operatorName: DEFAULT_OPERATOR_NAME,
      reason: changeForm.reason || null
    })
    changeResult.value = {
      accountType: res.data.account_type,
      accountId: res.data.account_id,
      status: res.data.status,
      allowed: res.data.allowed
    }
    ElMessage.success(changeForm.targetStatus === 'FROZEN' ? '账户冻结成功' : '账户解冻成功')
  } catch (error) {
    ElMessage.error(error.message || '状态变更失败')
  } finally {
    loadingChange.value = false
  }
}

const resetCheck = () => {
  Object.assign(checkForm, buildCheckForm())
  checkResult.value = null
}
</script>

<style scoped>
.workbench-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.section-title {
  margin: 0 0 20px;
  font-size: 16px;
  font-weight: 600;
}

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

.result-reason {
  margin: 16px 0 0;
  font-size: 13px;
  color: var(--color-text-muted);
}
</style>
