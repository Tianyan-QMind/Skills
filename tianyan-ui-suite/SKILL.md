---
name: tianyan-ui-suite
description: "Build and review polished TianYan UI 2.0 surfaces for runnable quantum applications. Use for standalone FastAPI pages, algorithm showcases, responsive result views, and traceable quantum-circuit visualizations."
---

# 天衍 UI · 量子应用展示合同

你是资深前端开发，负责构建天衍 UI 量子应用展示页。

## 铁则 0：框架层与业务层分离（**执行流程 — 严格按顺序走**）

> **禁止**：Agent 跳过 `materialize_qml_app_surface` 工具、自己写 `index.html`，导致模板文件被覆写。
> 本铁则规定的是**可执行的 step-by-step 流程**，不是建议。任何一步没做到，后续全部作废。

### Step 1：必须先跑 `materialize_qml_app_surface`（没有例外）

### Step 2：验证框架文件确实写入了（防止 conflict 静默失败）

### Step 3：**只**写 `backend/application.py`（这是你唯一能碰的文件）

| 文件 | 你能做什么 |
|------|-----------|
| `backend/application.py` | ✅ 创建 + 编辑 — 写业务逻辑和 API 返回数据 |
| `frontend/standalone/index.html` | ❌ 绝对禁止读写 — materializer 管（conflict 恢复时 Read+Write 模板除外） |
| `backend/main.py` | ❌ 绝对禁止读写 — 框架 API 壳，校验合同（同上） |
| `scripts/serve.py` | ❌ 绝对禁止读写 — 启动脚本（同上） |
| `tests/test_smoke.py` | ❌ 绝对禁止读写 — 测试（同上） |
| `application_manifest.json` | ❌ 绝对禁止读写 — materializer 自动维护 |

> **例外说明**：conflict 恢复子流程中，允许从 `assets/` Read 模板内容然后 Write 覆盖应用目录下的冲突文件。这是**恢复原状**，不是自定义修改。恢复完成后，框架文件再次不可变。

### Step 4：完成后跑验证
```
inspect_app_surface → python scripts/serve.py → pytest tests/test_smoke.py
```

---

### Conflict 恢复子流程（materialize 返回 conflict 时）

> **什么时候会遇到 conflict？** 之前某次运行写了自定义的 index.html，现在 materialize 想写模板但检测到文件已存在且内容不同。
>
> **模板源文件在哪？** 在本 skill 同级的 `assets/` 目录（和 SKILL.md 同属 `tianyan-ui-suite/`）。路径固定：
> - `assets/frontend/standalone/index.html`
> - `assets/backend/main.py`
> - `assets/scripts/serve.py`
> - `assets/tests/test_smoke.py`

**遇到 conflict 时，用 Read + Write 恢复模板原样**（这是"恢复"不是"自定义修改"，属于应急修复，正常流程不允许这样做）：

1. **Read** 从 `assets/` 读取每个冲突文件的模板内容
2. **Write** 把模板内容写入应用目录下对应的冲突文件（覆盖旧内容）
3. **重新调用** `materialize_qml_app_surface(application_slug="<同slug>")` — 此时 SHA 相同，应该返回 `unchanged`，不再 conflict
4. 验证通过后，才能开始写 `backend/application.py`


> **为什么这不算违反"禁写框架文件"的铁则？**
> - 正常流程：materialize 成功 → 框架文件已经是模板 → 不能改
> - Conflict 恢复：框架文件被改坏了 → Write 把它改回模板原样 → 这是修复，不是自定义
> - 恢复完成后，框架文件再次不可变，回到正常流程约束

---

---

### 仲裁优先级

`spec-source.md`（规范原文铁则）> 本文件 > tokens.md / components.md / checklist.md > 业务偏好

---

## 需求 0：顶部双栏等高对齐（铁约束）

核心 CSS（模板内置）：
- `.top-grid { display:flex; align-items:stretch }` — 父容器 stretch 让两侧等高
- `.input-card, .result-card { flex:1; display:flex; flex-direction:column }` — 消除空白
- `.action-row { margin-top:auto }` — 按钮自动靠底

字段数量自适应：≤12→2列，13–16→3列，**>16→3列+分组折叠**。

