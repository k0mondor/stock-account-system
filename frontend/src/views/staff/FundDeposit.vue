<!-- src/views/staff/FundDeposit.vue -->
<template>
  <div>
    <PageHeader title="存款" />

    <el-card style="margin: 24px auto 0; max-width: 520px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="资金账户号" label-position="top" prop="fundAccountNo" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FND00000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="存款金额" label-position="top" prop="amount" style="margin-bottom: 0;">
            <el-input v-model.number="form.amount" type="number" placeholder="请输入金额" style="width: 100%;" />
          </el-form-item>
        </el-form>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleDeposit">确认存款</button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetForm">重置</button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { deposit } from '@/utils/request'
import PageHeader from '@/components/PageHeader.vue'

const form = ref({
  fundAccountNo: '',
  amount: 0
})

const rules = {
  fundAccountNo: [{ required: true, message: '请输入资金账户号', trigger: 'blur' }],
  amount: [
    { required: true, message: '请输入存款金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ]
}

const formRef = ref(null)

const handleDeposit = async () => {
  await formRef.value.validate()
  try {
    const res = await deposit({
      fundAccountNo: form.value.fundAccountNo,
      amount: form.value.amount
    })
    ElMessage.success(`存款成功！当前可用资金：¥${res.data.availableBalance.toFixed(2)}`)
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || '存款失败')
  }
}

const resetForm = () => {
  form.value = { fundAccountNo: '', amount: 0 }
  formRef.value?.resetFields()
}
</script>

<style scoped>
</style>
