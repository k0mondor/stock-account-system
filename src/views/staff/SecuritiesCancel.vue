<template>
  <div>
    <PageHeader title="注销证券账户" show-back />

    <el-card style="margin: 24px auto 0; max-width: 1100px; background: var(--color-white);">
      <el-steps :active="step" align-center style="margin-bottom: 32px;">
        <el-step title="信息查询" />
        <el-step title="确认注销" />
        <el-step title="注销完成" />
      </el-steps>

      <div v-if="step === 0" style="max-width: 400px; margin: 0 auto;">
        <el-form @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC00000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证件号码" label-position="top" style="margin-bottom: 0;">
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
            <div><strong>账户号：</strong>{{ accountInfo.securitiesAccountNo }}</div>
            <div><strong>姓名：</strong>{{ accountInfo.investorName }}</div>
            <div><strong>证件号：</strong>{{ accountInfo.idNo }}</div>
            <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
          </div>
          <div style="margin-top: 24px; text-align: center;">
            <button
              class="btn-primary"
              @click="handleCancel"
              :disabled="accountInfo.accountStatus !== 'NORMAL'"
            >
              执行注销
            </button>
            <p v-if="accountInfo.accountStatus !== 'NORMAL'" style="margin-top: 8px; color: var(--color-text-muted); font-size: 13px;">
              {{ cancelDisabledReason }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="step === 1" style="text-align: center; padding: 40px 0;">
        <div style="font-size: 64px; margin-bottom: 16px;">✓</div>
        <h3>注销成功</h3>
        <p style="color: var(--color-text-muted);">账户状态已更新为 CANCELLED（销户）</p>
        <div style="margin-top: 24px; padding: 24px; max-width: 400px; margin-left: auto; margin-right: auto; border: 1px solid var(--color-border); text-align: left;">
          <p style="margin: 0 0 8px;"><strong>账户号：</strong>{{ accountInfo.securitiesAccountNo }}</p>
          <p style="margin: 0 0 8px;"><strong>投资者：</strong>{{ accountInfo.investorName }}</p>
          <p style="margin: 0;"><strong>当前状态：</strong><AccountStatusTag status="CANCELLED" /></p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSecuritiesAccountByNo, cancelSecuritiesAccount } from '@/utils/request'
import { AccountStatus } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageHeader from '@/components/PageHeader.vue'

const step = ref(0)
const form = ref({
  securitiesAccountNo: '',
  idNo: ''
})
const accountInfo = ref(null)

const cancelDisabledReason = computed(() => {
  if (!accountInfo.value) return ''
  const status = accountInfo.value.accountStatus
  if (status === AccountStatus.CANCELLED) return '账户已销户'
  if (status === AccountStatus.LOST) return '账户已挂失，请先补办后再注销'
  if (status === AccountStatus.FROZEN) return '账户已冻结，无法注销'
  return ''
})

const handleQuery = async () => {
  if (!form.value.securitiesAccountNo) {
    ElMessage.warning('请输入账户号')
    return
  }
  try {
    const res = await getSecuritiesAccountByNo(form.value.securitiesAccountNo)
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
      `确认注销账户 ${accountInfo.value.securitiesAccountNo}（${accountInfo.value.investorName}）？注销后将无法恢复。`,
      '注销确认',
      {
        confirmButtonText: '确认注销',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await cancelSecuritiesAccount(accountInfo.value.securitiesAccountNo)
    accountInfo.value.accountStatus = AccountStatus.CANCELLED
    step.value = 1
    ElMessage.success('注销成功')
  } catch (e) {
    if (e !== 'cancel' && e?.message) {
      ElMessage.error(e.message || '注销失败')
    }
  }
}

const resetForm = () => {
  form.value = { securitiesAccountNo: '', idNo: '' }
  accountInfo.value = null
  step.value = 0
}
</script>

<style scoped>
.btn-primary, .btn-secondary {
  padding: 10px 28px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 0;
  cursor: pointer;
}
</style>