### 需求 0·补：页面布局紧凑性（空白防呆约束）

模板已内置等高对齐（`.top-grid { align-items:stretch }` + `.input-card/.result-card { flex:1 }`），
但后端返回的**内容体量**仍可能导致视觉空白。以下字段必须控制长度/数量。

#### 顶部摘要区高度约束
| 字段 | 上限 | 原因 |
|------|------|------|
| `scenario_summary` / `_en` | 中文 ≤ 60 字、英文 ≤ 100 词，1–2 句 | page-header 只有单行内边距，过长会撑高顶部并在标题区上方留空白 |
| `description` / `_en` | 中文 ≤ 50 字、英文 ≤ 80 词，1 句 | 作为标题下方副标题，过长会把 top-grid 向下推 |

#### 输入区 vs 结果区高度平衡
| 字段 | 建议范围 | 原因 |
|------|---------|------|
| `fields[]` | 4–12 个 | ≤2 个输入卡内容稀疏；>16 触发 3 列+分组折叠，输入卡可能高于结果卡 |
| `prediction.scores[]` | 2–5 项 | 运行后结果卡高度 = risk-display + compare-panel + tips-bar；过多 score 标签让结果卡显著高于输入卡 |
| `method_steps[]` | 3–6 步 | 步骤条 `repeat(N,1fr)` 自适应；>6 步挤压或换行 |
| `prediction.label` | ≤ 8 字 / ≤ 16 字符 | 主结果区大字显示，过长换行撑高 risk-main |

#### 运行后状态约束
- "等待运行"态：结果卡显示占位（risk-main + compare-panel + tips-bar），输入卡通过 `flex:1` +
  `action-row { margin-top:auto }` 让按钮贴底，**禁止**返回空字符串或 `null` 字段让卡片塌陷。
- 推理成功后：`explanations[]` 建议 2–4 条；tips-bar 单行展示，过长自动换行但不应超过 3 行。
- `scientific_boundary[]` 建议 2–4 条；在 tips-bar 以分隔符拼接，过多会撑高 tips-bar。

> **自检**：生成后打开页面，检查 (1) 场景摘要与标题之间无超过 40px 的空白；
> (2) 输入卡底部按钮贴底、无卡片外背景色空白；(3) 运行后左右两卡底部对齐。

---

## 需求 1：中英文双语（i18n 铁约束）

所有框架静态文本走 `data-i18n` + `I18N` 字典 + `t(key)` 函数。`I18N.en` 每个 key **必须有真实英文翻译**，禁止占位注释。语言切换入口为 `applyLanguage(lang)`。

**泄漏防护**（铁约束——`applyLanguage('en')` 后全页不得有任何中文字符）：
1. JS 动态框架文本必须 `t(key)`，禁止硬编码中文
2. SVG `<text>` 算法相关内容带 `data-i18n`
3. 自检：grep `[\u4e00-\u9fff]` 仅命中 `I18N.zh` 和注释
4. **application.py 的所有业务数据字段必须配全 `_en` 版本**（见下方完整清单）。前端逻辑是"有 `_en` 用 `_en`，没有降级显示中文"——**如果你不配 `_en`，英文页面必然显示中文，这是不可接受的泄漏**。

---

### 模板双语合同（任何模板必须实现）

业务数据双语由**模板**负责消费 `_en` 字段，`application.py` 只负责提供。任何模板（含替换模板）必须满足：

1. **标量字段选择器** `L(obj, key)`：当前语言为 `en` 且 `obj[key + '_en']` 非空时返回该值，否则返回 `obj[key]`。
2. **数组字段选择器** `LArr(zhArr, enArr)`：当前语言为 `en` 且 `enArr` 非空数组时返回 `enArr`，否则返回 `zhArr`。
3. 所有渲染业务数据的函数必须通过上述选择器取值，禁止直接读取中文字段。
4. 语言切换函数（如 `applyLanguage`）必须重新调用所有业务渲染函数（含 `renderInputForm`），且重渲染输入表单时**保留用户已输入的值**，不得重置为默认值。
5. 框架自带的 `standalone/index.html` 已实现上述合同；替换模板时须自行实现等价逻辑。

