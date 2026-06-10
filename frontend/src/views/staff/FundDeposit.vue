<!-- src/views/staff/FundDeposit.vue -->
<template>
  <div>
    <PageHeader title="存款" />

    <PagePanel width="narrow">
      <PageFormBlock>
        <el-form ref="formRef" :model="form" :rules="rules" class="page-form-stack" @submit.prevent>
          <el-form-item label="资金账户号" label-position="top" prop="fundAccountNo" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FUND000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="存款金额" label-position="top" prop="amount" style="margin-bottom: 0;">
            <el-input v-model="form.amount" inputmode="decimal" placeholder="请输入金额，最多16位整数和2位小数" style="width: 100%;" />
          </el-form-item>
        </el-form>
        <PageActionRow primary-text="确认存款" secondary-text="重置" @primary="handleDeposit" @secondary="resetForm" />
      </PageFormBlock>
    </PagePanel>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { deposit } from '@/utils/request'
import PageActionRow from '@/components/PageActionRow.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PagePanel from '@/components/PagePanel.vue'

const form = ref({
  fundAccountNo: '',
  amount: ''
})

const amountPattern = /^\d{1,16}(\.\d{1,2})?$/
const validateAmount = (_rule, value, callback) => {
  const normalized = String(value ?? '').trim()
  if (!normalized) {
    callback(new Error('请输入存款金额'))
    return
  }
  if (!amountPattern.test(normalized)) {
    callback(new Error('金额最多16位整数，且最多保留2位小数'))
    return
  }
  if (Number(normalized) <= 0) {
    callback(new Error('金额必须大于0'))
    return
  }
  callback()
}

const rules = {
  fundAccountNo: [{ required: true, message: '请输入资金账户号', trigger: 'blur' }],
  amount: [
    { validator: validateAmount, trigger: 'blur' }
  ]
}

const formRef = ref(null)

const handleDeposit = async () => {
  await formRef.value.validate()
  try {
    const res = await deposit({
      fundAccountNo: form.value.fundAccountNo,
      amount: form.value.amount.trim()
    })
    ElMessage.success(`存款成功！当前可用资金：¥${res.data.availableBalance.toFixed(2)}`)
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || '存款失败')
  }
}

const resetForm = () => {
  form.value = { fundAccountNo: '', amount: '' }
  formRef.value?.resetFields()
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
