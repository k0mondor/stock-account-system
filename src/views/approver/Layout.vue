<!-- src/views/approver/Layout.vue -->
<template>
  <el-container style="min-height: 100vh;">
    <el-aside width="220px" style="background: #f5f5f5; border-right: 1px solid var(--color-gray-200);">
      <div class="logo">账户业务子系统</div>
      <el-menu
        :default-active="$route.path"
        router
        style="border-right: none;"
      >
        <el-menu-item index="/approver/approval">审批列表</el-menu-item>
        <el-menu-item index="/approver/log">操作日志</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="border-bottom: 1px solid #e5e4e7; display: flex; align-items: center; justify-content: space-between; padding: 0 24px;">
        <span style="color: var(--color-gray-500);">审批人员界面</span>
        <el-button type="default" size="large" @click="logout" style="padding: 8px 24px; font-size: 14px;">退出</el-button>
      </el-header>
      <el-main style="background: #f8f9fa; padding: 40px 24px;">
        <div style="max-width: 1100px; margin: 0 auto;">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const logout = () => router.push('/login')
</script>

<style scoped>
.logo { padding: 24px; font-weight: 600; }
</style>
