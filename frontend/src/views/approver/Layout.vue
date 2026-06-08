<!-- src/views/approver/Layout.vue -->
<template>
  <div>
    <el-container style="min-height: 100vh;">
      <el-aside width="220px" style="background: #f5f5f5; border-right: 1px solid var(--color-gray-200);">
        <div class="logo"><BiText text="账户业务子系统/ACCOUNT" /></div>
        <el-menu
          :default-active="$route.path"
          router
          style="border-right: none;"
        >
          <el-menu-item index="/approver/approval"><BiText :text="UiText.approvalList" /></el-menu-item>
          <el-menu-item index="/approver/log"><BiText :text="UiText.operationLog" /></el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header style="border-bottom: 1px solid #e5e4e7; display: flex; align-items: center; justify-content: space-between; padding: 0 24px;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="color: var(--color-gray-500);"><BiText :text="UiText.approverArea" /></span>
          <span v-if="currentApproverLabel" style="font-size: 13px; color: var(--color-gray-500);">
            当前审批员：{{ currentApproverLabel }}
          </span>
        </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-button link @click="helpVisible = true" :aria-label="UiText.help">
              <el-icon><QuestionFilled /></el-icon>
            </el-button>
            <el-button class="btn-secondary" @click="logout"><BiText :text="UiText.logout" /></el-button>
          </div>
        </el-header>
        <el-main style="background: #f8f9fa; padding: 40px 24px;">
          <div style="max-width: 1100px; margin: 0 auto;">
            <router-view />
          </div>
        </el-main>
      </el-container>
    </el-container>

    <HelpDrawer v-model="helpVisible" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import HelpDrawer from '@/components/HelpDrawer.vue'
import { UiText } from '@/constants/i18n'
import BiText from '@/components/BiText.vue'
import { clearCurrentStaffSession, readCurrentStaffSession } from '@/utils/request/core'

const router = useRouter()
const currentStaff = ref(readCurrentStaffSession())
const currentApproverLabel = computed(() => {
  const staff = currentStaff.value
  if (!staff?.staff_id) return ''
  return staff.staff_name ? `${staff.staff_name} (${staff.staff_id})` : staff.staff_id
})
const logout = () => {
  clearCurrentStaffSession()
  router.push('/login')
}

const helpVisible = ref(false)

const handleGlobalKeydown = (e) => {
  if (e.key === '?') {
    e.preventDefault()
    helpVisible.value = !helpVisible.value
    return
  }
  if (e.key === 'Escape' && helpVisible.value) {
    helpVisible.value = false
  }
}

onMounted(() => window.addEventListener('keydown', handleGlobalKeydown, true))
onBeforeUnmount(() => window.removeEventListener('keydown', handleGlobalKeydown, true))
</script>

<style scoped>
.logo { padding: 24px; font-weight: 600; }
</style>