**消费清单**（模板必须用选择器读取的字段）：

| 渲染位置 | 中文字段 | 英文字段 | 选择器 |
|---------|---------|---------|--------|
| 页面标题 / 副标题 / 页头 | `title` / `description` / `scenario_summary` | `title_en` / `description_en` / `scenario_summary_en` | `L()` |
| 输入字段标签 | `fields[].label` | `fields[].label_en` | `L()` |
| 预设按钮名 | `presets[].name` | `presets[].name_en` | `L()` |
| 流程步骤 | `method_steps[].title` / `detail` | `title_en` / `detail_en` | `L()` |
| 性能概览标签 | `metrics[].label` | `label_en` | `L()` |
| 推理结果主标签 | `prediction.label` | `label_en` | `L()` |
| 分数语义 | `prediction.score_semantics` | `score_semantics_en` | `L()` |
| 分数标签 | `prediction.scores[].label` | `label_en` | `L()` |
| 解释文案 | `explanations[]` | `explanations_en[]` | `LArr()` |
| 推理边界提示 | `boundary[]` | `boundary_en[]` | `LArr()` |
| 数值单位 | `prediction.unit` | `prediction.unit_en` | `L()` |
| 收敛单位 | `convergence.unit` | `convergence.unit_en` | `L()` |
| 科学边界 | `scientific_boundary[]` | `scientific_boundary_en[]` | `LArr()` |
| 收敛语义说明 | `convergence.semantics` | `semantics_en` | `L()` |

**模块级常量**：`application.py` 必须定义 `SCORE_SEMANTICS`（中文），推荐同时定义 `SCORE_SEMANTICS_EN`（英文）。`/api/health` 会返回两者，模板在 `prediction.score_semantics` 缺失时用 `L(__apiHealth, 'score_semantics')` 兜底。未定义 `SCORE_SEMANTICS_EN` 时框架自动降级为中文。

---

### application.py 必须提供的 `_en` 字段完整清单

下列字段全部**必须**有中英双语版本。**没有例外**。

| 字段路径 | 中文 key | 英文 key | 示例 |
|---------|---------|---------|------|
| 应用元数据 | `title` | `title_en` | `"金融欺诈量子检测"` → `"Quantum Financial Fraud Detection"` |
| 应用描述 | `description` | `description_en` | `"基于 Qiskit..."` → `"Built on Qiskit..."` |
| 场景摘要 | `scenario_summary` | `scenario_summary_en` | `"输入交易特征..."` → `"Enter transaction features..."` |
| 输入字段 | `fields[].label` | `fields[].label_en` | `"交易金额"` → `"Transaction Amount"` |
| 输入字段 | `fields[].id` | （无英文版本，保持 snake_case） | `amount` |
| 预设 | `presets[].name` | `presets[].name_en` | `"欺诈样本"` → `"Fraud Sample"` |
| 流程步骤 | `method_steps[].title` | `method_steps[].title_en` | `"量子核计算"` → `"Quantum Kernel Computation"` |
| 流程步骤 | `method_steps[].detail` | `method_steps[].detail_en` | `"使用 ZZFeatureMap..."` → `"Uses ZZFeatureMap..."` |
| 展示指标 | `metrics[].label` | `metrics[].label_en` | `"量子准确率"` → `"Quantum Accuracy"` |
| 展示指标 | `metrics[].desc_zh` | `metrics[].desc_en` | （已在 main.py 校验中强制） |
| 推理结果 | `prediction.label` | `prediction.label_en` | `"正常"` → `"Normal"` |
| 推理结果 | `prediction.score_semantics` | `prediction.score_semantics_en` | `"置信度"` → `"Confidence"` |
| 推理结果 | `prediction.scores[].label` | `prediction.scores[].label_en` | `"欺诈"` → `"Fraud"` |
| 推理结果 | `prediction.unit` | `prediction.unit_en` | `"万元"` → `"CNY 10k"`（物理单位如 `eV`、`Ha` 可省略 `unit_en`） |
| 推理边界 | `boundary[]` | `boundary_en[]` | 中文边界数组 + 英文边界数组 |
| 解释文案 | `explanations[]` | `explanations_en[]` | 中文解释数组 + 英文解释数组 |
| 科学边界 | `scientific_boundary[]` | `scientific_boundary_en[]` | 中文边界 + 英文边界 |
| 量子线路 | `circuit` / `quantum.gates[].gate` | （门符号国际化：`H`, `RY`, `CNOT` 已是英文） |

