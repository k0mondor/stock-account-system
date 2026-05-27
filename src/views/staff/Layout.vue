<template>
  <div>
    <el-container style="min-height: 100vh;">
      <el-aside width="220px" style="background: #f5f5f5; border-right: 1px solid var(--color-gray-200);">
        <div class="logo">账户业务子系统</div>
        <el-menu
          :default-active="$route.path"
          router
          style="border-right: none;"
        >
          <el-sub-menu index="securities">
            <template #title>证券账户</template>
            <el-menu-item index="/staff/securities/query">查询账户</el-menu-item>
            <el-menu-item index="/staff/securities/open">开设账户</el-menu-item>
            <el-menu-item index="/staff/securities/lost-reissue">挂失</el-menu-item>
            <el-menu-item index="/staff/securities/cancel">注销</el-menu-item>
          </el-sub-menu>
           <el-sub-menu index="fund">
             <template #title>资金账户</template>
             <el-menu-item index="/staff/fund/query">查询账户</el-menu-item>
             <el-menu-item index="/staff/fund/transfer">存取款业务</el-menu-item>
             <el-menu-item index="/staff/fund/lost-reissue">挂失</el-menu-item>
             <el-menu-item index="/staff/fund/cancel">注销</el-menu-item>
             <el-menu-item index="/staff/fund/change-pwd">修改密码</el-menu-item>
           </el-sub-menu>
          <el-menu-item index="/staff/joint/open">联合开户</el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header style="border-bottom: 1px solid var(--color-gray-200); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; position: sticky; top: 0; z-index: 1001;">
          <div style="display: flex; align-items: center; gap: 24px; height: 100%;">
            <span style="color: var(--color-gray-500);">工作人员界面</span>

            <div class="apple-nav-trigger" @click.stop="toggleMega">
              <span>业务快捷导航 ▾</span>
              
              <div class="apple-mega-dropdown" :class="{ 'is-active': showMega }">
                <div class="mega-content-grid" @click.stop>
                  
                   <div class="mega-column">
                     <span class="column-title">STOCK ACCOUNT / 证券账户</span>
                     <router-link to="/staff/securities/query" class="mega-link">查询证券账户 <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/securities/open" class="mega-link">开设证券账户 <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/securities/lost-reissue" class="mega-link">账户挂失业务 <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/securities/cancel" class="mega-link">账户注销业务 <span class="arrow">&rarr;</span></router-link>
                     <router-link to="/staff/joint/open" class="mega-link">联合开户业务 <span class="arrow">&rarr;</span></router-link>
                   </div>
                  
                  <div class="mega-column">
                    <span class="column-title">FUND ACCOUNT / 资金账户</span>
                    <router-link to="/staff/fund/query" class="mega-link">查询资金账户 <span class="arrow">&rarr;</span></router-link>
                    <router-link to="/staff/fund/transfer" class="mega-link">存取款业务办理 <span class="arrow">&rarr;</span></router-link>
                    <router-link to="/staff/fund/lost-reissue" class="mega-link">挂失补开业务 <span class="arrow">&rarr;</span></router-link>
                    <router-link to="/staff/fund/cancel" class="mega-link">账户注销业务 <span class="arrow">&rarr;</span></router-link>
                  </div>
                  
                  <div class="mega-column">
                    <span class="column-title">SYSTEM META / 系统状态</span>
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
            <el-button link @click="helpVisible = true" aria-label="帮助">
              <el-icon><QuestionFilled /></el-icon>
            </el-button>
            <el-button class="btn-secondary" @click="logout">退出</el-button>
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
