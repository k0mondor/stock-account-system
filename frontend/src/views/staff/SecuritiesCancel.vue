<template>
  <div>
    <PageHeader title="注销证券账户" show-back />

    <PagePanel>
      <el-steps :active="step" align-center style="margin-bottom: 32px;">
        <el-step title="信息查询" />
        <el-step title="确认注销" />
        <el-step title="注销完成" />
      </el-steps>

      <PageFormBlock v-if="step === 0">
        <el-form class="page-form-stack" @submit.prevent>
          <el-form-item label="账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证件号码" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.idNo" placeholder="330102199001011234" style="width: 100%;" />
          </el-form-item>
        </el-form>
        <PageActionRow primary-text="查询" secondary-text="重置" @primary="handleQuery" @secondary="resetForm" />

        <PageInfoCard v-if="accountInfo" title="查询结果">
          <PageDetailGrid>
            <div><strong>账户号：</strong>{{ accountInfo.securitiesAccountNo }}</div>
            <div><strong>姓名：</strong>{{ accountInfo.investorName }}</div>
            <div><strong>证件号：</strong>{{ accountInfo.idNo }}</div>
            <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
          </PageDetailGrid>
          <PageActionRow
            primary-text="执行注销"
            :primary-disabled="accountInfo.accountStatus !== 'NORMAL'"
            @primary="handleCancel"
          />
          <div class="inline-tip" v-if="accountInfo.accountStatus !== 'NORMAL'">
            <p v-if="accountInfo.accountStatus !== 'NORMAL'" style="margin-top: 8px; color: var(--color-text-muted); font-size: 13px;">
              {{ cancelDisabledReason }}
            </p>
          </div>
        </PageInfoCard>
      </PageFormBlock>

      <div v-if="step === 1" class="page-result-stack">
        <div class="page-result-mark">✓</div>
        <h3>注销成功</h3>
        <p class="page-result-subtitle">账户状态已更新为 CLOSED（销户）</p>
        <PageInfoCard class="result-card">
          <p style="margin: 0 0 8px;"><strong>账户号：</strong>{{ accountInfo.securitiesAccountNo }}</p>
          <p style="margin: 0 0 8px;"><strong>投资者：</strong>{{ accountInfo.investorName }}</p>
          <p style="margin: 0;"><strong>当前状态：</strong><AccountStatusTag status="CLOSED" /></p>
        </PageInfoCard>
      </div>
    </PagePanel>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSecuritiesAccountByNo, cancelSecuritiesAccount } from '@/utils/request'
import { AccountStatus } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageActionRow from '@/components/PageActionRow.vue'
import PageDetailGrid from '@/components/PageDetailGrid.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'

const step = ref(0)
const form = ref({
  securitiesAccountNo: '',
  idNo: ''
})
const accountInfo = ref(null)

const normalizeValue = (value) => String(value || '').trim()

const cancelDisabledReason = computed(() => {
  if (!accountInfo.value) return ''
  const status = accountInfo.value.accountStatus
  if (status === AccountStatus.CLOSED) return '账户已销户'
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
      const inputIdNo = normalizeValue(form.value.idNo)
      const accountIdNo = normalizeValue(res.data.idNo)

      if (inputIdNo && inputIdNo !== accountIdNo) {
        accountInfo.value = null
        ElMessage.error('证件号码与账户信息不匹配')
        return
      }

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
    const res = await cancelSecuritiesAccount({
      securitiesAccountNo: accountInfo.value.securitiesAccountNo,
      idNo: form.value.idNo
    })
    accountInfo.value = res.data
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
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.inline-tip {
  text-align: center;
}

.result-card {
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}
</style>
