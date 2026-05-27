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
          
          <!-- 已移除直接显示的密码输入框，改为弹窗输入 -->
          
          <el-form-item label="操作金额" label-position="top" prop="amount" style="margin-bottom: 0;">
            <el-input v-model.number="form.amount" type="number" placeholder="请输入金额" style="width: 100%;" />
          </el-form-item>
        </el-form>

        <!-- 密码弹窗 -->
        <el-dialog v-model="passwordDialogVisible" title="请指引客户在密码键盘上输入密码" width="400px">
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
            <el-form-item label="密码" prop="password">
              <el-input v-model="passwordForm.password" type="password" show-password placeholder="请输入密码" style="width: 100%;" />
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer" style="display: flex; justify-content: flex-end; gap: 12px;">
              <el-button @click="handlePasswordCancel">取消</el-button>
              <el-button type="primary" @click="handlePasswordConfirm">确认</el-button>
            </span>
          </template>
        </el-dialog>

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

// 表单数据（不包含密码）
const form = ref({
  fundAccountNo: '',
  amount: 0
})

// 密码弹窗相关状态
const passwordDialogVisible = ref(false)
// 使用对象形式的表单模型以配合 el-form
const passwordForm = ref({ password: '' })
const passwordFormRef = ref(null)
const passwordRules = {
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

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
  // 先校验表单（不含密码）
  await formRef.value.validate()
  // 打开密码弹窗，等待用户输入密码后再提交
  passwordDialogVisible.value = true
}

// 在弹窗确认后执行实际的存取款请求
const handlePasswordConfirm = async () => {
  // 校验密码输入
  await passwordFormRef.value.validate()
  try {
    if (activeTab.value === 'deposit') {
      const res = await deposit({
        fundAccountNo: form.value.fundAccountNo,
        amount: form.value.amount,
        password: passwordForm.value.password
      })
      ElMessage.success(`存款成功！当前可用资金：¥${res.data.availableBalance.toFixed(2)}`)
    } else {
      const res = await withdraw({
        fundAccountNo: form.value.fundAccountNo,
        amount: form.value.amount,
        password: passwordForm.value.password
      })
      ElMessage.success(`取款成功！当前可用资金：¥${res.data.availableBalance.toFixed(2)}`)
    }
    // 成功后关闭弹窗并重置表单
    resetForm()
    passwordDialogVisible.value = false
    passwordForm.value.password = ''
  } catch (e) {
    ElMessage.error(e.message || `${activeTab.value === 'deposit' ? '存款' : '取款'}失败`)
  }
}

const handlePasswordCancel = () => {
  passwordDialogVisible.value = false
  passwordForm.value.password = ''
}

const resetForm = () => {
  form.value = { fundAccountNo: '', amount: 0 }
  formRef.value?.resetFields()
  // 同时清空密码并关闭弹窗
  passwordForm.value.password = ''
  passwordDialogVisible.value = false
}
</script>

<style scoped>
:deep(input::-webkit-outer-spin-button),
:deep(input::-webkit-inner-spin-button) {
  -webkit-appearance: none !important;
  margin: 0;
}
</style>
