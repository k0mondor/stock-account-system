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
          <el-sub-menu index="securities">
            <template #title><BiText :text="UiText.securities" /></template>
            <el-menu-item index="/staff/securities/query"><BiText :text="UiText.queryAccount" /></el-menu-item>
            <el-menu-item index="/staff/securities/open"><BiText :text="UiText.openAccount" /></el-menu-item>
            <el-menu-item index="/staff/securities/lost-reissue"><BiText :text="UiText.lost" /></el-menu-item>
            <el-menu-item index="/staff/securities/cancel"><BiText :text="UiText.cancel" /></el-menu-item>
          </el-sub-menu>
           <el-sub-menu index="fund">
             <template #title><BiText :text="UiText.fund" /></template>
             <el-menu-item index="/staff/fund/query"><BiText :text="UiText.queryAccount" /></el-menu-item>
             <el-menu-item index="/staff/fund/transfer"><BiText :text="UiText.depositWithdraw" /></el-menu-item>
             <el-menu-item index="/staff/fund/lost-reissue"><BiText :text="UiText.lost" /></el-menu-item>
             <el-menu-item index="/staff/fund/cancel"><BiText :text="UiText.cancel" /></el-menu-item>
             <el-menu-item index="/staff/fund/change-pwd"><BiText :text="UiText.changePwd" /></el-menu-item>
           </el-sub-menu>
          <el-menu-item index="/staff/joint/open"><BiText :text="UiText.jointOpen" /></el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header style="border-bottom: 1px solid var(--color-gray-200); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; position: sticky; top: 0; z-index: 1001;">
          <div style="display: flex; align-items: center; gap: 24px; height: 100%;">
            <span style="color: var(--color-gray-500);"><BiText :text="UiText.staffArea" /></span>

            <div class="apple-nav-trigger" @click.stop="toggleMega">
              <span><BiText :text="UiText.quickNav" /> ▾</span>
              
              <div class="apple-mega-dropdown" :class="{ 'is-active': showMega }">
                <div class="mega-content-grid" @click.stop>
                  
                   <div class="mega-column">
                     <span class="column-title"><BiText text="证券账户/SECURITIES" /></span>
                     <router-link to="/staff/securities/query" class="mega-link"><BiText text="查询证券账户/QUERY" /> <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/securities/open" class="mega-link"><BiText text="开设证券账户/OPEN" /> <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/securities/lost-reissue" class="mega-link"><BiText text="账户挂失/LOSS" /> <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/securities/cancel" class="mega-link"><BiText text="账户注销/CLOSE" /> <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/joint/open" class="mega-link"><BiText text="联合开户/JOINT OPENING" /> <span class="arrow">&rarr;</span></router-link>
                   </div>
                  
                  <div class="mega-column">
                    <span class="column-title"><BiText text="资金账户/FUND" /></span>
                    <router-link to="/staff/fund/query" class="mega-link"><BiText text="查询资金账户/QUERY" /> <span class="arrow">&rarr;</span></router-link>
                    <router-link to="/staff/fund/transfer" class="mega-link"><BiText text="存取款办理/DEPOSIT & WITHDRAW" /> <span class="arrow">&rarr;</span></router-link>
                    <router-link to="/staff/fund/lost-reissue" class="mega-link"><BiText text="挂失补开/LOSS & REISSUE" /> <span class="arrow">&rarr;</span></router-link>
                    <router-link to="/staff/fund/cancel" class="mega-link"><BiText text="账户注销/CLOSE" /> <span class="arrow">&rarr;</span></router-link>
                  </div>
                  
                  <div class="mega-column">
                    <span class="column-title"><BiText text="系统状态/SYSTEM META" /></span>
                    <div style="font-size: 13px; color: #6B7280; line-height: 1.8;">
                      <p>节点状态: <span style="color: #111111; font-weight: 600;">ONLINE</span></p>
                      <p>环境架构: Vue 3 + Vite</p>
                      <p style="margin-top: 12px; font-size: 11px; color: #9CA3AF;">© 2026 STOCK ACCOUNT SYSTEM</p>
                    </div>
                  </div>
                  
                </div>
              </div>
              
              <div class="apple-blur-overlay" :class="{ 'is-active': showMega }" @click.stop="closeMega"></div>
            </div>
          </div>
          
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-button link @click="helpVisible = true" :aria-label="UiText.help">
              <el-icon><QuestionFilled /></el-icon>
            </el-button>
            <el-button class="btn-secondary" @click="logout"><BiText :text="UiText.logout" /></el-button>
          </div>
        </el-header>
        <el-main style="padding: 40px 24px;">
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
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { QuestionFilled } from '@element-plus/icons-vue'
import HelpDrawer from '@/components/HelpDrawer.vue'
import { UiText } from '@/constants/i18n'
import BiText from '@/components/BiText.vue'

const router = useRouter()
const showMega = ref(false)
const helpVisible = ref(false)

const toggleMega = () => {
  showMega.value = !showMega.value
}

const closeMega = () => {
  showMega.value = false
}

const logout = () => {
  router.push('/login')
}

const handleGlobalClick = () => closeMega()

const handleGlobalScroll = () => {
  if (showMega.value) closeMega()
}

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

onMounted(() => {
  document.addEventListener('click', handleGlobalClick)
  window.addEventListener('scroll', handleGlobalScroll, true)
  window.addEventListener('keydown', handleGlobalKeydown, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleGlobalClick)
  window.removeEventListener('scroll', handleGlobalScroll, true)
  window.removeEventListener('keydown', handleGlobalKeydown, true)
})
</script>

<style scoped>
.logo {
  padding: 24px;
  font-weight: 600;
  font-size: 18px;
  border-bottom: 1px solid var(--color-gray-200);
  color: var(--color-black);
}
</style>
