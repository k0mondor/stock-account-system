<template>
  <div :class="['page-form-block', `page-form-block--${width}`]">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  width: {
    type: String,
    default: 'narrow'
  }
})
</script>
