<template>
  <div>
    <PageHeader title="资金账户挂失补办" show-back />

    <el-card style="margin: 24px auto 0; max-width: 1100px; background: var(--color-white);">
      <el-steps :active="step" align-center style="margin-bottom: 32px;">
        <el-step title="信息查询" />
        <el-step title="执行挂失" />
        <el-step title="补办新卡" />
      </el-steps>

      <div v-if="step === 0" style="max-width: 400px; margin: 0 auto;">
        <el-form @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="原资金账户号" label-position="top" style="margin-bottom: 0;">
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
            <div><strong>余额：</strong>¥ {{ accountInfo.balance.toFixed(2) }}</div>
            <div><strong>状态：</strong><AccountStatusTag :status="accountInfo.accountStatus" /></div>
          </div>
          <div style="margin-top: 24px; text-align: center;">
            <button class="btn-primary" @click="handleLost" :disabled="accountInfo.accountStatus !== 'NORMAL'">执行挂失</button>
          </div>
        </div>
      </div>

      <div v-if="step === 1" style="text-align: center; padding: 40px 0;">
        <div style="font-size: 64px; margin-bottom: 16px;">✓</div>
        <h3>挂失成功</h3>
        <p style="color: var(--color-text-muted);">资金已冻结，状态更新为 LOST</p>
        <button class="btn-primary" @click="nextStep" style="margin-top: 24px;">继续补办新账户</button>
      </div>

      <div v-if="step === 2" style="max-width: 520px; margin: 0 auto; text-align: center;">
        <div style="padding: 32px; border: 1px solid var(--color-border); background: #fafafa;">
          <h4 style="margin-bottom: 24px;">补办新资金账户</h4>
          <p style="margin-bottom: 16px; color: var(--color-text-muted);">系统将复制原有余额并生成新账户</p>
          <el-input v-model="newPassword" placeholder="请输入新交易密码（默认123456）" style="max-width: 280px; margin-bottom: 24px;" type="password" />
          <button class="btn-primary" @click="handleReissue" style="padding: 12px 48px;">确认补办</button>
        </div>

        <div v-if="newAccount" style="margin-top: 32px; padding: 24px; border: 2px solid #000; text-align: left;">
          <h4 style="margin: 0 0 16px; color: #000;">补办成功！新账户信息</h4>
          <p><strong>新资金账户号：</strong><span style="font-size: 18px; font-weight: 600;">{{ newAccount.fundAccountNo }}</span></p>
          <p><strong>复制余额：</strong>¥ {{ newAccount.balance.toFixed(2) }}</p>
          <p><strong>新密码：</strong>{{ newPassword || '123456' }}</p>
          <p><strong>状态：</strong>正常</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getFundAccountByNo, openFundAccount } from '@/utils/request'
import { AccountStatus } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageHeader from '@/components/PageHeader.vue'

const step = ref(0)
const form = ref({
  fundAccountNo: '',
  idNo: ''
})
const accountInfo = ref(null)
const newAccount = ref(null)
const newPassword = ref('123456')

const handleQuery = async () => {
  if (!form.value.fundAccountNo) {
    ElMessage.warning('请输入原资金账户号')
    return
  }
  try {
    const res = await getFundAccountByNo(form.value.fundAccountNo)
    if (res.data) {
      accountInfo.value = res.data
      ElMessage.success('查询成功')
    } else {
      ElMessage.error('未找到对应账户')
    }
  } catch (e) {
    ElMessage.error('查询失败')
  }
}

const handleLost = () => {
  if (!accountInfo.value) return
  accountInfo.value.accountStatus = AccountStatus.LOST
  ElMessage.success('资金账户已挂失并冻结')
  step.value = 1
}

const nextStep = () => {
  step.value = 2
}

const handleReissue = async () => {
  if (!accountInfo.value) return
  try {
    const res = await openFundAccount({
      investorId: accountInfo.value.investorId,
      bankCardNo: accountInfo.value.bankCardNo || '6222021234567890'
    })
    newAccount.value = res.data.account
    newAccount.value.balance = accountInfo.value.balance
    ElMessage.success(`补办成功！新账户号：${newAccount.value.fundAccountNo}，余额已复制`)
  } catch (e) {
    ElMessage.error('补办失败')
  }
}

const resetForm = () => {
  form.value = { fundAccountNo: '', idNo: '' }
  accountInfo.value = null
  newAccount.value = null
  newPassword.value = '123456'
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