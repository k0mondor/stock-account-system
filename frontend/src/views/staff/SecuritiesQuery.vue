<template>
  <div>
    <PageHeader title="证券账户查询" />

    <PagePanel>
      <PageFormBlock>
        <el-form class="page-form-stack" @submit.prevent>
          <el-form-item label="账户号" label-position="top" style="margin-bottom: 0;">
            <el-input v-model="searchNo" placeholder="SEC000001" style="width: 100%;" />
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
        <PageActionRow primary-text="查询" secondary-text="重置" @primary="handleSearch" @secondary="resetSearch" />
      </PageFormBlock>

      <el-table
        :data="tableData"
        :empty-text="emptyText"
        stripe
        style="width: 100%; margin-top: 32px;"
      >
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
            <el-button
              v-if="row?.securitiesAccountNo"
              link
              @click="viewDetail(row)"
              style="color: var(--color-black);"
            >
              详情
            </el-button>
            <span v-else style="color: var(--color-gray-400);">--</span>
          </template>
        </el-table-column>
      </el-table>

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
    </PagePanel>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSecuritiesAccounts } from '@/utils/request'
import { AccountStatusLabel, IdTypeLabel } from '@/constants/enums'
import AccountStatusTag from '@/components/AccountStatusTag.vue'
import PageActionRow from '@/components/PageActionRow.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PagePanel from '@/components/PagePanel.vue'

const searchNo = ref('')
const searchStatus = ref('')
const tableData = ref([])
const detailVisible = ref(false)
const currentAccount = ref(null)
const hasSearched = ref(false)

const emptyText = computed(() => {
  return hasSearched.value ? '未查询到符合条件的证券账户' : '请输入条件后点击查询'
})

function normalizeTableData(data) {
  const list = Array.isArray(data) ? data : data ? [data] : []
  return list.filter(item => item && item.securitiesAccountNo)
}

const fetchData = async (params = {}) => {
  try {
    const res = await getSecuritiesAccounts(params)
    hasSearched.value = true
    tableData.value = normalizeTableData(res.data)
    if (!tableData.value.length) {
      currentAccount.value = null
      detailVisible.value = false
      ElMessage.info('未查询到符合条件的证券账户')
    }
  } catch (e) {
    tableData.value = []
    currentAccount.value = null
    detailVisible.value = false
    ElMessage.error(e.message || '查询失败')
  }
}

// 查询时支持单条件或双条件，若同时填写则必须同时满足（AND）
const handleSearch = () => {
  searchNo.value = searchNo.value.trim()
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
  tableData.value = []
  currentAccount.value = null
  detailVisible.value = false
  hasSearched.value = false
}

const viewDetail = (row) => {
  if (!row?.securitiesAccountNo) {
    ElMessage.warning('当前记录缺少账户信息，无法查看详情')
    return
  }
  currentAccount.value = row
  detailVisible.value = true
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
