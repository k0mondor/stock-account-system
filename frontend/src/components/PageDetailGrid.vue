<template>
  <div :class="['page-detail-grid', `page-detail-grid--${columns}`]">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  columns: {
    type: Number,
    default: 2
  }
})
</script>
