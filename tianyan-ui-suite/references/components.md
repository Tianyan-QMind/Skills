# 天衍 UI · 原子组件配方（组件白名单）

> 只允许使用以下组件，禁止自创新组件、禁止手写原生标签自定义样式。
> 每行样式注释标注对应规范条目。组件默认导出在 `src/components/` 下。
> 令牌名即 Tailwind 类名后缀（见 references/tokens.md）。

## 通用约定

- 颜色/字号/间距/圆角一律调用 token（`bg-primary`、`text-tip`、`rounded-btn`、`gap-20`）。
- 按钮最长不超过 128px（`max-w-btn`），内部文字居中。
- 可点击元素 hover：透明度 0.85（`hover:opacity-85`）或 primary 色过渡（`hover:text-primary` / `hover:border-primary`）。
- **版心 1640px**：页面根容器用 `max-w-1640` 约束（规范第三部分，强制）。
- **主标题左对齐**：页面主标题（h1）必须左对齐（规范第十部分）。

---

## 1. 按钮（规范 6.1，4 类封装组件 → 统一 Button.vue + variant）

> 《0818UI skill更新》11.2 提供统一 `Button.vue`，通过 `variant` 覆盖 4 类：
> `primary`(PrimaryBtn) / `line`(LineBtn) / `text`(TextBtn) / `disabled`(DisabledBtn)。

### Button.vue
```vue
<!-- components/Button.vue -->
<!-- 规范来源：第六部分 - 按钮组件白名单 -->
<template>
  <button
    :class="[
      'inline-flex items-center justify-center',
      'rounded-btn px-4 h-9',                          // 圆角4px，内边距，高度36px
      'font-sans text-minor',                          // 字体族 + 16px字号
      'transition-opacity duration-200',
      'max-w-btn whitespace-nowrap',                    // 最长128px
      variantClasses,
      { 'cursor-not-allowed opacity-60': disabled || variant === 'disabled' }
    ]"
    :disabled="disabled || loading"
    @click="!disabled && !loading && $emit('click')"
  >
    <!-- loading spin - 来源：第七部分 -->
    <span
      v-if="loading"
      class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
    ></span>
    <slot>{{ text }}</slot>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'line', 'text', 'disabled'].includes(v)
  },
  text: String,
  loading: Boolean,
  disabled: Boolean,
})

// 变体样式 - 来源：第六部分
const variantClasses = computed(() => {
  const map = {
    primary: 'bg-primary text-white hover:opacity-85',
    line: 'bg-transparent border border-borderLine text-textSub hover:border-primary hover:text-primary',
    text: 'bg-transparent text-ghost hover:text-primary',  // 卡片底部按钮：#7A8391→#1664FF
    disabled: 'bg-borderLine text-textBody',
  }
  return map[props.variant] || map.primary
})
</script>
```

> **4 类按钮 ↔ variant 映射**：`PrimaryBtn`=`variant="primary"` / `LineBtn`=`variant="line"` / `TextBtn`=`variant="text"` / `DisabledBtn`=`variant="disabled"`。
> **卡片区域底部按钮**：只展示文字，禁止边框，颜色 `#7A8391`（`text-ghost`），悬停为 `#1664FF`（`hover:text-primary`）。即 `variant="text"`。

---

## 2. Tab 栏（规范 6.2）

```vue
<template>
  <div class="inline-flex gap-20">
    <!-- 激活态：primary 底白字；未激活：cardBg 底 textBody 灰字 -->
    <button
      v-for="t in tabs" :key="t.key"
      @click="$emit('change', t.key)"
      class="rounded-btn px-20 py-20 text-tip transition-colors"
      :class="active === t.key ? 'bg-primary text-white' : 'bg-cardBg text-textBody hover:text-primary'"
    >
      {{ t.label }}
    </button>
  </div>
</template>
<script setup>
defineProps({ tabs: { type: Array, required: true }, active: { type: String, default: '' } });
defineEmits(['change']);
</script>
```
> 量子云场景 Tab 命名示例：概览 | 量子线路 | 任务记录 | 结果分析

---

## 3. 输入框（规范 6.3）

