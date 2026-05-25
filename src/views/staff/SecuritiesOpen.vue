<!-- src/views/staff/SecuritiesOpen.vue -->
<template>
  <div>
    <PageHeader title="开设证券账户" />

    <el-card style="margin: 24px auto 0; max-width: 520px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="投资者姓名" label-position="top" prop="investorName" style="margin-bottom: 0;">
            <el-input v-model="form.investorName" placeholder="请输入姓名" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证件类型" label-position="top" prop="idType" style="margin-bottom: 0;">
            <el-select v-model="form.idType" placeholder="请选择" style="width: 100%;">
              <el-option
                v-for="(label, key) in IdTypeLabel"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="证件号码" label-position="top" prop="idNo" style="margin-bottom: 0;">
            <el-input v-model="form.idNo" placeholder="请输入证件号码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="联系电话" label-position="top" prop="phone" style="margin-bottom: 0;">
            <el-input v-model="form.phone" placeholder="请输入手机号" style="width: 100%;" />
          </el-form-item>
        </el-form>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleOpen">确认开户</button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetForm">重置</button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { openSecuritiesAccount } from '@/utils/request'
import { IdTypeLabel } from '@/constants/enums'
import PageHeader from '@/components/PageHeader.vue'

const form = ref({
  investorName: '',
  idType: 'ID_CARD',
  idNo: '',
  phone: ''
})

const rules = {
  investorName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  idType: [{ required: true, message: '请选择证件类型', trigger: 'change' }],
  idNo: [{ required: true, message: '请输入证件号码', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const formRef = ref(null)

const handleOpen = async () => {
  await formRef.value.validate()
  try {
    const res = await openSecuritiesAccount(form.value)
    ElMessage.success(`开户成功！证券账户号：${res.data.accountNo}`)
    resetForm()
  } catch (e) {
    ElMessage.error(e.message || '开户失败')
  }
}

const resetForm = () => {
  form.value = { investorName: '', idType: 'ID_CARD', idNo: '', phone: '' }
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