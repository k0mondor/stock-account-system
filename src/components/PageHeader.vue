<!-- src/components/PageHeader.vue -->
<template>
  <div class="page-header">
    <div class="left">
      <el-button v-if="showBack" link @click="goBack" style="margin-right: 12px;">
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h2 class="title">{{ title }}</h2>
    </div>
    <div class="right">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  showBack: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e4e7;
}

.left {
  display: flex;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #000;
}
</style>
