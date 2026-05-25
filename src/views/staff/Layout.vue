<template>
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
      <el-header style="border-bottom: 1px solid var(--color-gray-200); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; background: var(--color-white);">
        <div style="display: flex; align-items: center; gap: 24px; height: 100%;">
          <span style="color: var(--color-gray-500);">工作人员界面</span>

          <div class="apple-nav-trigger" @mouseenter="openMega" @mouseleave="closeMega">
            <span>业务快捷导航 ▾</span>
            
            <div class="apple-mega-dropdown" :class="{ 'is-active': showMega }" @mouseenter="openMega" @mouseleave="closeMega">
              <div class="mega-content-grid" @click.stop>
                
                <div class="mega-column">
                  <span class="column-title">STOCK ACCOUNT / 证券账户</span>
                  <router-link to="/staff/securities/query" class="mega-link">查询证券账户 <span class="arrow">&rarr;</span></router-link>
                  <router-link to="/staff/securities/open" class="mega-link">开设证券账户 <span class="arrow">&rarr;</span></router-link>
                  <router-link to="/staff/securities/lost-reissue" class="mega-link">账户挂失业务 <span class="arrow">&rarr;</span></router-link>
                  <router-link to="/staff/securities/cancel" class="mega-link">账户注销业务 <span class="arrow">&rarr;</span></router-link>
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
            
            <div class="apple-blur-overlay" :class="{ 'is-active': showMega }"></div>
          </div>
        </div>
        
        <el-button class="btn-secondary" @click="logout">退出</el-button>
      </el-header>
      <el-main style="background: var(--color-beige); padding: 40px 24px;">
        <div style="max-width: 1100px; margin: 0 auto;">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showMega = ref(false)
let leaveTimer = null

const openMega = () => {
  if (leaveTimer) {
    clearTimeout(leaveTimer)
    leaveTimer = null
  }
  showMega.value = true
}

const closeMega = () => {
  leaveTimer = setTimeout(() => {
    showMega.value = false
  }, 150)
}

const logout = () => {
  router.push('/login')
}
</script>

<style scoped>
.logo {
  padding: 24px;
  font-weight: 600;
  font-size: 18px;
  border-bottom: 1px solid var(--color-gray-200);
  color: var(--color-black);
}

/* 2. 注入针对退出按钮的 Swiss 样式穿透覆盖 */
:deep(.el-button.btn-secondary) {
  padding: 8px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  border-radius: 0 !important; /* 直角 */
  background: #fff !important;
  color: #000 !important;
  border: 2px solid #000 !important; /* 粗黑边框 */
  transition: all 0.2s ease !important;
  height: auto !important;
}

:deep(.el-button.btn-secondary:hover) {
  background: #000 !important;
  color: #fff !important;
  border-color: #000 !important;
}
</style>
