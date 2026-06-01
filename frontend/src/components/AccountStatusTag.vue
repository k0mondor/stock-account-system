<!-- src/components/AccountStatusTag.vue -->
<template>
  <el-tag :type="tagType" size="small">
    {{ AccountStatusLabel[status] || status }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'
import { AccountStatusLabel } from '@/constants/enums'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const tagType = computed(() => {
  // 统一使用默认样式，避免任何彩色（blue/red/yellow）
  return ''
})
</script>