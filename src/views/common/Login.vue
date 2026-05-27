<template>
  <div class="login-page-container">
    
    <div class="norris-stage">
      <div class="norris-title-wrapper">
        <h1 class="norris-title">STOCK ACCOUNT SYSTEM</h1>
        <div class="shutter-swipe-bar"></div>
      </div>
    </div>

    <div class="login-content-area">
      <el-card class="login-card">
        
        <div class="login-header-centered">
          <div class="wave-roller-container">
            <div 
              v-for="(char, index) in titleChars" 
              :key="index" 
              class="letter-cube"
              :style="{ '--delay': `${index * 0.06}s` }"
            >
              <span class="cube-face face-front">{{ char.zh }}</span>
              <span class="cube-face face-bottom" :class="{ 'small-font': char.en.length > 1 }">
                {{ char.en }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="role-select">
          <button class="btn-primary" @click="loginAsStaff">
            <BiText :text="UiText.staffEntry" layout="stack" />
          </button>
          <button class="btn-secondary" @click="loginAsApprover">
            <BiText :text="UiText.approverEntry" layout="stack" />
          </button>
        </div>
        
        <p class="tip">点击按钮直接进入对应界面（Demo 无真实鉴权）</p>
      </el-card>
    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { UiText } from '@/constants/i18n'
import BiText from '@/components/BiText.vue'

const router = useRouter()

const titleChars = [
  { zh: '系', en: '系' },
  { zh: '统', en: '统' },
  { zh: '登', en: '登' },
  { zh: '录', en: '录' }
]

const loginAsStaff = () => {
  router.push('/staff/securities/query')
}

const loginAsApprover = () => {
  router.push('/approver')
}
</script>

<style scoped>
/* 全局页面容器 */
.login-page-container {
  width: 100%;
  min-height: 100vh;
  background-color: #F4F5F6; 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  overflow-x: hidden;
  padding-bottom: 80px;
}

.norris-stage {
  width: 100vw;
  height: 35vh; 
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.norris-title-wrapper {
  position: relative;
  display: inline-block;
  overflow: hidden;
}

.norris-title {
  font-family: 'Inter', -apple-system, sans-serif !important;
  font-size: 72px;
  font-weight: 900;
  letter-spacing: -0.04em !important;
  color: #111111;
  margin: 0;
  white-space: nowrap;
  user-select: none;
  animation: fadeInText 0.1s linear forwards;
  animation-delay: 0.35s; 
  opacity: 0;
}

.shutter-swipe-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #000000;
  z-index: 2;
  animation: norrisSwipeRight 1.4s cubic-bezier(0.25, 1, 0.2, 1) forwards;
}

@keyframes fadeInText {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

@keyframes norrisSwipeRight {
  0% {
    transform: translateX(-100%) scaleX(1);
    transform-origin: left center;
  }
  45% {
    transform: translateX(0%) scaleX(1);
    transform-origin: left center;
  }
  46% {
    transform: translateX(0%) scaleX(1);
    transform-origin: right center;
  }
  100% {
    transform: translateX(100%) scaleX(0);
    transform-origin: right center;
  }
}

/* 
 * Lando 3D 翻转动效
 * 登录标题的 3D 翻转立方体效果
 */
.login-header-centered {
  display: flex;
  justify-content: center; 
  align-items: center;
  margin-bottom: 40px;     
  height: 36px;            
}

.wave-roller-container {
  display: flex;
  gap: 2px;
  perspective: 300px;
}

.letter-cube {
  position: relative;
  width: 32px;  
  height: 36px; 
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--delay);
}

.login-card:hover .letter-cube {
  transform: rotateX(90deg); 
}

.cube-face {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backface-visibility: hidden; 
}

.face-front {
  font-size: 24px;
  font-weight: 700;
  color: #111111;
  transform: rotateX(0deg) translateZ(18px);
}

.face-bottom {
  font-size: 20px; 
  font-weight: 900;
  color: #9CA3AF; 
  transform: rotateX(-90deg) translateZ(18px);
}

.small-font {
  font-size: 16px !important;
  letter-spacing: -0.02em;
}

/* 
 * 登录表单区域
 * 保持与全局风格一致的直角卡片设计
 */
.login-content-area {
  width: 100%;
  max-width: 420px;
  padding: 0 20px;
  z-index: 10;
}

.login-card {
  border-radius: 0px !important;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.015) !important;
  border: 1px solid rgba(0, 0, 0, 0.03) !important;
  background-color: #FFFFFF !important;
  padding: 24px 10px;
}

.role-select {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 24px;
}

.btn-primary {
  flex: 1;
  padding: 14px 0;
  background: #000000 !important;
  color: #FFFFFF !important;
  font-size: 14px;
  font-weight: 600;
  border: 1px solid #000000 !important;
  border-radius: 0px !important;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: background-color 0.15s ease-in-out !important;
}
.btn-primary:hover {
  background: #222222 !important;
}

.btn-secondary {
  flex: 1;
  padding: 14px 0;
  background: #FFFFFF !important;
  color: #000000 !important;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid #000000 !important;
  border-radius: 0px !important;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.15s ease-in-out !important;
}
.btn-secondary:hover {
  background: #000000 !important;
  color: #FFFFFF !important;
}

.tip {
  font-size: 11px;
  color: #9CA3AF;
  text-align: center;
  margin: 0;
}
</style>