**关键规则**：
- `label` 类字段必须提供 `_en` 版本，禁止只给中文
- `label_en` 必须是真实英文（不是拼音、不是中文翻译）
- `explanations_en[]` 和 `scientific_boundary_en[]` 必须存在且与中文版一一对应
- 如果 AI 不确定精确翻译，**必须**查专业词典或用通用描述，禁止省略 `_en` 字段

**main.py 校验**：main.py 目前对 `_en` 字段是推荐校验（存在时检查格式），但作为生成 AI 的提示约束，SKILL.md 必须写死"全部 `_en` 字段必配"。

---

## 需求 2：算法性能概览（metric+desc 交替网格）

固定 2×2 网格（`metric | desc | metric | desc`），每个 metric **必须配 desc 描述文字**（禁止只输出 metric 卡）。每组内容：`{ value, labelZh, labelEn, descZh, descEn, colorClass }`。

value **必须是带单位的展示字符串**（如 `"94.7%"`、`"0.895"`、`"128×"`），**禁止裸数字 `0` / `0.0` / 空字符串**（后端 main.py 正则拒绝）。

---

## 可选训练图表（框架自动渲染）

Qiskit / Cqlib VQC 的离线 `train_and_save` 自动保存 `models/<model>.training.json`，返回
`training_evidence_file`。在 `backend/application.py` 中将 `TRAINING_EVIDENCE_PATH`
设为该返回值（应用根目录下的相对路径）。框架 `/api/training` 会只读加载记录，校验模型
SHA256 与参数后展示实际损失、迄今最低损失、初始参数及 JSON 中的训练参数，并提供完整精度表格。
这些数值必须来自实际训练，不能由大模型编造或从其他应用截图抄写。
保持推理只读，不要在 `get_info`、`infer` 或导入后端时启动训练。
QSVC 及没有记录的模型不设置此常量；框架说明缺失原因，不伪造 VQC 训练曲线。
记录失效只影响图表；不要为了补图而阻断原本可用的推理。

## 需求 3：量子线路（真实门序列）

从实际参与计算的 SDK 线路对象提取门序列，保持操作顺序、量子位顺序和完整数值参数。
`stage` 是非空说明字符串，例如 feature_map、ansatz、cost、mixer；没有固定阶段数量。
线路没有测量指令时，不得为凑齐阶段添加 M；经典分类器、能量汇总和解码应放在方法流程中。
不得根据算法名称手工猜测门表或只画部分层；尤其不能遗漏 ZZFeatureMap 中的 H 或改写相位系数。
对于 Qiskit，应对与推理相同参数绑定后的线路读取 `circuit.data`：门名取
`instruction.operation.name`，量子位取 `circuit.find_bit(q).index`，参数取
`[float(p) for p in instruction.operation.params]`。需要展开复合门时使用 SDK 的
decompose/transpile，并确认展开后的线路与原线路等价；不要把优化后的硬件线路与模型线路混称。
Qiskit 受控门的 `qubits` 顺序为控制位在前、目标位在后；不要排序该数组。
`params` 可选，提供时必须是有限实数数组（角度为弧度），不能提前四舍五入；未绑定符号参数不属于单次推理线路。

### 绘制要求

- SVG 按后端 `/api/infer.quantum.gates` 动态渲染，`data-circuit-source="api"`
- q0 在上、时间向右；同一量子位保持原门序，不根据 stage 重排。受控门用控制点和目标符号，未知多位门保留单个操作块与操作数顺序。
- 规范模板提供缩放、横向滚动、完整参数表及 SVG/JSON 导出；不要另造硬编码线路图。图中缩略参数不改变导出数据。
- 颜色走 CSS 变量（quantumPurple→`#BB79E1`、primary→`#1664FF`、cyan→`#00C7E7`、danger→`#FB4214`）

