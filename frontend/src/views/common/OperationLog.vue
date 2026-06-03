<!-- src/views/common/OperationLog.vue -->
<template>
  <div>
    <PageHeader title="业务办理历史" />

    <el-card style="margin: 24px auto 0; max-width: 1200px; background: var(--color-white);">
      <!-- 筛选表单 -->
      <el-form
        @submit.prevent
        style="display: flex; justify-content: center; align-items: center; gap: 16px; flex-wrap: wrap;"
      >
        <el-form-item label="账户号" style="margin-bottom: 0;">
          <el-input v-model="searchTargetId" placeholder="账户号/申请号" style="width: 180px;" clearable />
        </el-form-item>

        <el-form-item label="操作类型" style="margin-bottom: 0;">
          <el-select v-model="searchType" placeholder="全部" clearable style="width: 150px;">
            <el-option
              v-for="(label, key) in OperationTypeLabel"
              :key="key"
              :label="label"
              :value="key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="操作人员" style="margin-bottom: 0;">
          <el-input v-model="searchOperatorId" placeholder="操作人员ID" style="width: 150px;" clearable />
        </el-form-item>

        <el-form-item label="操作结果" style="margin-bottom: 0;">
          <el-select v-model="searchResult" placeholder="全部" clearable style="width: 120px;">
            <el-option label="成功" value="SUCCESS" />
            <el-option label="失败" value="FAILED" />
          </el-select>
        </el-form-item>

        <el-form-item style="margin-bottom: 0; display: inline-flex; align-items: center;">
          <button class="btn-primary" style="height: 32px; padding: 0 24px; line-height: 1;" @click="handleSearch">查询</button>
        </el-form-item>

        <el-form-item style="margin-bottom: 0; display: inline-flex; align-items: center;">
          <button class="btn-secondary" style="height: 32px; padding: 0 16px; line-height: 1;" @click="handleReset">重置</button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="logList" stripe style="width: 100%; margin-top: 24px;" v-loading="loading">
        <el-table-column prop="logId" label="日志编号" width="150" />
        <el-table-column prop="operatorId" label="操作人员" width="120" />
        <el-table-column prop="operatorName" label="操作人姓名" width="120" />
        <el-table-column prop="operationType" label="操作类型" width="130">
          <template #default="{ row }">
            <el-tag size="small" :type="getOperationTagType(row.operationType)">
              {{ OperationTypeLabel[row.operationType] || row.operationType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="targetType" label="目标类型" width="110">
          <template #default="{ row }">
            {{ TargetTypeLabel[row.targetType] || row.targetType }}
          </template>
        </el-table-column>
        <el-table-column prop="targetId" label="目标ID" width="150" />
        <el-table-column prop="operationDetail" label="操作详情" min-width="200">
          <template #default="{ row }">
            <span v-if="row.operationDetail">{{ row.operationDetail }}</span>
            <span v-else style="color: var(--color-gray-400);">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="operationResult" label="结果" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.operationResult === 'SUCCESS' ? 'success' : 'danger'">
              {{ row.operationResult === 'SUCCESS' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failReason" label="失败原因" width="180">
          <template #default="{ row }">
            <span v-if="row.failReason" style="color: var(--el-color-danger);">{{ row.failReason }}</span>
            <span v-else style="color: var(--color-gray-400);">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="operateTime" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.operateTime) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="!loading && logList.length === 0" style="text-align: center; padding: 48px 0; color: var(--color-gray-400);">
        <p>暂无操作日志记录</p>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" style="display: flex; justify-content: center; margin-top: 24px;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOperationLogs } from '@/utils/request'
import { OperationTypeLabel, TargetTypeLabel } from '@/constants/enums'
import PageHeader from '@/components/PageHeader.vue'

// 搜索条件
const searchTargetId = ref('')
const searchType = ref('')
const searchOperatorId = ref('')
const searchResult = ref('')

// 列表数据
const logList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 搜索
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value
    }
    if (searchTargetId.value) params.targetId = searchTargetId.value
    if (searchType.value) params.operationType = searchType.value
    if (searchOperatorId.value) params.operatorId = searchOperatorId.value
    if (searchResult.value) params.operationResult = searchResult.value

    const res = await getOperationLogs(params)
    logList.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('查询操作日志失败')
    logList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  searchTargetId.value = ''
  searchType.value = ''
  searchOperatorId.value = ''
  searchResult.value = ''
  currentPage.value = 1
  handleSearch()
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) return timeStr
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return timeStr
  }
}

// 根据操作类型返回标签样式
const getOperationTagType = (type) => {
  const dangerTypes = ['CANCEL', 'LOST']
  const warningTypes = ['STATUS_CHANGE', 'WITHDRAW']
  const successTypes = ['OPEN_ACCOUNT', 'DEPOSIT', 'APPROVE', 'LINK']
  if (dangerTypes.includes(type)) return 'danger'
  if (warningTypes.includes(type)) return 'warning'
  if (successTypes.includes(type)) return 'success'
  return 'info'
}

// 初始加载
handleSearch()
</script>

<style scoped>
</style>
