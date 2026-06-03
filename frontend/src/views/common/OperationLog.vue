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
      <el-input v-model="searchNo" placeholder="SEC00000001" style="width: 180px;" />
    </el-form-item>

    <el-form-item label="操作类型" style="margin-bottom: 0;">
      <el-select v-model="searchType" placeholder="全部" clearable style="width: 140px;">
        <el-option label="开户" value="OPEN_ACCOUNT" />
        <el-option label="存款" value="DEPOSIT" />
      </el-select>
    </el-form-item>

    <el-form-item style="margin-bottom: 0; display: inline-flex; align-items: center;">
      <button class="btn-primary" style="height: 32px; padding: 0 24px; line-height: 1;" @click="handleSearch">查询</button>
    </el-form-item>
  </el-form>

      <el-table :data="logList" stripe style="width: 100%; margin-top: 16px;">
        <el-table-column prop="logId" label="日志编号" width="140" />
        <el-table-column prop="operator" label="操作人员" width="120" />
        <el-table-column prop="operationType" label="操作类型" width="140" />
        <el-table-column prop="operateTime" label="操作时间" />
        <el-table-column prop="operateResult" label="结果" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'

const searchNo = ref('')
const searchType = ref('')
const logList = ref([
  {
    logId: 'LOG00000001',
    operator: 'staff_001',
    operationType: 'OPEN_ACCOUNT',
    operateTime: '2026-05-23T10:00:00',
    operateResult: 'SUCCESS'
  },
  {
    logId: 'LOG00000002',
    operator: 'staff_001',
    operationType: 'DEPOSIT',
    operateTime: '2026-05-23T11:30:00',
    operateResult: 'SUCCESS'
  }
])

const handleSearch = () => {
  // mock 筛选
  console.log('搜索', searchNo.value, searchType.value)
}
</script>