---

## 需求 4：算法流程（可点击 + 详情面板）

### 步骤条

N 步 = `grid-template-columns: repeat(N, 1fr)`，由 JS 动态设置，禁止 CSS 固定 repeat(4,1fr)。中间核心步骤加 `.flow-step core` 量子紫高亮。

### flow-detail DOM 强制子树

```html
<div class="flow-detail">
  <div class="flow-detail-title"></div>
  <div class="flow-detail-desc"></div>
  <div class="flow-detail-body">          <!-- grid: 1fr 1fr -->
    <div class="flow-metrics"></div>       <!-- 左: 该步骤独立运行时 metrics -->
    <div class="flow-viz"></div>           <!-- 右: 该步骤独立运行时 viz -->
  </div>
</div>
```

JS 数据优先级链（`showFlowDetail(idx, steps)`）：
1. `appResult.flow_details[step_idx]` — 运行时返回的独立 metrics/viz（**最准确**）
2. `method_steps[idx].metrics/viz` — 静态占位
3. **禁止所有步骤显示相同的通用占位**（用户报告"每步结果都一样"即因此）

### 每步骤必须配算法语义相关的结果

| 步骤位置 | VQE 语义 | QAOA 语义 | QNN 语义 |
|---------|---------|----------|---------|
| 步骤 0（数据输入） | 哈密顿量项数 / 轨道数 | 节点数 / 边数 / Ising 项 | 特征维度 / 类别数 |
| 步骤 1（特征编码） | UCCSD 单双激发数 | X 基态 + Ising ZZ 对 | ZZFeatureMap 层数 |
| 步骤 2（量子核心） | 线路深度 / 参数维度 | p 层深度 / 全连接 ZZ 对 | 参数化旋转 + CNOT 环形数 |
| 步骤 3（读出） | 能量期望值 / 迭代数 | 组合解 / 近似比 | FC 维度 / Softmax 输出 |

**禁止**把所有步骤的 metrics 都写成 `qubits / depth / backend` 的通用占位。

---

## API 合同（application.py 必须遵守）

**完整 schema 见 `assets/backend/main.py` 的 `_validate_info` / `_validate_result` 函数。以下是约束摘要**。

数值输入经框架校验后统一以有限 `float` 传给 `application.infer`；合法数字字符串
也会归一化，布尔值被拒绝。迭代次数等整数业务字段应检查有限性、
`value.is_integer()` 和业务范围，再转成 `int` 传给 SDK；不要用仅接受原始
`int` 类型的判断拒绝框架传来的 `100.0`。`fields[].step=1` 不能替代业务整数校验。

### `/api/info`（页面加载时获取）

| 字段 | 必填 | 双语 `_en` | 说明 |
|------|------|-----------|------|
| `title` | ✅ | ✅ 必须提供 `title_en` | 页面标题 |
| `description` | ✅ | ✅ 必须提供 `description_en` | 页面概述 |
| `scenario_summary` | ✅ | ✅ 必须提供 `scenario_summary_en` | 场景摘要（顶部说明栏） |
| `fields[]` | ✅ | ✅ 每个字段必须提供 `label_en` | 输入字段 `{id, label, label_en, min, max, step, default}` |
| `presets[]` | ✅ | ✅ 每个预设必须提供 `name_en` | 预设值，覆盖所有 field id |
| `method_steps[]` | ✅ | ✅ 每步必须提供 `title_en` + `detail_en` | 流程步骤 `{title, title_en, detail, detail_en}` |
| `metrics[]` | ✅ | ✅ 必须 `label_en` + `desc_en` | showcase 指标（≥4项），`value` 带单位 |
| `circuit` | ✅ 推荐 | — | 量子线路数据 `{qubits, depth, backend, gates[]}`，保留真实阶段，不补造门 |
| `scientific_boundary[]` | ✅ | ✅ 必须提供 `scientific_boundary_en[]` | 科学边界条件 |

