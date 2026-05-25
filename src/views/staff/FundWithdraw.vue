<!-- src/views/staff/FundWithdraw.vue -->
<template>
  <div>
    <PageHeader title="取款" />

    <el-card style="margin: 24px auto 0; max-width: 520px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="资金账户号" label-position="top" prop="fundAccountNo" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FND00000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="取款密码" label-position="top" prop="password" style="margin-bottom: 0;">
            <el-input v-model="form.password" type="password" placeholder="请输入取款密码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="取款金额" label-position="top" prop="amount" style="margin-bottom: 0;">
            <el-input v-model.number="form.amount" type="number" placeholder="请输入金额" style="width: 100%;" />
          </el-form-item>
        </el-form>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleWithdraw">确认取款</button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetForm">重置</button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { withdraw } from '@/utils/request'
import PageHeader from '@/components/PageHeader.vue'

const form = ref({
  fundAccountNo: '',
  password: '',
  amount: 0
})

const rules = {
  fundAccountNo: [{ required: true, message: '请输入资金账户号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入取款密码', trigger: 'blur' }],
  amount: [
    { required: true, message: '请输入取款金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ]
}

const formRef = ref(null)

const handleWithdraw = async () => {
  await formRef.value.validate()
  try {
    const res = await withdraw({
      fundAccountNo: form.value.fundAccountNo,
      password: form.value.password,
      amount: form.value.amount
    })
    ElMessage.success(`取款成功！当前余额：¥${res.data.balance.toFixed(2)}`)
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || '取款失败')
  }
}

const resetForm = () => {
  form.value = { fundAccountNo: '', password: '', amount: 0 }
  formRef.value?.resetFields()
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