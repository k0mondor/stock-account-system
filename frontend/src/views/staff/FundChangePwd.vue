<!-- src/views/staff/FundChangePwd.vue -->
<template>
  <div>
    <PageHeader title="修改密码" show-back />

    <el-card style="margin: 24px auto 0; max-width: 520px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="资金账户号" label-position="top" prop="fundAccountNo" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FUND000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="密码类型" label-position="top" prop="pwdType" style="margin-bottom: 0;">
            <el-select v-model="form.pwdType" placeholder="请选择密码类型" style="width: 100%;">
              <el-option label="交易密码" value="trade" />
              <el-option label="取款密码" value="withdraw" />
            </el-select>
          </el-form-item>
          <el-form-item label="原密码" label-position="top" prop="originalPassword" style="margin-bottom: 0;">
            <el-input v-model="form.originalPassword" type="password" placeholder="请输入原密码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="新密码" label-position="top" prop="newPassword" style="margin-bottom: 0;">
            <el-input v-model="form.newPassword" type="password" placeholder="请输入新密码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="确认新密码" label-position="top" prop="confirmPassword" style="margin-bottom: 0;">
            <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" style="width: 100%;" />
          </el-form-item>
        </el-form>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleSubmit">确认修改</button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetForm">重置</button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { changeFundPassword } from '@/utils/request'
import PageHeader from '@/components/PageHeader.vue'

const form = ref({
  fundAccountNo: '',
  pwdType: '',
  originalPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.value.newPassword) {
    callback(new Error('两次新密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  fundAccountNo: [{ required: true, message: '请输入资金账户号', trigger: 'blur' }],
  pwdType: [{ required: true, message: '请选择密码类型', trigger: 'change' }],
  originalPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const formRef = ref(null)

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    await changeFundPassword({
      fundAccountNo: form.value.fundAccountNo,
      pwdType: form.value.pwdType,
      originalPassword: form.value.originalPassword,
      newPassword: form.value.newPassword,
      confirmPassword: form.value.confirmPassword
    })
    const pwdLabel = form.value.pwdType === 'trade' ? '交易密码' : '取款密码'
    ElMessage.success(`${pwdLabel}修改成功`)
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || '密码修改失败')
  }
}

const resetForm = () => {
  form.value = {
    fundAccountNo: '',
    pwdType: '',
    originalPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  formRef.value?.resetFields()
}
</script>

<style scoped>
</style>
