<!-- src/views/common/OperationLog.vue -->
<template>
  <div>
    <PageHeader title="业务办理历史" />

    <el-card style="margin: 24px auto 0; max-width: 1100px; background: var(--color-white);">
      <el-form
        @submit.prevent
        style="display: flex; justify-content: center; align-items: center; gap: 16px; flex-wrap: wrap;"
      >
        <el-form-item label="账户号" style="margin-bottom: 0;">
          <el-input v-model="searchNo" placeholder="SEC000001 / FUND000001" style="width: 200px;" />
        </el-form-item>

        <el-form-item label="操作类型" style="margin-bottom: 0;">
          <el-select v-model="searchType" placeholder="全部" clearable style="width: 160px;">
            <el-option label="开户" value="OPEN_ACCOUNT" />
            <el-option label="审批" value="APPROVE" />
            <el-option label="存款" value="DEPOSIT" />
            <el-option label="取款" value="WITHDRAW" />
            <el-option label="挂失" value="LOST" />
            <el-option label="补办" value="REISSUE" />
            <el-option label="注销" value="CANCEL" />
          </el-select>
        </el-form-item>

        <el-form-item style="margin-bottom: 0; display: inline-flex; align-items: center;">
          <button class="btn-primary" style="height: 32px; padding: 0 24px; line-height: 1;" @click="handleSearch">查询</button>
        </el-form-item>
        <el-form-item style="margin-bottom: 0; display: inline-flex; align-items: center;">
          <button class="btn-secondary" style="height: 32px; padding: 0 24px; line-height: 1;" @click="resetSearch">重置</button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="logList"
        :empty-text="emptyText"
        stripe
        style="width: 100%; margin-top: 16px;"
      >
        <el-table-column prop="logId" label="日志编号" width="140" />
        <el-table-column prop="operatorName" label="操作人员" width="120" />
        <el-table-column prop="operationType" label="操作类型" width="140" />
        <el-table-column prop="operateTime" label="操作时间" />
        <el-table-column prop="operationResult" label="结果" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOperationLogs } from '@/utils/request'
import PageHeader from '@/components/PageHeader.vue'

const searchNo = ref('')
const searchType = ref('')
const logList = ref([])
const loading = ref(false)
const hasSearched = ref(false)

const emptyText = computed(() => {
  return hasSearched.value ? '未查询到符合条件的业务日志' : '请输入条件后点击查询'
})

const loadLogs = async () => {
  loading.value = true
  try {
    const res = await getOperationLogs({
      targetId: searchNo.value || undefined,
      operationType: searchType.value || undefined,
      page: 1,
      pageSize: 50
    })
    logList.value = res.data?.items || []
    hasSearched.value = true
  } catch (error) {
    logList.value = []
    ElMessage.error(error.message || '日志查询失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (!searchNo.value && !searchType.value) {
    ElMessage.error('请至少填写账户号或操作类型后再查询')
    return
  }
  loadLogs()
}

const resetSearch = () => {
  searchNo.value = ''
  searchType.value = ''
  logList.value = []
  hasSearched.value = false
}
</script>
