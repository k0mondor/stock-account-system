<!-- src/views/approver/ApprovalList.vue -->
<template>
  <div>
    <PageHeader title="审批列表" />

    <el-card style="margin-top: 24px; max-width: 1100px; background: var(--color-white);">
      <el-table :data="approvalList" stripe style="width: 100%;">
        <el-table-column prop="applyId" label="申请编号" width="140" />
        <el-table-column prop="investorId" label="投资者ID" width="100" />
        <el-table-column prop="accountType" label="账户类型" width="120" />
        <el-table-column label="申请状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.applyStatus === 'PENDING_APPROVE' ? 'warning' : ''">
              {{ ApplyStatusLabel[row.applyStatus] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applyTime" label="申请时间" />
        <el-table-column label="操作" fixed="right" width="160">
          <template #default="{ row }">
            <el-button link @click="handleApprove(row)" style="color: var(--color-black);">审批</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 审批对话框 -->
    <el-dialog v-model="dialogVisible" title="审批操作" width="400px">
      <el-form :model="approveForm" label-width="80px">
        <el-form-item label="审批意见">
          <el-input v-model="approveForm.comment" type="textarea" :rows="3" />
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ApplyStatusLabel } from '@/constants/enums'
import PageHeader from '@/components/PageHeader.vue'

const approvalList = ref([
  {
    applyId: 'APP00000001',
    investorId: 10001,
    accountType: 'SECURITIES',
    applyStatus: 'PENDING_APPROVE',
    applyTime: '2026-05-23T10:00:00'
  },
  {
    applyId: 'APP00000002',
    investorId: 10002,
    accountType: 'FUND',
    applyStatus: 'PENDING_APPROVE',
    applyTime: '2026-05-23T11:30:00'
  }
])

const dialogVisible = ref(false)
const currentApply = ref(null)
const approveForm = ref({ comment: '' })

const handleApprove = (row) => {
  currentApply.value = row
  approveForm.value = { comment: '' }
  dialogVisible.value = true
}

const submitApprove = (status) => {
  ElMessage.success(`审批${status === 'APPROVED' ? '通过' : '驳回'}成功`)
  dialogVisible.value = false
  // 实际应更新列表状态
}
</script>