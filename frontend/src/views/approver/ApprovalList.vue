<!-- src/views/approver/ApprovalList.vue -->
<template>
  <div>
    <PageHeader title="审批列表" />

    <el-card style="margin-top: 24px; max-width: 1200px; background: var(--color-white);">
      <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 20px;">
        <button class="btn-primary" @click="handleSearch">查询</button>
        <button class="btn-secondary" @click="resetSearch">重置</button>
      </div>

      <el-table
        v-loading="loading"
        :data="approvalList"
        :empty-text="emptyText"
        stripe
        style="width: 100%;"
      >
        <el-table-column prop="applyId" label="申请编号" width="140" />
        <el-table-column prop="investorId" label="投资者ID" width="100" />
        <el-table-column prop="applicantName" label="申请人" width="120" />
        <el-table-column prop="idNo" label="证件号码" width="190" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column label="处理状态" width="120">
          <template #default="{ row }">
            <el-tag :type="PROCESS_STATUS_TAG[row.applyStatus] || 'info'">
              {{ PROCESS_STATUS_LABEL[row.applyStatus] || row.applyStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="业务状态" width="120">
          <template #default="{ row }">
            <el-tag type="info">
              {{ APP_STATUS_LABEL[row.appStatus] || row.appStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applyTime" label="申请时间" />
        <el-table-column label="操作" fixed="right" width="160">
          <template #default="{ row }">
            <el-button
              link
              :disabled="row.applyStatus !== 'PENDING'"
              @click="handleApprove(row)"
              style="color: var(--color-black);"
            >
              审批
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 审批对话框 -->
    <el-dialog v-model="dialogVisible" title="审批操作" width="400px">
      <el-form ref="approveFormRef" :model="approveForm" :rules="approveRules" label-width="80px">
        <el-form-item label="审批意见">
          <el-input v-model="approveForm.comment" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="银行卡号" prop="bankCardNo">
          <el-input v-model="approveForm.bankCardNo" placeholder="审批通过时必填" />
        </el-form-item>
        <el-form-item label="交易密码" prop="tradePassword">
          <el-input v-model="approveForm.tradePassword" type="password" show-password placeholder="审批通过时必填" />
        </el-form-item>
        <el-form-item label="取款密码" prop="withdrawPassword">
          <el-input v-model="approveForm.withdrawPassword" type="password" show-password placeholder="审批通过时必填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; justify-content: center; gap: 12px;">
          <button class="btn-secondary" @click="dialogVisible = false">取消</button>
          <button class="btn-primary" @click="submitApprove('APPROVED')">通过</button>
          <button class="btn-secondary" @click="submitApprove('REJECTED')">驳回</button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { approveApplication, getApplications, rejectApplication } from '@/utils/request'
import PageHeader from '@/components/PageHeader.vue'

const PROCESS_STATUS_LABEL = {
  PENDING: '待审批',
  APPROVED: '已通过',
  REJECTED: '已驳回',
  COMPLETED: '已完成'
}

const PROCESS_STATUS_TAG = {
  PENDING: 'warning',
  APPROVED: 'success',
  REJECTED: 'danger',
  COMPLETED: 'info'
}

const APP_STATUS_LABEL = {
  SUBMITTED: '已提交',
  CANCELLED: '已撤销'
}

const approvalList = ref([])
const loading = ref(false)
const hasSearched = ref(false)

const dialogVisible = ref(false)
const currentApply = ref(null)
const approveFormRef = ref(null)
const approveForm = ref({
  comment: '',
  bankCardNo: '',
  tradePassword: '',
  withdrawPassword: ''
})
const approveRules = {
  bankCardNo: [
    { required: true, message: '请输入银行卡号', trigger: 'blur' },
    { min: 8, message: '银行卡号至少 8 位', trigger: 'blur' }
  ],
  tradePassword: [
    { required: true, message: '请输入交易密码', trigger: 'blur' },
    { min: 6, message: '交易密码至少 6 位', trigger: 'blur' }
  ],
  withdrawPassword: [
    { required: true, message: '请输入取款密码', trigger: 'blur' },
    { min: 6, message: '取款密码至少 6 位', trigger: 'blur' }
  ]
}

const emptyText = computed(() => {
  return hasSearched.value ? '当前没有可显示的审批申请' : '点击查询加载审批列表'
})

const loadApplications = async () => {
  loading.value = true
  try {
    const res = await getApplications()
    approvalList.value = (res.data || []).sort((a, b) => new Date(b.applyTime) - new Date(a.applyTime))
    hasSearched.value = true
  } catch (error) {
    approvalList.value = []
    ElMessage.error(error.message || '加载审批列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadApplications()
}

const resetSearch = () => {
  approvalList.value = []
  hasSearched.value = false
}

const handleApprove = (row) => {
  currentApply.value = row
  approveForm.value = {
    comment: '',
    bankCardNo: '',
    tradePassword: '',
    withdrawPassword: ''
  }
  dialogVisible.value = true
}

const submitApprove = async (status) => {
  if (!currentApply.value) return

  try {
    if (status === 'APPROVED') {
      await approveFormRef.value?.validate()
      const res = await approveApplication({
        applicationId: currentApply.value.applyId,
        comment: approveForm.value.comment,
        bankCardNo: approveForm.value.bankCardNo.trim(),
        tradePassword: approveForm.value.tradePassword.trim(),
        withdrawPassword: approveForm.value.withdrawPassword.trim()
      })
      ElMessage.success(
        `审批通过，已生成账户：${res.data.securitiesAccountNo || '-'} / ${res.data.fundAccountNo || '-'}`
      )
    } else {
      await rejectApplication({
        applicationId: currentApply.value.applyId,
        comment: approveForm.value.comment || '审批驳回'
      })
      ElMessage.success('审批驳回成功')
    }

    dialogVisible.value = false
    currentApply.value = null
    await loadApplications()
  } catch (error) {
    ElMessage.error(error.message || '审批失败')
  }
}
</script>
