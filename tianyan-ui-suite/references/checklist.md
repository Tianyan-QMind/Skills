# 天衍 UI · 完整合规自检清单

> **每次输出代码后强制附带本清单**（规范第一部分·铁则5、第九部分·第四步），逐条核对，标记「符合 / 不符合」。
> 任何一项不符合，先修正代码再输出。来源：《0818UI skill更新》第十二部分。

## 一、视觉参数校验

- [ ] 色值匹配规范 HEX（primary `#1664FF` / primaryDeep `#4F9DF7` / linkBlue `#1F84FC` / danger `#FB4214` / cyan `#00C7E7` / textTitle `#020814` / textSub `#41464F` / textBody `#939AAB` / pageBg `#F4F7FC` / cardBg `#FFFFFF` / cardBgLight `#F3F7FF` / borderLine `#DCE0EB`），无近似值
- [ ] 拓展色（quantumEntangle1 `#ECF2FF` / quantumEntangle2 `#B5BFFF` / quantumPurple `#BB79E1` / quantumIndigo `#A58DF8` / quantumBlue `#4A86FF`）仅用于数据维度区分
- [ ] 字号/字重映射表严格一一对应：60/Bold、40/Bold、30/R、24/R、20/R、18/R、16/R、14/R
- [ ] 间距仅 20px / 30px（栅格），页面边距 140/60/140
- [ ] 圆角仅 4px(btn) / 6px(tag) / 8px(modal)
- [ ] **版心 1640px**（`max-w-1640`，强制）
- [ ] **主标题左对齐**（h1 左对齐）
- [ ] 字体仅苹方-简 + DINPro（无衬线）
- [ ] 图标仅 6 类（计算/任务/时钟/图表/设置/导出）、1.5px 线性、默认 primary、红点 danger
- [ ] 暗色变量仅在暗色模式启用（`#0A0E1A`/`#131A2E`/`#2A3457`/`#E8EDFF`/`#9AA6CF`/`--shadow-dark`）

## 二、代码规范校验

- [ ] 无硬编码色值（全部走 token 类，如 `bg-primary` / `text-textTitle` / `bg-cardBg`）
- [ ] 无硬编码 px 尺寸（样式仅调用预设变量名，铁则2）
- [ ] 使用 Tailwind/SCSS 变量（`tailwind.config.js` 主题变量）
- [ ] 复用原子白名单组件（Button/Tab/Input/Tag/StatusDot/Card/Pagination/Toast/Icon），无手写原生标签自定义样式
- [ ] 每行视觉样式有规范注释（铁则4）

## 三、品牌语义校验

- [ ] 量子精密、科技未来、可信计算、冷静理性、数据高密、低噪高效（整体气质符合）
- [ ] 确定性反馈：每一步操作明确 loading + 结果轻提示
- [ ] 数据可溯源：所有图表/数值区块带时间戳或状态标识（等待/运行中/已完成/失败）
- [ ] 静默氛围：仅功能指示性动效，无装饰性动效
- [ ] 低心理负荷：信息层级扁平，核心操作路径 ≤ 3 步
- [ ] 主视觉使用唯一 `data-testid="algorithm-showcase"`，结果来自真实 API 响应
- [ ] 量子线路使用唯一 `data-testid="quantum-circuit"`，并声明 `data-circuit-source` 为 `api`、`model-artifact` 或 `declared-static`
- [ ] 线路至少包含一个 `data-testid="quantum-wire"`；固定拓扑明确标注为结构示意而非单次运行轨迹
- [ ] 桌面和移动端均可访问主要操作、API 结果和量子线路；窄屏可横向滚动线路但不得隐藏

## 四、组件规范校验

- [ ] 按钮仅 4 类（primary/line/text/disabled）+ 卡片底部文字按钮（`text-ghost` hover `text-primary`，无边框）
- [ ] 按钮 max-width 128px（`max-w-btn`）、文字居中、loading 内置 spin16 + "提交中…"
- [ ] Tab 激活 primary 底白字 / 未激活 cardBg 底 textBody 灰字
- [ ] 输入框常态 borderLine / 聚焦 primary / 只读 pageBg 底；内边距 12×16
- [ ] Tag 圆角6、内边距 4×8、状态色映射正确（待提交=primary / 运行中=cyan / 已完成=primaryDeep / 失败=danger）
- [ ] 卡片圆角8、cardBg 底、内边距24、**卡内无边框**、仅 shadow-sm；焦点卡用 cardBgLight
- [ ] 状态指示器圆点直径 8px、语义色正确（在线=success / 离线=textBody / 运行中=cyan / 错误=danger）
- [ ] 分页仅数字 + 上一页/下一页，无跳转输入框
- [ ] 无自创组件、无异形卡片、无不规则圆角

## 五、禁止项校验（黑名单，触碰即违规）

- [ ] 无自定义色值/透明度/渐变/阴影/hover 以外动效（loading spin 的 `border-2`+`/40` 属封闭豁免；拓展色1 渐变对为规范内允许）
- [ ] 无规范数字（20/30/140/60/4/6/8）与组件常量（36/128/12/16/24/8/32/40/1）及具名 token 以外的 px 尺寸数字，无 Tailwind 任意值（封装组件内部 RTF 规定取值除外）
- [ ] 无实心图标/彩色杂图标/粗线条图标
- [ ] 无自创新组件/异形卡片/不规则圆角
- [ ] 无加粗规范里标注 Regular 的文字
- [ ] 无 emoji
- [ ] 无非 DINPro/苹方字体
- [ ] 无纯装饰性分割线（分割线必伴随内容分组意义）
- [ ] 页面内交互反馈方式 ≤ 3 种（统一 toast + loading + 状态 tag）

---

**符合性结论：**
- ✓ 全部符合规范 → 可交付
- ✗ 需在 X 项需修正（详见说明）→ 回到代码修正后重跑本清单