```vue
<template>
  <!-- 常态 border-borderLine / 聚焦 border-primary / 只读 bg-pageBg 浅灰底；内边距固定 12px 16px -->
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :readonly="readonly"
    @input="$emit('update:modelValue', $event.target.value)"
    class="h-10 w-full rounded-btn border border-borderLine bg-cardBg px-4 py-3 text-tip text-textTitle placeholder:text-textBody transition-colors focus:border-primary focus:outline-none"
    :class="readonly && 'bg-pageBg'"
  />
</template>
<script setup>
defineProps({
  modelValue: String,
  placeholder: String,
  readonly: Boolean,
  type: { type: String, default: 'text' }, // 文本/密码等（规范6.3）
});
defineEmits(['update:modelValue']);
</script>
```

---

## 4. Tag 标签（规范 6.5，来源 11.3）

```vue
<!-- components/Tag.vue -->
<!-- 规范来源：第六部分 - Tag标签 -->
<template>
  <span
    :class="[
      'inline-flex items-center rounded-tag',          // 圆角6px
      'px-2 py-1',                                     // 左右8px 上下4px
      'text-tip font-regular',                         // 14px Regular
      colorClasses
    ]"
  >
    <span
      v-if="showDot"
      class="w-2 h-2 rounded-full mr-1.5"
      :class="dotColor"
    ></span>
    <slot>{{ text }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 状态：待提交 / 运行中 / 已完成 / 失败 - 来源：第六部分
  status: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'cyan', 'deep', 'danger'].includes(v)
  },
  text: String,
  showDot: Boolean,
})

// 状态底色 + 文字色（RTF 11.3 规定的状态底色，属封装组件内部取值）
const colorClasses = computed(() => {
  const map = {
    primary: 'bg-quantumEntangle1 text-primary',   // 待提交 #ECF2FF
    cyan: 'bg-[#E0F7FA] text-cyan',               // 运行中
    deep: 'bg-[#E3EEFF] text-primaryDeep',         // 已完成
    danger: 'bg-[#FFE8E0] text-danger',            // 失败
  }
  return map[props.status] || map.primary
})

const dotColor = computed(() => {
  const map = {
    primary: 'bg-primary',
    cyan: 'bg-cyan',
    deep: 'bg-primaryDeep',
    danger: 'bg-danger',
  }
  return map[props.status] || map.primary
})
</script>
```
> 状态映射（规范 6.5）：待提交=primary / 运行中=cyan / 已完成=primaryDeep / 失败=danger。
> Tag 状态底色（`#E0F7FA`/`#E3EEFF`/`#FFE8E0`）为 RTF 11.3 封装组件内部规定的状态底色，属封闭豁免，禁止在业务代码中复用。

---

## 5. 状态指示器（规范 6.7，来源 11.4）

```vue
<!-- components/StatusDot.vue -->
<!-- 规范来源：第六部分 - 状态指示器 -->
<template>
  <span class="inline-flex items-center gap-1.5">
    <span
      class="w-2 h-2 rounded-full"                     // 8px直径
      :class="dotColor"
    ></span>
    <span class="text-tip text-textSub">{{ label }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'online',
    validator: (v) => ['online', 'offline', 'running', 'error'].includes(v)
  },
  label: String,
})

const dotColor = computed(() => {
  const map = {
    online: 'bg-success',       // 在线 #34C759
    offline: 'bg-textBody',     // 离线
    running: 'bg-cyan',         // 运行中
    error: 'bg-danger',        // 错误
  }
  return map[props.status] || map.online
})
</script>
```

---

## 6. 卡片（规范 6.6，来源 11.5）

```vue
<!-- components/Card.vue -->
<!-- 规范来源：第六部分 - 卡片规范 -->
<template>
  <div
    :class="[
      'rounded-modal',                                 // 圆角8px
      'p-6',                                           // 内边距24px
      'shadow-sm',                                     // 仅允许shadow-sm
      bgClass
    ]"
  >
    <slot></slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'base',
    validator: (v) => ['base', 'light'].includes(v)
  }
})

const bgClass = computed(() => {
  const map = {
    base: 'bg-cardBg',         // 卡片白底
    light: 'bg-cardBgLight',   // 卡片浅蓝背景（焦点卡）
  }
  return map[props.variant] || map.base
})
</script>
```
> `variant="light"`（`bg-cardBgLight`）用于核心结果/焦点卡突出。

---

## 7. 分页（规范附加：仅数字+上一页/下一页，禁止跳转输入框）

