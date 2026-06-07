<template>
  <el-card :class="['page-panel', `page-panel--${width}`]">
    <slot />
  </el-card>
</template>

<script setup>
defineProps({
  width: {
    type: String,
    default: 'wide'
  }
})
</script>
