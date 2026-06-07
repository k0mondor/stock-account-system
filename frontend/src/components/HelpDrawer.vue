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
          <div class="help-title"><BiText :text="UiText.help" /></div>
          <div class="help-subtitle"><BiText text="快捷键与规则速览/SHORTCUTS & RULES" /></div>
        </div>
        <el-button class="btn-secondary" @click="emit('update:modelValue', false)"><BiText text="关闭/CLOSE" /></el-button>
      </div>

      <div class="help-section">
        <div class="help-h"><BiText text="快捷键/SHORTCUTS" /></div>
        <div class="help-list">
          <div class="help-item">
            <BiText text="打开或关闭帮助/TOGGLE HELP" />
            <span class="kbd">?</span>
          </div>
          <div class="help-item">
            <BiText text="关闭面板/CLOSE" />
            <span class="kbd">Esc</span>
          </div>
        </div>
      </div>

      <div class="help-section">
        <div class="help-h"><BiText text="账户状态/STATUS" /></div>
        <div class="help-list">
          <div class="help-item">
            <span class="mono">NORMAL</span>
            <BiText text="正常/NORMAL" />
          </div>
          <div class="help-item">
            <span class="mono">LOST</span>
            <BiText text="挂失/LOST" />
          </div>
          <div class="help-item">
            <span class="mono">FROZEN</span>
            <BiText text="冻结/FROZEN" />
          </div>
          <div class="help-item">
            <span class="mono">CLOSED</span>
            <BiText text="销户/CLOSED" />
          </div>
        </div>
      </div>

      <div class="help-section">
        <div class="help-h"><BiText text="联调模式/INTEGRATION" /></div>
        <div class="help-list">
          <div class="help-item">
            <BiText text="接口前缀/API BASE" />
            <span class="mono">{{ apiBaseUrl }}</span>
          </div>
          <div class="help-item">
            <BiText text="鉴权方式/AUTH" />
            <span class="mono">Bearer Token</span>
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
import { UiText } from '@/constants/i18n'
import BiText from '@/components/BiText.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'same-origin'
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