> **铁约束：`/api/info` 必须支撑完整英文页面。** 页面一加载就会请求 `/api/info` 并渲染全部框架内容，
> 因此它返回的每一处可见文案都必须有真实英文版本：`title_en`、`description_en`、
> `scenario_summary_en`、`fields[].label_en`、`presets[].name_en`、`method_steps[].title_en` /
> `detail_en`、`metrics[].label_en` / `desc_en`、`scientific_boundary_en[]` 缺一不可。
> 这些英文**由 `backend/application.py` 的业务层提供**（框架模板只消费 `_en`、不做翻译）。
> 交付标准是：切换到 English 后整页不出现任何中文（门符号与 `id` 这类非文案字段除外）。
> 前端在缺少 `_en` 时会回退显示中文，所以"漏配 `_en`"等同于把中文泄漏到英文页面，属于不合格交付，
> 不能用"有中文兜底"来接受。

### `/api/infer`（点击 Run 后获取）

| 字段 | 必填 | 双语 `_en` | 说明 |
|------|------|-----------|------|
| `prediction` | ✅ | ✅ 必须见下方 | 5 种 kind（见下方） |
| `quantum.gates[].stage` | ✅ | — | 非空字符串，说明真实门所属阶段；无固定枚举 |
| `quantum.qubits/depth/backend/gates[]` | ✅ | — | 量子线路数据 |
| `flow_details[]` | ✅ | 可选（有则用） | 每步独立运行时 `{step_idx, metrics[], viz}` |
| `explanations[]` | ✅ | ✅ 必须 `explanations_en[]` | 解释文案（tipsBar 显示） |
| `boundary[]` | ✅ | ✅ 必须 `boundary_en[]` | 非空字符串数组（tipsBar 显示，缺失英文会残留中文） |
| `latency_ms` | ✅ | — | ≥0 |

> **铁约束：`/api/infer` 的业务文案同样必须能渲染英文。** 与 `/api/info` 一样，英文由
> `backend/application.py` 提供，模板只消费 `_en`：`prediction.label_en` /
> `score_semantics_en` / `scores[].label_en` / `unit_en`、`explanations_en[]`、`boundary_en[]`，
> 以及 VQE 的 `convergence.semantics_en` 等可读字段，全部必须配齐且与中文一一对应。
> 运行后切换到 English，结果卡、解释与边界提示仍出现中文即不合格。

### prediction 双语要求（所有 kind）

| 字段 | `_en` 版本 | 说明 |
|------|-----------|------|
| `label` | `label_en` | 主结果区大字显示（如 `"正常"` / `"Normal"`） |
| `score_semantics` | `score_semantics_en` | 主结果区小字 subtitle（如 `"置信度"` / `"Confidence"`） |
| `scores[].label` | `scores[].label_en` | 各指标标签（如 `"欺诈"` / `"Fraud"`） |

### prediction 5 种 kind 约束摘要

| kind | 适用算法 | 必填字段 | 主结果显示 |
|------|---------|---------|-----------|
| `classification` | QNN 分类 | `label` + `scores[]`(0-1展示权重) + `decision_value` + `score_semantics` | 分类标签（如 "Versicolor"） |
| `regression` | QNN 回归/QPE 相位 | `value` + `unit` + `normalized_value` + `score_semantics` | 数值 + 单位（如 "284.5 万元"） |
| `energy` | VQE 能量 | `value` + `unit` + `score_semantics` | 物理能量 + 单位，不伪造归一化值或概率 |
| `solution` | QAOA/Grover | `label`(比特串或解描述) + `value`(该解的原目标值) + `scores[]`(有限数值) + `score_semantics` | 离散解（比特串 "01010"） |
| `state` | 态层析/量子模拟 | `label`(量子态描述) + `scores[]` + `score_semantics` | 量子态描述（如 "\|ψ⟩ ≈ 0.92\|0⟩ + 0.38\|1⟩"） |

VQE 可在真实 `/api/infer` 响应加入 `convergence`：`unit` 必须与能量结果一致，
`semantics` 说明哈密顿量、活性空间和能量偏移约定；`points` 为 1--2000 个
`{evaluation, energy}` 原始回调记录（编号为递增正整数，能量必须有限），
`final_energy` 为最终参数独立复算且等于 `prediction.value`，可选
`reference_energy` 必须对应同一哈密顿量/粒子扇区/能量约定。官方页面直接绘制
实际曲线、参考线与最终点；不要把每次函数评估叫做优化迭代，不要把非单调原始
记录改成单调曲线。未提供记录时面板隐藏。量子线路使用同一绑定电路的真实门表。
末次回调可能是线搜索或有限差分评估，不保证等于优化器返回参数的能量；
不得要求 `points[-1].energy == final_energy`，也不得补造回调点来满足等式。
达到迭代上限时须如实说明，不能仅凭返回结果或误差低于某阈值就称优化已收敛。

