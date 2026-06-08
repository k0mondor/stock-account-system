<template>
  <div>
    <PageHeader title="证券账户密码重置" show-back />

    <PagePanel width="narrow">
      <PageInfoCard title="办理说明" style="margin-bottom: 24px;">
        <p class="inline-tip">该页面用于柜台工作人员核验客户证件后代理重置证券账户密码，不需要输入原密码。</p>
      </PageInfoCard>

      <PageFormBlock>
        <el-form ref="formRef" :model="form" :rules="rules" class="page-form-stack" @submit.prevent>
          <el-form-item label="工作人员号" label-position="top" prop="staffId" style="margin-bottom: 0;">
            <el-input v-model="form.staffId" placeholder="STAFF000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证券账户号" label-position="top" prop="securitiesAccountNo" style="margin-bottom: 0;">
            <el-input v-model="form.securitiesAccountNo" placeholder="SEC000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="客户证件号码" label-position="top" prop="customerIdNumber" style="margin-bottom: 0;">
            <el-input v-model="form.customerIdNumber" placeholder="请输入客户证件号码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="新密码" label-position="top" prop="newPassword" style="margin-bottom: 0;">
            <el-input v-model="form.newPassword" type="password" placeholder="请输入新密码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="确认新密码" label-position="top" prop="confirmPassword" style="margin-bottom: 0;">
            <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="重置原因" label-position="top" prop="reason" style="margin-bottom: 0;">
            <el-input
              v-model="form.reason"
              type="textarea"
              :rows="3"
              maxlength="256"
              show-word-limit
              placeholder="请输入重置原因，例如客户忘记密码"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
        <PageActionRow primary-text="确认重置" secondary-text="重置" @primary="handleSubmit" @secondary="resetForm" />
      </PageFormBlock>
    </PagePanel>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { resetSecurityPasswordByStaff } from '@/utils/request'
import { DEFAULT_OPERATOR_ID } from '@/utils/request/core'
import PageActionRow from '@/components/PageActionRow.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'

const form = ref({
  staffId: DEFAULT_OPERATOR_ID,
  securitiesAccountNo: '',
  customerIdNumber: '',
  newPassword: '',
  confirmPassword: '',
  reason: ''
})

const validateConfirmPassword = (_rule, value, callback) => {
  if (value !== form.value.newPassword) {
    callback(new Error('两次新密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  staffId: [{ required: true, message: '请输入工作人员号', trigger: 'blur' }],
  securitiesAccountNo: [{ required: true, message: '请输入证券账户号', trigger: 'blur' }],
  customerIdNumber: [{ required: true, message: '请输入客户证件号码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  reason: [{ required: true, message: '请输入重置原因', trigger: 'blur' }]
}

const formRef = ref(null)

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    await resetSecurityPasswordByStaff({
      staffId: form.value.staffId,
      securitiesAccountNo: form.value.securitiesAccountNo,
      customerIdNumber: form.value.customerIdNumber,
      newPassword: form.value.newPassword,
      confirmPassword: form.value.confirmPassword,
      reason: form.value.reason
    })
    ElMessage.success('证券账户密码重置成功')
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || '密码重置失败')
  }
}

const resetForm = () => {
  form.value = {
    staffId: DEFAULT_OPERATOR_ID,
    securitiesAccountNo: '',
    customerIdNumber: '',
    newPassword: '',
    confirmPassword: '',
    reason: ''
  }
  formRef.value?.resetFields()
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
</style>