```vue
<template>
  <div class="flex items-center justify-end gap-20 text-tip text-textSub">
    <button class="transition-colors hover:text-primary" :disabled="page<=1">上一页</button>
    <button
      v-for="n in pages" :key="n"
      @click="$emit('change', n)"
      class="h-8 w-8 rounded-btn transition-colors"
      :class="n===page ? 'bg-primary text-white' : 'text-textSub hover:text-primary'"
    >{{ n }}</button>
    <button class="transition-colors hover:text-primary" :disabled="page>=total">下一页</button>
  </div>
</template>
<script setup>
defineProps({ page: Number, total: Number, pages: { type: Array, required: true } });
defineEmits(['change']);
</script>
```

---

## 8. Toast（全局顶部轻提示，规范第七部分）

```vue
<template>
  <Teleport to="body">
    <!-- 规范第七部分 顶部居中；成功/失败由 type 决定底色；仅 v-if 显隐（状态切换属功能指示性动效） -->
    <div
      v-if="visible"
      role="status"
      class="fixed left-1/2 top-30 z-50 flex -translate-x-1/2 items-center gap-20 rounded-modal px-20 py-20 text-tip text-white shadow-sm"
      :class="type === 'success' ? 'bg-success' : 'bg-danger'"
    >
      {{ message }}
      <!-- 规范第七部分 失败态可手动关闭；成功态 3s 自动消失 -->
      <button v-if="type === 'danger'" aria-label="关闭" class="transition-opacity hover:opacity-85" @click="visible = false">×</button>
    </div>
  </Teleport>
</template>
<script setup>
import { ref, onUnmounted } from 'vue';
const visible = ref(false);
const message = ref('');
const type = ref('success');
let timer = null;
function show(msg, kind = 'success') {
  message.value = msg;
  type.value = kind;
  visible.value = true;
  clearTimeout(timer);
  if (kind === 'success') {
    timer = setTimeout(() => (visible.value = false), 3000); // 成功3s自动消失
  }
}
defineExpose({ show });
onUnmounted(() => clearTimeout(timer));
</script>
```
> 失败态红色 `bg-danger`，可手动关闭；成功态 3s 自动消失。
> 骨架屏加载仅允许 `animate-pulse` 浅灰块，禁止自定义动画。

---

## 9. 图标（规范 6.4）

```vue
<template>
  <!-- 仅 计算/任务/时钟/图表/设置/导出 6类；1.5px线性轮廓，默认primary -->
  <svg
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    class="h-4 w-4 text-primary" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
    :aria-label="name"
  >
    <!-- 依 name 输出对应 1.5px 线性 path（计算/任务/时钟/图表/设置/导出） -->
    <component :is="paths[name]" />
  </svg>
</template>
<script setup>
defineProps({ name: { type: String, required: true } });
// paths 表：'计算'|'任务'|'时钟'|'图表'|'设置'|'导出' 各自的 1.5px 线性 SVG path
</script>
```

> **折叠/展开指示箭头（技能补充）**：折叠区状态指示箭头可用内联 SVG 绘制——1.5px 线性轮廓、`text-primary`、`h-4 w-4`、旋转 90° 表示展开（`transition-transform` 为状态切换指示动效）。属功能指示性图形（同 StatusDot 地位），仅限折叠交互使用，禁止用于其他装饰场景。

---

## 10. 滑块 Slider（技能补充白名单组件 · spec 未定义，为识别/工具页补充）

> 规范未规定滑块控件；本技能为「识别/工具页」补充白名单组件 Slider。
> 视觉参数仍 100% 走规范令牌：轨道 `borderLine`、填充 `primary`、手柄 8px 圆点（复用状态圆点常量）、圆头 `rounded-full`（封闭豁免）。

