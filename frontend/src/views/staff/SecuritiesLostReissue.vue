<template>
  <div>
    <PageHeader title="证券账户挂失补办" show-back />

    <PagePanel>
      <el-steps :active="step" align-center style="margin-bottom: 32px;">
        <el-step title="信息查询" />
        <el-step title="执行挂失" />
        <el-step title="恢复账户" />
      </el-steps>

      <PageFormBlock v-if="step === 0">
        <el-form class="page-form-stack" @submit.prevent>
          <el-form-item label="原账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="投资者姓名" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.investorName" placeholder="张三" style="width: 100%;" />
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
            <div><strong>证件：</strong>{{ accountInfo.idNo }}</div>
            <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
          </PageDetailGrid>
          <PageActionRow
            primary-text="执行挂失"
            :primary-disabled="accountInfo.accountStatus !== AccountStatus.NORMAL"
            @primary="handleLost"
          />
        </PageInfoCard>
      </PageFormBlock>

      <div v-if="step === 1" class="page-result-stack">
        <div class="page-result-mark">✓</div>
        <h3>挂失成功</h3>
        <p class="page-result-subtitle">账户状态已更新为 LOST</p>
        <p class="impact-tip">对关联账户影响：证券账户已挂失，关联资金账户已自动冻结。</p>
        <PageActionRow primary-text="继续恢复账户" @primary="nextStep" />
      </div>

      <PageFormBlock v-if="step === 2" width="medium">
        <PageInfoCard variant="muted" align="center">
          <h4 class="step-title">恢复原证券账户</h4>
          <p class="page-result-subtitle">补办后恢复为正常状态，账户号保持不变</p>
          <PageActionRow primary-text="确认恢复" @primary="handleReissue" />
        </PageInfoCard>

        <PageInfoCard v-if="newAccount" variant="success">
          <h4 style="margin: 0 0 16px; color: #000;">补办成功！账户已恢复</h4>
          <p><strong>证券账户号：</strong><span style="font-size: 18px; font-weight: 600;">{{ newAccount.securitiesAccountNo }}</span></p>
          <p><strong>投资者姓名：</strong>{{ newAccount.investorName }}</p>
          <p><strong>证件号码：</strong>{{ newAccount.idNo }}</p>
          <p><strong>状态：</strong>正常</p>
          <p class="impact-tip" style="margin-top: 12px;">对关联账户影响：证券账户已补办恢复，若资金账户因本次挂失被冻结，将同步恢复正常。</p>
        </PageInfoCard>
      </PageFormBlock>
    </PagePanel>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSecuritiesAccountByNo, reportSecuritiesAccountLost, reissueSecuritiesAccount } from '@/utils/request'
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
  investorName: '',
  idNo: ''
})
const accountInfo = ref(null)
const newAccount = ref(null)

const normalizeValue = (value) => String(value || '').trim()

const handleQuery = async () => {
  if (!form.value.securitiesAccountNo) {
    ElMessage.warning('请输入原账户号')
    return
  }
  try {
    const res = await getSecuritiesAccountByNo(form.value.securitiesAccountNo)
    if (res.data) {
      const inputInvestorName = normalizeValue(form.value.investorName)
      const inputIdNo = normalizeValue(form.value.idNo)
      const accountInvestorName = normalizeValue(res.data.investorName)
      const accountIdNo = normalizeValue(res.data.idNo)

      if (inputInvestorName && inputInvestorName !== accountInvestorName) {
        accountInfo.value = null
        ElMessage.error('投资者姓名与账户信息不匹配')
        return
      }

      if (inputIdNo && inputIdNo !== accountIdNo) {
        accountInfo.value = null
        ElMessage.error('证件号码与账户信息不匹配')
        return
      }

      accountInfo.value = res.data
      ElMessage.success('查询成功')
    } else {
      ElMessage.error('未找到对应账户')
    }
  } catch (e) {
    ElMessage.error(e.message || '查询失败')
  }
}

const handleLost = async () => {
  if (!accountInfo.value) return
  try {
    const res = await reportSecuritiesAccountLost({
      securitiesAccountNo: accountInfo.value.securitiesAccountNo,
      idNo: form.value.idNo
    })
    accountInfo.value = res.data
    ElMessage.success('账户已成功挂失')
    step.value = 1
  } catch (e) {
    ElMessage.error(e.message || '挂失失败')
  }
}

const nextStep = () => {
  step.value = 2
}

const handleReissue = async () => {
  if (!accountInfo.value) return
  try {
    const res = await reissueSecuritiesAccount({
      securitiesAccountNo: accountInfo.value.securitiesAccountNo,
      idNo: form.value.idNo
    })
    newAccount.value = res.data
    ElMessage.success(`补办成功！账户 ${newAccount.value.securitiesAccountNo} 已恢复正常`)
  } catch (e) {
    ElMessage.error(e.message || '补办失败')
  }
}

const resetForm = () => {
  form.value = { securitiesAccountNo: '', investorName: '', idNo: '' }
  accountInfo.value = null
  newAccount.value = null
  step.value = 0
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-title {
  margin-bottom: 24px;
}

.impact-tip {
  margin: 8px 0 0;
  color: var(--color-text-muted);
}
</style>
