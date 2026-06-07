<template>
  <div :class="['page-info-card', `page-info-card--${variant}`, `page-info-card--${align}`]">
    <h4 v-if="title" class="page-info-card__title">{{ title }}</h4>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default'
  },
  align: {
    type: String,
    default: 'left'
  }
})
</script>
