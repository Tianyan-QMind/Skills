# 天衍 UI · 设计令牌（tokens）

> 完整令牌表。所有取值与《0818UI skill更新》（天衍平台设计规范 2.0）色值唯一列举 100% 一致，禁止近似。
> 令牌名即 Tailwind 类名后缀（规范原文命名，直接作为类名使用，无需二次映射）。

## 1. 颜色（HEX 唯一枚举，规范第四部分）

### 主色系
| 令牌 | HEX | Tailwind 类 | 用途 |
|---|---|---|---|
| `primary` | `#1664FF` | `bg-primary` / `text-primary` | 主色·量子蓝（主按钮、激活态） |
| `primaryDeep` | `#4F9DF7` | `bg-primaryDeep` | 深蓝辅助·量子深空（已完成态） |
| `linkBlue` | `#1F84FC` | `text-linkBlue` | 链接蓝·量子跃迁（文字跳转按钮） |
| `danger` | `#FB4214` | `bg-danger` | 危险红·量子错误（失败态） |
| `cyan` | `#00C7E7` | `bg-cyan` | 浅青辅助·量子相干（运行中态） |

### 文字色系
| 令牌 | HEX | Tailwind 类 | 用途 |
|---|---|---|---|
| `textTitle` | `#020814` | `text-textTitle` | 标题黑·量子黑体 |
| `textSub` | `#41464F` | `text-textSub` | 次要文字·量子灰 |
| `textBody` | `#939AAB` | `text-textBody` | 正文浅灰·量子雾灰 |

### 背景/边框
| 令牌 | HEX | Tailwind 类 | 用途 |
|---|---|---|---|
| `pageBg` | `#F4F7FC` | `bg-pageBg` | 页面背景·量子真空 |
| `cardBg` | `#FFFFFF` | `bg-cardBg` | 卡片白底·量子基态 |
| `cardBgLight` | `#F3F7FF` | `bg-cardBgLight` | 卡片浅蓝背景·量子激发态（焦点卡） |
| `borderLine` | `#DCE0EB` | `border-borderLine` | 边框·量子势垒 |

### 拓展色（规范第四部分·拓展色）
| 令牌 | HEX | Tailwind 类 | 用途 |
|---|---|---|---|
| `quantumEntangle1` | `#ECF2FF` | `bg-quantumEntangle1` | 量子纠缠浅（数据渐变起点 / Tag 待提交底） |
| `quantumEntangle2` | `#B5BFFF` | `bg-quantumEntangle2` | 量子纠缠浅（数据渐变终点） |
| `quantumPurple` | `#BB79E1` | `bg-quantumPurple` | 量子紫（数据维度区分） |
| `quantumIndigo` | `#A58DF8` | `bg-quantumIndigo` | 量子靛（数据维度区分） |
| `quantumBlue` | `#4A86FF` | `bg-quantumBlue` | 量子耀蓝（数据维度区分） |

> 拓展色1（`quantumEntangle1` → `quantumEntangle2`：`#ECF2FF → #B5BFFF`）为规范内唯一渐变对，仅限有明确数据语义的数据渐变场景。

### 辅助语义色（规范第六/七部分出现）
| 令牌 | HEX | Tailwind 类 | 用途 |
|---|---|---|---|
| `success` | `#34C759` | `bg-success` | 操作成功 toast、在线状态圆点 |
| `ghost` | `#7A8391` | `text-ghost` | 卡片底部文字按钮，hover→`primary` |

## 2. 暗色模式（天衍夜间量子态，规范第四部分·暗色变量）

> 规范以 `--*-dark` CSS 变量组定义暗色令牌，"暗色模式时才启用此变量组"。
> 配置中同时以 `dark` 颜色对象提供静态暗色类（`bg-dark-bg` / `bg-dark-card` / `border-dark-border` / `text-dark-textPrimary` / `text-dark-textSecondary`），二者取值一致。

| 暗色变量 | HEX | 对应白天令牌 |
|---|---|---|
| `--bg-dark` / `dark.bg` | `#0A0E1A` | `pageBg` |
| `--card-dark` / `dark.card` | `#131A2E` | `cardBg` |
| `--border-dark` / `dark.border` | `#2A3457` | `borderLine` |
| `--text-primary-dark` / `dark.textPrimary` | `#E8EDFF` | `textTitle` |
| `--text-secondary-dark` / `dark.textSecondary` | `#9AA6CF` | `textSub` / `textBody` |
| `--shadow-dark` | `0 8px 32px rgba(0,0,0,0.6)` | `shadow-dark` |

