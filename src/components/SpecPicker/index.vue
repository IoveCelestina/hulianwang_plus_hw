<template>
  <div class="spec-picker">
    <div v-if="groups.length === 0" class="empty">该菜品无可选规格</div>

    <div v-for="g in groups" :key="g.spec_name" class="group">
      <div class="label">
        {{ g.spec_name }}
        <span v-if="required && g.options.length" class="req">*</span>
      </div>

      <el-radio-group
        v-model="local[g.spec_name]"
        class="radios"
        @change="emitChange"
      >
        <el-radio-button
          v-for="opt in g.options"
          :key="opt.value"
          :label="opt.value"
        >
          <span class="opt">
            <span class="opt-name">{{ opt.label }}</span>
            <span v-if="showDelta && opt.priceDelta !== 0" class="delta">
              +¥{{ opt.priceDelta }}
            </span>
          </span>
        </el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

type DishSpecOut = {
  id: number
  spec_name: string
  spec_values: any[] // 真实后端：list[dict{name, price?}]（也做了兼容 string）
}

const props = withDefaults(
  defineProps<{
    specs: DishSpecOut[]
    modelValue: Record<string, any>
    required?: boolean
    showDelta?: boolean
  }>(),
  { required: true, showDelta: true }
)

const emit = defineEmits<{
  (e: 'update:modelValue', v: Record<string, any>): void
}>()

const local = reactive<Record<string, any>>({})

// 归一化 options：支持 dict{name,price?} / string
function normalizeOptions(values: any[]) {
  const out: { label: string; value: string; priceDelta: number }[] = []
  for (const v of values || []) {
    if (typeof v === 'string') {
      out.push({ label: v, value: v, priceDelta: 0 })
    } else if (v && typeof v === 'object' && typeof v.name === 'string') {
      const pd = Number(v.price ?? 0)
      out.push({ label: v.name, value: v.name, priceDelta: Number.isFinite(pd) ? pd : 0 })
    }
  }
  return out
}

const groups = computed(() => {
  return (props.specs || []).map((s) => ({
    spec_name: s.spec_name,
    options: normalizeOptions(s.spec_values || []),
  }))
})

function syncFromModel() {
  const mv = props.modelValue || {}
  // 初始化 local
  for (const g of groups.value) {
    const cur = mv[g.spec_name]
    // 若未选，默认选第一项（更顺滑，也避免生成 invalid 组合）
    local[g.spec_name] = cur ?? (g.options[0]?.value ?? undefined)
  }
}
watch(() => [props.specs, props.modelValue], syncFromModel, { immediate: true, deep: true })

function emitChange() {
  emit('update:modelValue', JSON.parse(JSON.stringify(local)))
}
</script>

<style scoped lang="scss">
.spec-picker {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.group .label {
  font-size: 12px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 8px;
}
.req { color: #ef4444; margin-left: 4px; }
.radios :deep(.el-radio-button__inner) {
  border-radius: 10px;
}
.opt {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.delta {
  font-size: 12px;
  font-weight: 900;
  color: var(--app-primary);
}
.empty {
  padding: 14px;
  border-radius: 12px;
  border: 1px dashed var(--app-border);
  background: #fff;
  color: var(--app-muted);
  font-size: 12px;
}
</style>
