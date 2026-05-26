<template>
  <div>
    <PageHeader title="证券账户查询" />

    <el-card style="margin-top: 24px; max-width: 1100px; background: var(--color-white);">
      <div style="max-width: 400px; margin: 0 auto;">
        <el-form @submit.prevent style="display: flex; flex-direction: column; gap: 20px;">
          <el-form-item label="账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="searchNo" placeholder="SEC00000001" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="状态" label-position="top" style="margin-bottom: 0;">
            <el-select v-model="searchStatus" placeholder="全部" clearable style="width: 100%;">
              <el-option
                v-for="(label, key) in AccountStatusLabel"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
        </el-form>
        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <button class="btn-primary" @click="handleSearch">查询</button>
          <button class="btn-secondary" style="margin-left: 12px;" @click="resetSearch">重置</button>
        </div>
      </div>

      <el-table :data="tableData" stripe style="width: 100%; margin-top: 32px;">
        <el-table-column prop="securitiesAccountNo" label="证券账户号" width="160" />
        <el-table-column prop="investorName" label="投资者姓名" width="120" />
        <el-table-column prop="idNo" label="证件号码" width="180" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <AccountStatusTag :status="row.accountStatus" />
          </template>
        </el-table-column>
        <el-table-column prop="openTime" label="开户时间" width="180" />
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button link @click="viewDetail(row)" style="color: var(--color-black);">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="账户详情" width="500px">
      <div v-if="currentAccount" style="line-height: 2;">
        <p><strong>账户号：</strong>{{ currentAccount.securitiesAccountNo }}</p>
        <p><strong>投资者：</strong>{{ currentAccount.investorName }} (ID: {{ currentAccount.investorId }})</p>
        <p><strong>证件：</strong>{{ IdTypeLabel[currentAccount.idType] }} {{ currentAccount.idNo }}</p>
        <p><strong>电话：</strong>{{ currentAccount.phone }}</p>
        <p><strong>状态：</strong><AccountStatusTag :status="currentAccount.accountStatus" /></p>
        <p><strong>开户时间：</strong>{{ currentAccount.openTime }}</p>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSecuritiesAccounts } from '@/utils/request'
import { AccountStatusLabel, IdTypeLabel } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageHeader from '@/components/PageHeader.vue'

const searchNo = ref('')
const searchStatus = ref('')
const tableData = ref([])
const detailVisible = ref(false)
const currentAccount = ref(null)

const fetchData = async (params = {}) => {
  try {
    const res = await getSecuritiesAccounts(params)
    tableData.value = res.data || []
  } catch (e) {
    ElMessage.error('查询失败')
  }
}

// 查询时支持单条件或双条件，若同时填写则必须同时满足（AND）
const handleSearch = () => {
  // 若两个条件均未填写，则提示错误
  if (!searchNo.value && !searchStatus.value) {
    ElMessage.error('请至少填写账户号或状态后再查询')
    return
  }
  const params = {}
  if (searchNo.value) params.securitiesAccountNo = searchNo.value
  if (searchStatus.value) params.accountStatus = searchStatus.value
  fetchData(params)
}

const resetSearch = () => {
  searchNo.value = ''
  searchStatus.value = ''
  fetchData()
}

const viewDetail = (row) => {
  currentAccount.value = row
  detailVisible.value = true
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.btn-primary, .btn-secondary {
  padding: 10px 28px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 0;
  cursor: pointer;
}
:deep(.el-form-item) {
  margin-bottom: 28px !important;
  position: relative;
}

/* 2. 扒掉红字的绝对定位，改用块级标准流，动态向下推挤后续组件 */
:deep(.el-form-item__error) {
  position: relative !important;
  top: 4px !important; /* 让红字和输入框之间有 4px 的微调距离 */
  left: 0 !important;
  display: block !important;
  line-height: 1.5 !important;
  padding-bottom: 4px !important;
}
</style>