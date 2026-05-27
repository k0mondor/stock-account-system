<!-- src/views/staff/JointOpen.vue -->
<template>
  <div>
    <PageHeader title="联合开户" />

    <el-card style="margin: 24px auto 0; max-width: 720px; background: var(--color-white);">
      <div style="max-width: 460px; margin: 0 auto 32px;">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="证券账户信息" />
          <el-step title="资金账户信息" />
          <el-step title="确认并提交" />
        </el-steps>
      </div>

      <div style="max-width: 400px; margin: 0 auto;">

        <!-- Step 1: 证券账户 -->
        <div v-if="currentStep === 0">
          <el-form ref="securitiesFormRef" :model="securitiesForm" :rules="securitiesRules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
            <el-form-item label="投资者姓名" label-position="top" prop="investorName" style="margin-bottom: 0;">
              <el-input v-model="securitiesForm.investorName" placeholder="请输入姓名" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="证件类型" label-position="top" prop="idType" style="margin-bottom: 0;">
              <el-select v-model="securitiesForm.idType" placeholder="请选择" style="width: 100%;">
                <el-option
                  v-for="(label, key) in IdTypeLabel"
                  :key="key"
                  :label="label"
                  :value="key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="证件号码" label-position="top" prop="idNo" style="margin-bottom: 0;">
              <el-input v-model="securitiesForm.idNo" placeholder="请输入证件号码" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="联系电话" label-position="top" prop="phone" style="margin-bottom: 0;">
              <el-input v-model="securitiesForm.phone" placeholder="请输入手机号" style="width: 100%;" />
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: 资金账户 -->
        <div v-if="currentStep === 1">
          <el-form ref="fundFormRef" :model="fundForm" :rules="fundRules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
            <el-form-item label="银行卡号" label-position="top" prop="bankCardNo" style="margin-bottom: 0;">
              <el-input v-model="fundForm.bankCardNo" placeholder="请输入银行卡号" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="交易密码" label-position="top" prop="tradePwd" style="margin-bottom: 0;">
              <el-input v-model="fundForm.tradePwd" type="password" placeholder="请输入交易密码" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="确认交易密码" label-position="top" prop="tradePwdConfirm" style="margin-bottom: 0;">
              <el-input v-model="fundForm.tradePwdConfirm" type="password" placeholder="请再次输入" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="取款密码" label-position="top" prop="withdrawPwd" style="margin-bottom: 0;">
              <el-input v-model="fundForm.withdrawPwd" type="password" placeholder="请输入取款密码" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="确认取款密码" label-position="top" prop="withdrawPwdConfirm" style="margin-bottom: 0;">
              <el-input v-model="fundForm.withdrawPwdConfirm" type="password" placeholder="请再次输入" style="width: 100%;" />
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 3: 确认 -->
        <div v-if="currentStep === 2">
          <div style="background: var(--color-beige); padding: 24px; border: 1px solid var(--color-gray-200); margin-bottom: 24px; text-align: left;">
            <h4 style="margin: 0 0 16px; font-weight: 600;">确认信息</h4>
            <p><strong>投资者：</strong>{{ securitiesForm.investorName }}</p>
            <p><strong>证件：</strong>{{ IdTypeLabel[securitiesForm.idType] }} {{ securitiesForm.idNo }}</p>
            <p><strong>电话：</strong>{{ securitiesForm.phone }}</p>
            <p><strong>银行卡：</strong>{{ fundForm.bankCardNo }}</p>
            <p style="color: var(--color-gray-500); margin-top: 16px;">提交后将同时开设证券账户与资金账户，并自动建立关联。</p>
          </div>
        </div>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button v-if="currentStep > 0" class="btn-secondary" @click="prevStep" style="margin-right: 12px;">上一步</button>
          <button v-if="currentStep < 2" class="btn-primary" @click="nextStep">下一步</button>
          <button v-if="currentStep === 2" class="btn-primary" @click="submitJoint">确认提交</button>
        </div>

      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { openSecuritiesAccount, openFundAccount, createAssociation } from '@/utils/request'
import { IdTypeLabel } from '@/constants/enums'
import PageHeader from '@/components/PageHeader.vue'

const currentStep = ref(0)

const securitiesForm = ref({
  investorName: '',
  idType: 'ID_CARD',
  idNo: '',
  phone: ''
})

const fundForm = ref({
  bankCardNo: '',
  tradePwd: '',
  tradePwdConfirm: '',
  withdrawPwd: '',
  withdrawPwdConfirm: ''
})

const securitiesRules = {
  investorName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  idType: [{ required: true, message: '请选择证件类型', trigger: 'change' }],
  idNo: [{ required: true, message: '请输入证件号码', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const fundRules = {
  bankCardNo: [{ required: true, message: '请输入银行卡号', trigger: 'blur' }],
  tradePwd: [{ required: true, message: '请输入交易密码', trigger: 'blur' }],
  tradePwdConfirm: [
    { required: true, message: '请确认交易密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== fundForm.value.tradePwd) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ],
  withdrawPwd: [{ required: true, message: '请输入取款密码', trigger: 'blur' }],
  withdrawPwdConfirm: [
    { required: true, message: '请确认取款密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== fundForm.value.withdrawPwd) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

const securitiesFormRef = ref(null)
const fundFormRef = ref(null)

const nextStep = async () => {
  if (currentStep.value === 0) {
    await securitiesFormRef.value.validate()
  } else if (currentStep.value === 1) {
    await fundFormRef.value.validate()
  }
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const submitJoint = async () => {
  try {
    const secRes = await openSecuritiesAccount(securitiesForm.value)
    const secNo = secRes.data.accountNo

    const fundRes = await openFundAccount({
      investorId: secRes.data.account.investorId,
      bankCardNo: fundForm.value.bankCardNo
    })
    const fundNo = fundRes.data.accountNo

    await createAssociation({
      securitiesAccountNo: secNo,
      fundAccountNo: fundNo
    })

    ElMessage.success(`联合开户成功！证券账户：${secNo}，资金账户：${fundNo}`)

    currentStep.value = 0
    securitiesForm.value = { investorName: '', idType: 'ID_CARD', idNo: '', phone: '' }
    fundForm.value = { bankCardNo: '', tradePwd: '', tradePwdConfirm: '', withdrawPwd: '', withdrawPwdConfirm: '' }
  } catch (e) {
    ElMessage.error(e.message || '开户失败')
  }
}
</script>

<style scoped>
</style>
