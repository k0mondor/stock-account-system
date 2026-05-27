<template>
  <el-drawer
    :model-value="modelValue"
    size="420px"
    :with-header="false"
    @close="emit('update:modelValue', false)"
  >
    <div class="help-shell">
      <div class="help-top">
        <div>
          <div class="help-title">帮助</div>
          <div class="help-subtitle">快捷键与规则速览</div>
        </div>
        <el-button class="btn-secondary" @click="emit('update:modelValue', false)">关闭</el-button>
      </div>

      <div class="help-section">
        <div class="help-h">快捷键</div>
        <div class="help-list">
          <div class="help-item">
            <span>打开/关闭帮助</span>
            <span class="kbd">?</span>
          </div>
          <div class="help-item">
            <span>关闭面板</span>
            <span class="kbd">Esc</span>
          </div>
        </div>
      </div>

      <div class="help-section">
        <div class="help-h">账户状态</div>
        <div class="help-list">
          <div class="help-item">
            <span class="mono">NORMAL</span>
            <span>正常</span>
          </div>
          <div class="help-item">
            <span class="mono">LOST</span>
            <span>挂失</span>
          </div>
          <div class="help-item">
            <span class="mono">FROZEN</span>
            <span>冻结</span>
          </div>
          <div class="help-item">
            <span class="mono">CLOSED</span>
            <span>销户</span>
          </div>
        </div>
      </div>

      <div class="help-section">
        <div class="help-h">数据源</div>
        <div class="help-list">
          <div class="help-item">
            <span>当前数据源</span>
            <span class="mono">{{ dataSource }}</span>
          </div>
          <div class="help-item">
            <span>切换方式</span>
            <span class="mono">VITE_DATA_SOURCE</span>
          </div>
        </div>
      </div>

      <div class="help-footer">
        <div class="help-muted">提示：关闭面板后可继续滚动与操作，不会误触发导航。</div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const dataSource = import.meta.env.VITE_DATA_SOURCE || 'mock'
</script>

<style scoped>
.help-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px;
}

.help-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.help-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.help-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
}

.help-section {
  border: 1px solid rgba(0, 0, 0, 0.06);
  padding: 14px 14px 10px;
}

.help-h {
  font-size: 11px;
  font-weight: 700;
  color: #6B7280;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.help-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.help-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-primary);
}

.kbd {
  font-family: 'SF Mono', 'JetBrains Mono', 'Courier New', monospace;
  font-size: 12px;
  border: 1px solid rgba(0, 0, 0, 0.22);
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.02);
}

.mono {
  font-family: 'SF Mono', 'JetBrains Mono', 'Courier New', monospace;
  font-size: 12px;
}

.help-footer {
  padding-top: 6px;
}

.help-muted {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.6;
}
</style>

