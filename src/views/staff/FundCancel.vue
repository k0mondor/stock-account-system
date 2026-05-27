<template>
  <div>
    <PageHeader title="注销资金账户" show-back />

    <el-card style="margin: 24px auto 0; max-width: 1100px; background: var(--color-white);">
      <el-steps :active="step" align-center style="margin-bottom: 32px;">
        <el-step title="信息查询" />
        <el-step title="确认注销" />
        <el-step title="注销完成" />
      </el-steps>

      <div v-if="step === 0" style="max-width: 400px; margin: 0 auto;">
        <el-form @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="资金账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FND00000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="投资者身份证号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.idNo" placeholder="330102199001011234" style="width: 100%;" />
          </el-form-item>
        </el-form>
        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleQuery">查询</button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetForm">重置</button>
        </div>

        <div v-if="accountInfo" style="margin-top: 32px; padding: 24px; border: 1px solid var(--color-border);">
          <h4 style="margin: 0 0 16px; font-weight: 600;">查询结果</h4>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div><strong>账户号：</strong>{{ accountInfo.fundAccountNo }}</div>
            <div><strong>投资者ID：</strong>{{ accountInfo.investorId }}</div>
            <div><strong>可用资金：</strong>¥ {{ accountInfo.availableBalance.toFixed(2) }}</div>
            <div><strong>冻结资金：</strong>¥ {{ accountInfo.frozenAmount.toFixed(2) }}</div>
            <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
          </div>
          <div style="margin-top: 24px; text-align: center;">
            <button
              class="btn-primary"
              @click="handleCancel"
              :disabled="!canCancel"
            >
              执行注销
            </button>
            <p v-if="!canCancel && accountInfo" style="margin-top: 8px; color: var(--color-text-muted); font-size: 13px;">
              {{ cancelDisabledReason }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="step === 1" style="text-align: center; padding: 40px 0;">
        <div style="font-size: 64px; margin-bottom: 16px;">✓</div>
        <h3>注销成功</h3>
        <p style="color: var(--color-text-muted);">账户状态已更新为 CLOSED（销户）</p>
        <div style="margin-top: 24px; padding: 24px; max-width: 400px; margin-left: auto; margin-right: auto; border: 1px solid var(--color-border); text-align: left;">
          <p style="margin: 0 0 8px;"><strong>账户号：</strong>{{ accountInfo.fundAccountNo }}</p>
          <p style="margin: 0 0 8px;"><strong>投资者ID：</strong>{{ accountInfo.investorId }}</p>
          <p style="margin: 0;"><strong>当前状态：</strong><AccountStatusTag status="CLOSED" /></p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFundAccountByNo, cancelFundAccount } from '@/utils/request'
import { AccountStatus } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageHeader from '@/components/PageHeader.vue'

const step = ref(0)
const form = ref({
  fundAccountNo: '',
  idNo: ''
})
const accountInfo = ref(null)

const canCancel = computed(() => {
  if (!accountInfo.value) return false
  const status = accountInfo.value.accountStatus
  if (status !== AccountStatus.NORMAL) return false
  if (accountInfo.value.availableBalance > 0 || accountInfo.value.frozenAmount > 0) return false
  return true
})

const cancelDisabledReason = computed(() => {
  if (!accountInfo.value) return ''
  const status = accountInfo.value.accountStatus
  if (status === AccountStatus.CLOSED) return '账户已销户'
  if (status === AccountStatus.LOST) return '账户已挂失，请先补办后再注销'
  if (status === AccountStatus.FROZEN) return '账户已冻结，无法注销'
  if (accountInfo.value.availableBalance > 0 || accountInfo.value.frozenAmount > 0) return '账户资金不为 0，请先转出/解冻后再注销'
  return ''
})

const handleQuery = async () => {
  if (!form.value.fundAccountNo) {
    ElMessage.warning('请输入资金账户号')
    return
  }
  try {
    const res = await getFundAccountByNo(form.value.fundAccountNo)
    if (res.data) {
      accountInfo.value = res.data
      ElMessage.success('查询成功')
    } else {
      accountInfo.value = null
      ElMessage.error('未找到对应账户')
    }
  } catch (e) {
    ElMessage.error('查询失败')
  }
}

const handleCancel = async () => {
  if (!accountInfo.value) return
  try {
    await ElMessageBox.confirm(
      `确认注销资金账户 ${accountInfo.value.fundAccountNo}？注销后将无法恢复。`,
      '注销确认',
      {
        confirmButtonText: '确认注销',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await cancelFundAccount(accountInfo.value.fundAccountNo)
    accountInfo.value.accountStatus = AccountStatus.CLOSED
    step.value = 1
    ElMessage.success('注销成功')
  } catch (e) {
    if (e !== 'cancel' && e?.message) {
      ElMessage.error(e.message || '注销失败')
    }
  }
}

const resetForm = () => {
  form.value = { fundAccountNo: '', idNo: '' }
  accountInfo.value = null
  step.value = 0
}
</script>

<style scoped>
</style>
