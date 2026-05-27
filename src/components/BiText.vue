<template>
  <span class="bi-text" :class="{ 'is-stack': layout === 'stack' }">
    <template v-if="hasBi && layout === 'inline'">
      <span class="bi-zh">{{ zh }}/</span><wbr /><span class="bi-en">{{ en }}</span>
    </template>
    <template v-else-if="hasBi && layout === 'stack'">
      <span class="bi-zh">{{ zh }}/</span>
      <span class="bi-en">{{ en }}</span>
    </template>
    <template v-else>
      {{ text }}
    </template>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  layout: {
    type: String,
    default: 'inline',
    validator: (v) => ['inline', 'stack'].includes(v)
  }
})

const hasBi = computed(() => props.text.includes('/'))

const zh = computed(() => {
  const idx = props.text.indexOf('/')
  return idx === -1 ? props.text : props.text.slice(0, idx)
})

const en = computed(() => {
  const idx = props.text.indexOf('/')
  return idx === -1 ? '' : props.text.slice(idx + 1)
})
</script>

<style scoped>
.bi-text {
  white-space: normal;
  line-height: 1.25;
}

.bi-text.is-stack {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  line-height: 1.1;
}

.bi-en {
  word-break: keep-all;
  overflow-wrap: normal;
  hyphens: none;
}
</style>