```vue
<template>
  <!-- 技能补充 Slider：轨道borderLine(h-1) / 填充primary / 手柄8px圆点primary（rounded-full封闭豁免） -->
  <div
    ref="root"
    role="slider"
    tabindex="0"
    :aria-label="label"
    :aria-valuemin="min"
    :aria-valuemax="max"
    :aria-valuenow="modelValue"
    class="relative flex h-2 w-full cursor-pointer touch-none select-none items-center"
    @pointerdown="onPointer"
    @keydown.left.prevent="step(-1)"
    @keydown.right.prevent="step(1)"
  >
    <!-- 轨道：borderLine 色 -->
    <div class="absolute h-1 w-full rounded-full bg-borderLine"></div>
    <!-- 已填充段：primary（宽度=数据百分比，非 px 常量，允许） -->
    <div class="absolute h-1 rounded-full bg-primary" :style="{ width: pct + '%' }"></div>
    <!-- 手柄：8px 圆点 primary -->
    <div class="absolute h-2 w-2 -translate-x-1/2 rounded-full bg-primary" :style="{ left: pct + '%' }"></div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue';
const props = defineProps({
  modelValue: { type: Number, required: true },
  min: { type: Number, required: true },
  max: { type: Number, required: true },
  step: { type: Number, default: 0.1 },
  label: { type: String, default: '' },
});
const emit = defineEmits(['update:modelValue']);
const root = ref(null);
const pct = computed(() => ((props.modelValue - props.min) / (props.max - props.min)) * 100);
function setFromClientX(clientX) {
  const rect = root.value.getBoundingClientRect();
  const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
  const raw = props.min + ratio * (props.max - props.min);
  const val = Math.round(raw / props.step) * props.step;
  emit('update:modelValue', Math.min(props.max, Math.max(props.min, val)));
}
function onPointer(e) { setFromClientX(e.clientX); }
function step(dir) {
  const val = Math.min(props.max, Math.max(props.min, props.modelValue + dir * props.step));
  emit('update:modelValue', Math.round(val * 10) / 10);
}
</script>
```

---

## 11. 进度条 Progress（技能补充白名单组件 · 数据可视化扩展）

> 规范未规定进度条；本技能补充白名单组件 Progress。
> 轨道 `borderLine`、填充走拓展色序（primary/primaryDeep/cyan/quantumPurple/quantumIndigo/quantumBlue）、宽度=数据百分比（非 px 常量）。

```vue
<template>
  <!-- 技能补充 Progress：轨道borderLine(h-1) / 填充数据色 / 宽度=数据百分比；圆头rounded-full封闭豁免 -->
  <div class="h-1 w-full rounded-full bg-borderLine">
    <div
      class="h-full rounded-full transition-all duration-300"
      :class="colorClass"
      :style="{ width: pct + '%' }"
    ></div>
  </div>
</template>
<script setup>
import { computed } from 'vue';
const props = defineProps({
  value: { type: Number, default: 0 }, // 0~1
  color: { type: String, default: 'primary' }, // 走拓展色序
});
const pct = computed(() => Math.max(0, Math.min(100, props.value * 100)));
const colorClass = computed(() => ({
  primary: 'bg-primary',
  primaryDeep: 'bg-primaryDeep',
  cyan: 'bg-cyan',
  quantumPurple: 'bg-quantumPurple',
  quantumIndigo: 'bg-quantumIndigo',
  quantumBlue: 'bg-quantumBlue',
  success: 'bg-success',
  danger: 'bg-danger',
}[props.color] ?? 'bg-primary'));
</script>
```

---

## 组件白名单总表

| 组件 | 关键类 | 规范条目 |
|---|---|---|
| Button（variant=primary/line/text/disabled） | `bg-primary text-white rounded-btn max-w-btn h-9 hover:opacity-85` | 6.1 |
| 卡片底部按钮 | `text-ghost hover:text-primary`（禁止边框） | 6.1 |
| Tab | 激活 `bg-primary text-white` / 未激活 `bg-cardBg text-textBody` | 6.2 |
| Input | `border-borderLine focus:border-primary read-only:bg-pageBg px-4 py-3` | 6.3 |
| Tag | `rounded-tag px-2 py-1` + 状态底色（primary/cyan/deep/danger） | 6.5 |
| StatusDot | `w-2 h-2 rounded-full` + 语义色（success/textBody/cyan/danger） | 6.7 |
| Card | `rounded-modal bg-cardBg p-6 shadow-sm`（无边框）；`variant="light"` → `bg-cardBgLight` 焦点卡 | 6.6 |
| Pagination | 数字 + 上一页/下一页，禁止跳转框 | 附加 |
| Toast | 顶部居中，success 3s / danger 可关闭 | 第七部分 |
| Icon | 6 类 1.5px 线性，`text-primary` | 6.4 |
| Slider（技能补充） | 轨道 `bg-borderLine` h-1 / 填充 `bg-primary` / 手柄 8px 圆点；圆头 `rounded-full` 封闭豁免 | 补充 |
| Progress（技能补充） | 轨道 `bg-borderLine` h-1 / 填充拓展色序 / 宽度=数据百分比 | 补充 |