> 白天模式必须使用上方 HEX；暗色模式才启用暗色覆盖组。

## 3. 字号 + 字重绑定映射（规范第五部分，一一对应，禁止混用）

| 令牌 | px | 字重 | Tailwind 类 | 用途 |
|---|---|---|---|---|
| `banner` | 60 | Bold | `text-banner` | Banner 大标题（量子计算主视觉） |
| `h1` | 40 | Bold | `text-h1` | 一级页面标题（任务中心/实验列表） |
| `h2` | 30 | Regular | `text-h2` | 二级标题、数据数值（量子比特数/保真度） |
| `h3` | 24 | Regular | `text-h3` | 三级板块标题（任务参数/运行日志） |
| `subhead` | 20 | Regular | `text-subhead` | 小标题说明（量子线路概览） |
| `content` | 18 | Regular | `text-content` | 大段正文（算法描述/文档） |
| `minor` | 16 | Regular | `text-minor` | 辅助次级文字（时间戳/标签说明） |
| `tip` | 14 | Regular | `text-tip` | 表格、备注、小字（状态角标/阈值说明） |

> 字号即字重，禁止再叠加 `font-bold` 修改 Regular 字样。

## 4. 几何令牌（规范第三部分，唯一允许的尺寸）

| 类别 | 值 | Tailwind 类 | 说明 |
|---|---|---|---|
| 栅格间距 | `20px` / `30px` | `gap-20` / `gap-30` / `p-20` / `p-30` | 其余栅格间距全部禁用 |
| 页面边距 | 左右 `140px` / 顶 `60px` / 底 `140px` | `px-page-x pt-page-top pb-page-bottom` | 1920px 基准画布 |
| **页面版心** | **`1640px`** | `max-w-1640` | **强制！必须严格遵守（规范第三部分）** |
| 圆角·按钮 | `4px` | `rounded-btn` | btn |
| 圆角·Tag | `6px` | `rounded-tag` | tag |
| 圆角·弹窗卡片 | `8px` | `rounded-modal` | modal |
| 侧栏宽（技能补充） | `300px` | `w-aside` | 识别/工具页左输入区 |
| 居中面板宽（技能补充） | `420px` | `w-panel` | 登录/表单页 |

### 组件常量（规范第六部分，唯一允许的组件尺寸）
| 组件 | 常量 | 说明 |
|---|---|---|
| 按钮 | 高 `36px`(`h-9`)、max-width `128px`(`max-w-btn`)、文字居中 | 规范 6.1 |
| 输入框 | 内边距 `12px 16px`(`px-4 py-3`)、高 `40px`(`h-10`) | 规范 6.3 |
| 卡片 | 内边距 `24px`(`p-6`)、无内部边框 | 规范 6.6 |
| Tag | 内边距 `4px 8px`(`py-1 px-2`) | 规范 6.5 |
| 状态圆点 | 直径 `8px`(`w-2 h-2`) | 规范 6.7 |
| 按钮 loading | 内置 spin `16px`(`w-4 h-4`) | 规范第七部分 |
| 边框线 | 宽 `1px`(`border`) | 默认 |

> **封闭豁免表**（仅限白名单组件内部使用，布局中禁止）：
> - `rounded-full`：仅圆形元素——状态圆点、loading spin；
> - `border-2` + 透明度 `/40`：仅 loading spin 外圈（`border-2 border-white/40 border-t-white`）这一处；
> - 其余任何非规范 px 数字一律禁止：要么属于上表常量，要么抽为 tailwind.config.js 里的具名 token 后再用。

## 5. 字体（规范第三部分·字体族）
- 中文：苹方-简 `PingFang SC`
- 英文/数字：`DINPro`（无衬线）
- 无衬线体系，禁止其他字体
- Tailwind：`font-sans`（已含 `PingFang SC` + `DINPro`）

## 6. 图标（规范 6.4）
- 线型：统一 `1.5px` 线性轮廓
- 默认颜色：`primary`
- 状态提示红点：`danger`
- 允许图标库：仅限 **计算 / 任务 / 时钟 / 图表 / 设置 / 导出** 6 类

---

## 完整 tailwind.config.js（固定输出第一步，规范第九部分·第一步）

