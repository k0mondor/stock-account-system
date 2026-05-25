<!-- src/views/staff/FundTransfer.vue -->
<template>
  <div>
    <PageHeader title="存取款业务" />

    <el-card style="margin: 24px auto 0; max-width: 520px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <!-- 存取款切换标签 -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange" style="margin-bottom: 24px;">
          <el-tab-pane label="存款" name="deposit"></el-tab-pane>
          <el-tab-pane label="取款" name="withdraw"></el-tab-pane>
        </el-tabs>

        <el-form ref="formRef" :model="form" :rules="currentRules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="资金账户号" label-position="top" prop="fundAccountNo" style="margin-bottom: 0;">
            <el-input v-model="form.fundAccountNo" placeholder="FND00000001" style="width: 100%;" />
          </el-form-item>
          
          <!-- 取款密码字段 - 仅在取款模式下显示 -->
          <el-form-item 
            v-if="activeTab === 'withdraw'" 
            label="取款密码" 
            label-position="top" 
            prop="password" 
            style="margin-bottom: 0;"
          >
            <el-input v-model="form.password" type="password" placeholder="请输入取款密码" style="width: 100%;" />
          </el-form-item>
          
          <el-form-item label="操作金额" label-position="top" prop="amount" style="margin-bottom: 0;">
            <el-input v-model.number="form.amount" type="number" placeholder="请输入金额" style="width: 100%;" />
          </el-form-item>
        </el-form>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleSubmit">
            {{ activeTab === 'deposit' ? '确认存款' : '确认取款' }}
          </button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetForm">重置</button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { deposit, withdraw } from '@/utils/request'
import PageHeader from '@/components/PageHeader.vue'

const activeTab = ref('deposit')

const form = ref({
  fundAccountNo: '',
  password: '', // 仅取款时使用
  amount: 0
})

// 存款验证规则
const depositRules = {
  fundAccountNo: [{ required: true, message: '请输入资金账户号', trigger: 'blur' }],
  amount: [
    { required: true, message: '请输入存款金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ]
}

// 取款验证规则（包含密码验证）
const withdrawRules = {
  fundAccountNo: [{ required: true, message: '请输入资金账户号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入取款密码', trigger: 'blur' }],
  amount: [
    { required: true, message: '请输入取款金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ]
}

// 根据当前标签页动态返回验证规则
const currentRules = computed(() => {
  return activeTab.value === 'deposit' ? depositRules : withdrawRules
})

const formRef = ref(null)

const handleTabChange = () => {
  resetForm()
}

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    if (activeTab.value === 'deposit') {
      const res = await deposit({
        fundAccountNo: form.value.fundAccountNo,
        amount: form.value.amount
      })
      ElMessage.success(`存款成功！当前余额：¥${res.data.balance.toFixed(2)}`)
    } else {
      const res = await withdraw({
        fundAccountNo: form.value.fundAccountNo,
        password: form.value.password,
        amount: form.value.amount
      })
      ElMessage.success(`取款成功！当前余额：¥${res.data.balance.toFixed(2)}`)
    }
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || `${activeTab.value === 'deposit' ? '存款' : '取款'}失败`)
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