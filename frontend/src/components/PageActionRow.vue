<template>
  <div :class="['page-action-row', `page-action-row--${align}`]">
    <button
      :type="primaryType"
      class="btn-primary"
      :disabled="primaryDisabled"
      @click="$emit('primary')"
    >
      {{ primaryText }}
    </button>
    <button
      v-if="secondaryText"
      :type="secondaryType"
      class="btn-secondary"
      :disabled="secondaryDisabled"
      @click="$emit('secondary')"
    >
      {{ secondaryText }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  align: {
    type: String,
    default: 'center'
  },
  primaryText: {
    type: String,
    required: true
  },
  secondaryText: {
    type: String,
    default: ''
  },
  primaryType: {
    type: String,
    default: 'button'
  },
  secondaryType: {
    type: String,
    default: 'button'
  },
  primaryDisabled: {
    type: Boolean,
    default: false
  },
  secondaryDisabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['primary', 'secondary'])
</script>