> 与《0818UI skill更新》第十一部分 11.1 一致；页面边距与版心令牌（`page-x/page-top/page-bottom/1640`）按规范第三部分布局参数补入 `extend`，以满足铁则2（样式仅调用预设变量名，禁止硬编码 px）。

```js
/** ============================================================
 * tailwind.config.js —— 天衍量子云平台主题配置
 * 依据《0818UI skill更新》第三~五部分，含暗色变量。禁止改值。
 * ============================================================ */
module.exports = {
  content: ['./src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      // 色值 - 来源：第四部分
      colors: {
        primary: '#1664FF',
        primaryDeep: '#4F9DF7',
        linkBlue: '#1F84FC',
        danger: '#FB4214',
        cyan: '#00C7E7',
        textTitle: '#020814',
        textSub: '#41464F',
        textBody: '#939AAB',
        pageBg: '#F4F7FC',
        cardBg: '#FFFFFF',
        cardBgLight: '#F3F7FF',
        borderLine: '#DCE0EB',
        quantumEntangle1: '#ECF2FF',   // 拓展色·量子纠缠浅
        quantumEntangle2: '#B5BFFF',   // 拓展色·量子纠缠浅（渐变终点）
        quantumPurple: '#BB79E1',
        quantumIndigo: '#A58DF8',
        quantumBlue: '#4A86FF',
        success: '#34C759',            // 操作成功（规范第七部分）
        ghost: '#7A8391',              // 卡片底部文字按钮（规范6.1）
        // 暗色模式 - 来源：第三部分·暗色变量
        dark: {
          bg: '#0A0E1A',
          card: '#131A2E',
          border: '#2A3457',
          textPrimary: '#E8EDFF',
          textSecondary: '#9AA6CF',
        },
      },
      // 字号 - 来源：第五部分
      fontSize: {
        banner: ['60px', { fontWeight: '700' }],
        h1: ['40px', { fontWeight: '700' }],
        h2: ['30px', { fontWeight: '400' }],
        h3: ['24px', { fontWeight: '400' }],
        subhead: ['20px', { fontWeight: '400' }],
        content: ['18px', { fontWeight: '400' }],
        minor: ['16px', { fontWeight: '400' }],
        tip: ['14px', { fontWeight: '400' }],
      },
      // 圆角 - 来源：第三部分
      borderRadius: {
        btn: '4px',
        tag: '6px',
        modal: '8px',
      },
      // 间距 - 来源：第三部分（栅格 20/30 + 页面边距 140/60/140）
      spacing: {
        '20': '20px',
        '30': '30px',
        '60': '60px',          // 页面顶部边距（规范3·布局参数）
        '140': '140px',        // 页面左右/底部边距（规范3·布局参数）
        'page-x': '140px',     // 页面左右边距
        'page-top': '60px',    // 页面顶部边距
        'page-bottom': '140px',// 页面底部边距
      },
      // 版心 - 来源：第三部分（强制 1640px）
      maxWidth: {
        '1640': '1640px',
        btn: '128px',          // 按钮最大宽（规范6.1）
      },
      // 布局宽度 - 技能补充（规范未规定侧栏/面板宽，抽为具名 token 避免任意值）
      width: {
        aside: '300px',        // 侧栏宽（识别/工具页左输入区）
        panel: '420px',        // 居中面板宽（登录/表单页）
      },
      // 阴影 - 仅允许 shadow-sm
      boxShadow: {
        'sm': '0 1px 3px rgba(0,0,0,0.06)',
        'dark': '0 8px 32px rgba(0,0,0,0.6)',
      },
      // 字体 - 来源：第三部分
      fontFamily: {
        sans: ['PingFang SC', '苹方-简', 'DINPro', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
```

## 暗色模式 CSS 变量（规范第四部分·暗色变量）

> 规范原文以 `--*-dark` 变量组定义暗色令牌，暗色模式时启用。可配合 `<html class="dark">` 切换覆盖白天令牌。

```css
/* 暗色模式专属变量（天衍夜间量子态，切换 .dark 时启用） */
.dark {
  --bg-dark: #0A0E1A;
  --card-dark: #131A2E;
  --border-dark: #2A3457;
  --text-primary-dark: #E8EDFF;
  --text-secondary-dark: #9AA6CF;
  --shadow-dark: 0 8px 32px rgba(0,0,0,0.6);
}
```
> 白天模式必须使用上方 HEX；暗色模式才启用此变量组。
