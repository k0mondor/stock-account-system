<template>
  <div>
    <PageHeader title="证券账户挂失补办" show-back />

    <el-card style="margin: 24px auto 0; max-width: 1100px; background: var(--color-white);">
      <el-steps :active="step" align-center style="margin-bottom: 32px;">
        <el-step title="信息查询" />
        <el-step title="执行挂失" />
        <el-step title="补办新卡" />
      </el-steps>

      <div v-if="step === 0" style="max-width: 400px; margin: 0 auto;">
        <el-form @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="原账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC00000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="投资者姓名" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="form.investorName" placeholder="张三" style="width: 100%;" />
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
            <div><strong>证件：</strong>{{ accountInfo.idNo }}</div>
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
        <p style="color: var(--color-text-muted);">账户状态已更新为 LOST</p>
        <button class="btn-primary" @click="nextStep" style="margin-top: 24px;">继续补办新账户</button>
      </div>

      <div v-if="step === 2" style="max-width: 520px; margin: 0 auto; text-align: center;">
        <div style="padding: 32px; border: 1px solid var(--color-border); background: #fafafa;">
          <h4 style="margin-bottom: 24px;">补办新证券账户</h4>
          <p style="margin-bottom: 32px; color: var(--color-text-muted);">系统将为投资者生成新账户号并关联原有信息</p>
          <button class="btn-primary" @click="handleReissue" style="padding: 12px 48px;">确认补办</button>
        </div>

        <div v-if="newAccount" style="margin-top: 32px; padding: 24px; border: 2px solid #000; text-align: left;">
          <h4 style="margin: 0 0 16px; color: #000;">补办成功！新账户信息</h4>
          <p><strong>新证券账户号：</strong><span style="font-size: 18px; font-weight: 600;">{{ newAccount.securitiesAccountNo }}</span></p>
          <p><strong>投资者姓名：</strong>{{ newAccount.investorName }}</p>
          <p><strong>证件号码：</strong>{{ newAccount.idNo }}</p>
          <p><strong>状态：</strong>正常</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSecuritiesAccountByNo, openSecuritiesAccount } from '@/utils/request'
import { AccountStatus } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageHeader from '@/components/PageHeader.vue'

const step = ref(0)
const form = ref({
  securitiesAccountNo: '',
  investorName: '',
  idNo: ''
})
const accountInfo = ref(null)
const newAccount = ref(null)

const handleQuery = async () => {
  if (!form.value.securitiesAccountNo) {
    ElMessage.warning('请输入原账户号')
    return
  }
  try {
    const res = await getSecuritiesAccountByNo(form.value.securitiesAccountNo)
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

const handleLost = async () => {
  if (!accountInfo.value) return
  accountInfo.value.accountStatus = AccountStatus.LOST
  ElMessage.success('账户已成功挂失，状态更新为 LOST')
  step.value = 1
}

const nextStep = () => {
  step.value = 2
}

const handleReissue = async () => {
  if (!accountInfo.value) return
  try {
    const res = await openSecuritiesAccount({
      investorId: accountInfo.value.investorId,
      investorName: accountInfo.value.investorName,
      idType: accountInfo.value.idType,
      idNo: accountInfo.value.idNo,
      phone: accountInfo.value.phone
    })
    newAccount.value = res.data.account
    ElMessage.success(`补办成功！新账户号：${newAccount.value.securitiesAccountNo}`)
  } catch (e) {
    ElMessage.error('补办失败')
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
</style>