若提供 `quantum.top_states`，每项使用 `{label, value}`，例如从 SDK 真实测量
分布映射为 `{label: state.bitstring, value: state.probability}`；不要把
`bitstring`/`probability` 当作框架字段，也不要编造没有执行的测量结果。

**铁约束**：分类、离散解和量子态使用 `label`，回归使用完整精度的 `value` 与独立单位；所有 kind 都应说明 `score_semantics`。`classification` 的 `scores.value` 必须 0-1 归一化，只有经过校准并有证据时才能称为概率，其他 kind 无此数值范围限制。主模型分数展示 `decision_value` 并使用对应 `score_semantics`，不得把 `scores[]` 展示权重当成原始决策值。

回归的 `prediction.interval` 是可选字段，仅当它包含两个有限数值且下界不大于上界时显示参考区间。缺失或非法区间不应阻断预测与线路展示；不得根据点预测编造置信区间，也不得把参考区间表述为已校准的不确定性。长小数和单位必须在卡片内换行，保留原始数值。

### Max-Cut 的可选图与划分

`/api/infer` 可返回 `graph`：`num_nodes` 为 2–32 整数，`edges` 为
`[source,target,weight]` 列表（编号从 0 开始，无自环或重复无向边，权重为
0–1000000 的有限数值），`partition` 按顶点号提供整数 0/1，`cut_value` 为
跨割边权重之和并等于 `prediction.value`。`partition_source` 必须为
`best_sample`、`most_probable_sample`、`exact`、`greedy` 之一，并忠实对应这次
运行的来源。框架检查这些关系后绘制二着色图，输入变化后将旧图标为待更新；
无图应用省略 `graph`，不显示空图或默认划分。最佳样本、最可能样本、期望割值
须分别命名，不能用找到一个最优样本来声称平均割值已达最优。

标准输入仍为数值字段，可用固定顶点数下的边权字段表示图；计划和页面必须说明
固定规模与范围，不得承诺模板不支持的任意 JSON 图编辑器。应用仍需使用选定 SDK
对实际输入执行有界 QAOA 求解；保存结果的重放必须明确标注。

---

## 算法类型参数参考

| 算法 | qubits | depth | 编码门 | 纠缠拓扑 | 读出 |
|------|--------|-------|--------|---------|------|
| VQE | 4–8 | 3-5 | UCCSD/H+RY | 相邻CZ | 能量估计 |
| QAOA | 12 | p=1-4 | X基态+IsingZZ | 全连接ZZ | 组合解码器 |
| QNN | 4-8 | 4 | ZZFeatureMap/H+RY | 环形CNOT | FC+Softmax |
| Grover | 6-10 | O(√N) | Hadamard | Oracle+Diffusion | 标准基 |
| QPE | 控制4-6+目标1 | 1 | H叠加+受控U^(2^k) | 无 | IQFT |
| 态层析 | 4-6 | 2 | 目标态制备 | 无 | 密度矩阵 |

showcase metrics 参考 fraud_detection.md 的 VQE/QAOA/QNN/Grover 四组 JSON 示例（能量+收敛/近似比+迭代数/量子准确率+经典对照/加速比+成功率）。

---

## 视觉规范（完整列表见 spec-source.md + tokens.md + checklist.md）

禁止：自定义色值/px/渐变/阴影（除 shadow-sm）、20/30/140/60/4/6/8 以外 px、实心图标、自创新组件、Regular 文字加粗、Emoji、非苹方/DINPro 字体、纯装饰分割线。

For bounded per-instance QAOA/VQE apps, set `get_info()["execution_kind"] = "solver"`. The frontend then hides the QML training record panel; inference apps retain its existing behavior.
