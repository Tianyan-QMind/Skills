<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>量子增强 QML 应用 | 天衍量子云平台</title>
<style>
/* ===== rem 适配 ===== */
html { font-size: 100px; }
@media (max-width: 1600px) { html { font-size: 83px; } }
@media (max-width: 1440px) { html { font-size: 75px; } }
@media (max-width: 1280px) { html { font-size: 66px; } }

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; }

/* ===== 主题变量（天衍规范：色值唯一枚举 HEX完全匹配） ===== */
:root {
  /* 主色系 */
  --primary: #1664FF;           /* 量子蓝 */
  --primary-deep: #4F9DF7;      /* 量子深空 深蓝辅助 */
  --link-blue: #1F84FC;         /* 量子跃迁 链接蓝 */
  --danger: #FB4214;            /* 量子错误 危险红 */
  --cyan: #00C7E7;              /* 量子相干 浅青辅助 */
  /* 文字系 */
  --text-title: #020814;        /* 量子黑体 文字标题黑 */
  --text-sub: #41464F;          /* 量子灰 次要文字灰 */
  --text-body: #939AAB;         /* 量子雾灰 正文浅灰 */
  /* 背景系 */
  --page-bg: #F4F7FC;           /* 量子真空 页面背景 */
  --card-bg: #FFFFFF;           /* 量子基态 卡片白底 */
  --card-bg-light: #F3F7FF;     /* 量子激发态 卡片浅蓝 */
  --border-line: #DCE0EB;       /* 量子势垒 边框 */
  /* 拓展颜色（规范定义） */
  --entangle-light: #ECF2FF;    /* 量子纠缠浅 */
  --entangle-deep: #B5BFFF;     /* 量子纠缠深 */
  --quantum-purple: #BB79E1;    /* 量子紫 */
  --quantum-indigo: #A58DF8;    /* 量子靛 */
  --quantum-blue-bright: #4A86FF; /* 量子耀蓝 */
}

body {
  font-family: "PingFang SC", "DIN Pro", -apple-system, sans-serif;
  color: var(--text-title);
  background-color: var(--page-bg);
  min-height: 100vh;
  font-size: max(14px, .14rem);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
button { font-family: inherit; cursor: pointer; }

/* ===== 顶部说明栏 ===== */
.page-header {
  width: 14.4rem;                     /* 与 .main 同宽 */
  margin: 0 auto;                     /* 与 .main 居中对齐 */
  background-color: var(--entangle-light);  /* 规范拓展颜色1 */
  padding: .24rem .32rem;
  color: var(--text-title);
  font-size: max(14px, .16rem);                  /* textContent */
  line-height: .28rem;
  text-indent: 2em;
  border-radius: .08rem;              /* modal 圆角 */
}

/* ===== 主容器 ===== */
.main {
  width: 14.4rem;
  margin: .2rem auto 0;               /* 与说明栏间距 20px(base20) */
  padding: .32rem 0 .64rem;
}

/* ===== 页面标题区 ===== */
.title-section {
  text-align: center;
  margin: .32rem auto .32rem;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: .24rem;
}
.title-row > div:first-child { text-align: left; }
.title-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: .16rem;
  flex-shrink: 0;
}
.lang-switch {
  display: inline-flex;
  border: .01rem solid var(--border-line);
  border-radius: .04rem;              /* btn 圆角 */
  overflow: hidden;
}
.lang-btn {
  padding: .04rem .16rem;
  font-size: max(14px, .14rem);                   /* textTip */
  font-weight: 400;
  border: none;
  background: var(--card-bg);
  color: var(--text-sub);
  cursor: pointer;
  transition: background-color .2s, color .2s;
}
.lang-btn:hover { background: var(--entangle-light); color: var(--primary); }
.lang-btn.active {
  background: var(--primary);
  color: #fff;
}
.title-section h1 {
  font-size: .40rem;        /* textH1 */
  font-weight: 700;
  color: var(--text-title);
  margin: 0 0 .12rem;
  letter-spacing: 0;
}
.title-bar {
  background: var(--primary);
  width: .96rem;
  height: .04rem;
  border-radius: 9.99rem;
  margin: 0 auto .16rem;
}
.subtitle {
  font-size: .18rem;        /* textContent */
  color: var(--text-sub);
  margin-bottom: .2rem;
  overflow-wrap: anywhere;
}
.service-status {
  display: inline-flex;
  align-items: center;
  gap: .08rem;
  padding: .04rem .12rem;
  background: var(--card-bg-light);    /* 量子激发态 卡片浅蓝 */
  border: .01rem solid var(--cyan);    /* 规范 cyan 运行中态 */
  border-radius: .06rem;              /* tag 圆角 */
  font-size: max(14px, .14rem);                   /* textTip */
  color: var(--cyan);                  /* 规范 cyan 运行中态 */
}
.status-dot {
  width: .08rem;
  height: .08rem;
  border-radius: 50%;
  background: var(--cyan);             /* 规范 cyan 运行中态 */
}

/* ===== 卡片通用 ===== */
.card {
  background: var(--card-bg);
  border-radius: .08rem;     /* modal */
  padding: .24rem;
  /* 规范：卡片仅允许 shadow-sm，禁止自定义阴影 */
}

/* ===== 技术标题 ===== */
.section-title {
  border-bottom: .01rem solid var(--border-line);
  margin-bottom: .2rem;
  padding-bottom: .12rem;
  position: relative;
  display: flex;
  align-items: center;
}
.section-title::after {
  content: "";
  background: var(--primary);
  width: .48rem;
  height: .02rem;
  position: absolute;
  bottom: -.01rem;
  left: 0;
}
.section-title-text {
  font-size: .24rem;         /* textH3:24px Regular */
  font-weight: 400;          /* 规范 textH3 绑定 Regular，禁止加粗 */
  color: var(--text-title);
}
.section-title-time {
  margin-left: auto;
  font-size: max(14px, .14rem);
  color: var(--text-body);
}

/* ===== 顶部交互区 ===== */
.top-grid {
  display: flex;
  gap: .2rem;
  align-items: stretch;
  justify-content: space-between;
}
.input-panel {
  width: 6.8rem;
  display: flex;
  flex-direction: column;
}
.result-panel {
  width: 7.4rem;
  display: flex;
  flex-direction: column;
}

.input-card {
  width: 100%;
  background: var(--card-bg);
  border-radius: .08rem;
  padding: .28rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.input-card > .section-title { border-bottom: 0; margin-bottom: .16rem; padding-bottom: 0; }
.input-card > .section-title::after { display: none; }

/* ===== 输入表单 ===== */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: .16rem .24rem;
  margin-bottom: .2rem;
}
.form-item {
  display: flex;
  flex-direction: column;
  gap: .08rem;
}
.form-label {
  font-size: max(14px, .14rem);
  color: var(--text-sub);
  font-weight: 400;
}
.form-input {
  width: 100%;
  height: .4rem;
  padding: .12rem .16rem;
  border: .01rem solid var(--border-line);
  border-radius: .04rem;
  font-size: max(14px, .14rem);
  color: var(--text-title);
  background: var(--card-bg);
  transition: border-color .2s;
  font-family: inherit;
}
.form-input:focus {
  outline: none;
  border-color: var(--primary);
}
.form-input:read-only {
  background: var(--page-bg);
}
.form-select {
  width: 100%;
  height: .4rem;
  padding: 0 .16rem;
  border: .01rem solid var(--border-line);
  border-radius: .04rem;
  font-size: max(14px, .14rem);
  color: var(--text-title);
  background: var(--card-bg);
  font-family: inherit;
}

/* ===== 按钮组 ===== */
.action-row {
  display: flex;
  gap: .16rem;
  margin-top: auto;
}
.btn-primary {
  flex: 1;
  height: .4rem;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: .04rem;          /* btn 圆角 */
  font-size: max(14px, .14rem);              /* textTip */
  font-weight: 400;               /* 规范未标注按钮加粗，统一 Regular */
  transition: background .2s;     /* hover 功能指示性动效，允许 */
  min-width: 0;
}
.btn-primary:hover { background: var(--primary-deep); }  /* 规范：深蓝辅助 */
.btn-line {
  flex: 1;
  height: .4rem;
  background: var(--card-bg);
  color: var(--primary);
  border: .01rem solid var(--primary);
  border-radius: .04rem;          /* btn 圆角 */
  font-size: max(14px, .14rem);              /* textTip */
  font-weight: 400;               /* 规范未标注按钮加粗，统一 Regular */
  transition: all .2s;           /* hover 功能指示性动效，允许 */
  min-width: 0;
}
.btn-line:hover { background: var(--entangle-light); }  /* 规范拓展颜色1 */

/* ===== 结果展示 ===== */
.result-card {
  background: var(--card-bg);         /* 量子基态 卡片白底 */
  border-radius: .08rem;              /* modal */
  padding: .28rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.result-card > .section-title { border-bottom: 0; margin-bottom: .16rem; padding-bottom: 0; }
.result-card > .section-title::after { display: none; }

.risk-display {
  display: flex;
  gap: .2rem;
  align-items: stretch;
}
.risk-main {
  flex: 1;
  background: var(--card-bg);         /* 量子基态 卡片白底（禁止渐变） */
  border: .02rem solid var(--danger); /* 规范 danger 高风险态 */
  border-radius: .08rem;              /* modal */
  padding: .32rem;
  text-align: center;
}
.risk-main.low {
  border-color: var(--primary-deep);  /* 规范 深蓝辅助 低风险态 */
}
.risk-main.medium {
  border-color: var(--cyan);          /* 规范 cyan 中风险态 */
}
.risk-score {
  font-family: "DIN Pro", sans-serif;
  font-size: clamp(20px, .42rem, 32px);
  overflow-wrap: anywhere;
  font-weight: 700;
  color: var(--danger);               /* 规范 danger 高风险态 */
  line-height: 1;
  margin-bottom: .12rem;
}
.risk-main.low .risk-score { color: var(--primary-deep); }  /* 规范 深蓝辅助 */
.risk-main.medium .risk-score { color: var(--cyan); }       /* 规范 cyan */
.risk-level {
  font-size: max(14px, .16rem);         /* textMinor:16px Regular */
  font-weight: 400;          /* 规范禁止加粗 */
  color: var(--text-title);
}
.risk-tags {
  display: flex;
  gap: .08rem;
  justify-content: center;
  margin-top: .16rem;
  flex-wrap: wrap;
}
.tag {
  padding: .04rem .08rem;
  border-radius: .06rem;              /* tag 圆角 */
  font-size: max(14px, .14rem);                   /* textTip */
  font-weight: 400;
}
.tag-danger { background: var(--card-bg); color: var(--danger); border: .01rem solid var(--danger); }
.tag-cyan { background: var(--entangle-light); color: var(--cyan); }
.tag-primary { background: var(--entangle-light); color: var(--primary); }
.tag-success { background: var(--card-bg-light); color: var(--primary-deep); }  /* 规范：已完成态 */

/* ===== 量子 vs 经典对比 ===== */
.compare-panel {
  width: 3rem;
  display: flex;
  flex-direction: column;
  gap: .16rem;
}
.compare-box {
  background: var(--card-bg);          /* 量子基态 卡片白底 */
  border: .01rem solid var(--border-line);
  border-radius: .06rem;              /* tag 圆角 */
  padding: .2rem;
  text-align: center;
}
.compare-box.quantum {
  border-color: var(--quantum-purple); /* 规范拓展颜色2 量子紫 */
  background: var(--card-bg-light);     /* 量子激发态 卡片浅蓝 */
}
.compare-box.classical {
  border-color: var(--primary);         /* 规范 量子蓝 */
  background: var(--entangle-light);    /* 规范拓展颜色1 */
}
.compare-label {
  font-size: max(14px, .14rem);
  color: var(--text-sub);
  margin-bottom: .08rem;
}
.compare-value {
  font-family: "DIN Pro", sans-serif;
  font-size: .24rem;                  /* textH3:24px Regular */
  font-weight: 400;                   /* 规范 textH3 绑定 Regular */
}
.compare-box.quantum .compare-value { color: var(--quantum-purple); }  /* 规范拓展颜色2 */
.compare-box.classical .compare-value { color: var(--primary); }       /* 规范 量子蓝 */
#scoreMeaning { font-size: max(14px, .14rem); line-height: 1.5; overflow-wrap: anywhere; }

/* ===== Tips 提示 ===== */
.tips-bar {
  display: flex;
  align-items: center;
  gap: .08rem;
  margin-top: .16rem;
  padding: .12rem .16rem;
  background: var(--entangle-light);   /* 规范拓展颜色1 */
  border-radius: .04rem;              /* btn 圆角 */
  font-size: max(14px, .14rem);                   /* textTip */
  color: var(--text-sub);
}
.tips-bar b { color: var(--primary); font-weight: 400; }  /* 规范禁止加粗 Regular 文字 */

/* ===== 算法展示区 ===== */
.showcase-section {
  margin-top: .4rem;
}
.showcase-card {
  background: var(--card-bg);
  border-radius: .08rem;
  padding: .28rem;
}
.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: .2rem;
  align-items: center;
}
.showcase-metric {
  background: var(--card-bg-light);
  border-radius: .06rem;
  padding: .2rem;
  text-align: center;
  min-width: 0;
  overflow-wrap: anywhere;
}
.showcase-metric .metric-value {
  font-family: "DIN Pro", sans-serif;
  font-size: .30rem;                   /* textH2:30px Regular 数据数值 */
  font-weight: 400;                    /* 规范 textH2 绑定 Regular */
  color: var(--primary);
  line-height: 1.3;
}
.showcase-metric.quantum .metric-value { color: var(--quantum-purple); }  /* 规范拓展颜色2 量子紫 */
.showcase-metric.danger .metric-value { color: var(--danger); }          /* 规范 量子错误 危险红 */
.showcase-metric.success .metric-value { color: var(--primary-deep); }   /* 规范 深蓝辅助 */
.showcase-metric .metric-label {
  font-size: max(14px, .14rem);
  color: var(--text-sub);
  margin-top: .08rem;
}
.showcase-desc {
  font-size: max(14px, .16rem);
  color: var(--text-sub);
  line-height: 1.8;
}
.showcase-desc b { color: var(--text-title); font-weight: 400; }  /* 规范 textContent 绑定 Regular */

/* ===== 量子线路区 ===== */
.circuit-section {
  margin-top: .4rem;
}
.circuit-card {
  background: var(--card-bg);
  border-radius: .08rem;
  padding: .28rem;
}
.circuit-source-hint {
  display: inline-flex;
  align-items: center;
  gap: .08rem;
  padding: .04rem .12rem;
  background: var(--card-bg-light);     /* 量子激发态 卡片浅蓝 */
  border: .01rem solid var(--cyan);    /* 规范 cyan */
  border-radius: .04rem;               /* btn 圆角 */
  font-size: max(14px, .14rem);                   /* textTip:14px 规范最小字号 */
  color: var(--cyan);                  /* 规范 cyan */
  margin-bottom: .2rem;
}

/* 量子线路 SVG */
.circuit-container {
  overflow-x: auto;
  padding-bottom: .16rem;
}
.circuit-svg {
  min-width: 0;
  max-width: none;
  height: auto;
  display: block;
}
.main, .input-panel, .result-panel, .circuit-card { min-width: 0; }
.section-title, .circuit-source-hint { flex-wrap: wrap; overflow-wrap: anywhere; }
.circuit-toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 16px; font-size: 14px; }
.circuit-toolbar button, .circuit-toolbar select { padding: 6px 12px; border: 1px solid var(--primary); border-radius: 4px; background: var(--card-bg); color: var(--primary); font: inherit; }
.circuit-toolbar button:disabled { opacity: .5; }
.circuit-details { font-size: 14px; margin-top: 12px; }
.circuit-details summary { cursor: pointer; }
.circuit-table-scroll { overflow: auto; max-height: 320px; }
.circuit-details table { width: 100%; border-collapse: collapse; }
.circuit-details th, .circuit-details td { padding: 8px; text-align: left; border-bottom: 1px solid var(--border-line); overflow-wrap: anywhere; }
[data-inference-state="stale"] { opacity: .65; }
.graph-section { margin-top: .4rem; }
.convergence-section { margin-top: .4rem; }
.convergence-card { background: var(--card-bg); border-radius: .08rem; padding: .28rem; overflow: hidden; }
.convergence-chart { overflow-x: auto; }
.convergence-card svg { display: block; width: 100%; min-width: 640px; min-height: 240px; }
.convergence-card p { overflow-wrap: anywhere; line-height: 1.7; }
.convergence-table { max-height: 320px; overflow: auto; }
.convergence-table table { width: 100%; text-align: left; border-collapse: collapse; }
.convergence-table td, .convergence-table th { padding: 6px 12px; border-bottom: 1px solid var(--border-line); }
.graph-card { background: var(--card-bg); border-radius: .08rem; padding: .28rem; }
.graph-card svg { display: block; width: 100%; max-width: 560px; margin: auto; }
.graph-card p { overflow-wrap: anywhere; line-height: 1.7; }
.graph-legend { color: var(--text-sub); }

/* ===== 方法流程区 ===== */
.flow-section {
  margin-top: .4rem;
}
.flow-card {
  background: var(--card-bg);
  border-radius: .08rem;
  padding: .28rem;
}
.flow-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: .16rem;
}
.flow-step {
  position: relative;
  background: var(--page-bg);
  border: .01rem solid var(--border-line);
  border-radius: .08rem;
  padding: .2rem;
  text-align: center;
  min-height: 1.6rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .08rem;
}
.flow-step.core {
  /* 默认态与其他步骤完全一致，不提前染色 */
}
.flow-step.active {
  background: var(--entangle-light);
  border-color: var(--primary);
}
.flow-step.active .flow-step-icon { background: var(--primary); }
.flow-step.core.active {
  background: var(--entangle-light);
  border-color: var(--quantum-purple);
}
.flow-step.core.active .flow-step-icon { background: var(--quantum-purple); }
.flow-step-arrow {
  position: absolute;
  right: -.16rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: .24rem;
  color: var(--border-line);
  z-index: 1;
  background: var(--card-bg);
  padding: 0 .04rem;
}
.flow-step:last-child .flow-step-arrow { display: none; }
.flow-step-icon {
  width: .4rem;
  height: .4rem;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: max(14px, .16rem);
}
/* core 步骤默认态图标颜色与其他步骤一致，激活后再由 .flow-step.core.active .flow-step-icon 覆盖 */
.flow-step-name {
  font-size: max(14px, .16rem);         /* textMinor:16px Regular */
  font-weight: 400;          /* 规范禁止加粗 */
  color: var(--text-title);
}
.flow-step-desc {
  font-size: max(14px, .14rem);
  color: var(--text-body);
  line-height: 1.5;
}

/* ===== 流程步骤详情面板 ===== */
.flow-detail {
  display: none;               /* 默认隐藏，点击步骤才显示 */
  margin-top: .24rem;
  background: var(--page-bg);
  border-radius: .08rem;
  padding: .28rem;
  border: .01rem solid var(--border-line);
}
.flow-detail-title {
  font-size: .18rem;
  color: var(--text-title);
  font-weight: 400;
  margin-bottom: .16rem;
}
.flow-detail-desc {
  font-size: max(14px, .14rem);
  color: var(--text-body);
  line-height: 1.6;
  margin-bottom: .2rem;
}
.flow-detail-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .32rem;
  align-items: start;
}
.flow-metrics {
  display: flex;
  gap: .2rem;
  flex-wrap: wrap;
}
.flow-metric {
  background: var(--card-bg);
  border: .01rem solid var(--border-line);
  border-radius: .08rem;
  padding: .16rem .2rem;
  text-align: center;
  min-width: 1.2rem;
}
.flow-metric-value {
  font-size: .24rem;
  font-family: DIN Pro, monospace;
  color: var(--primary-deep);
  font-weight: 400;
}
.flow-metric-label {
  font-size: .12rem;
  color: var(--text-sub);
  margin-top: .04rem;
}
.flow-viz {
  background: var(--card-bg);
  border: .01rem solid var(--border-line);
  border-radius: .08rem;
  padding: .2rem;
  min-height: 1.8rem;
}
.feature-vector {
  display: flex;
  gap: .02rem;
  align-items: flex-end;
  height: .8rem;
  justify-content: center;
}
.feature-bar {
  width: .08rem;
  background: var(--primary);
  border-radius: .02rem .02rem 0 0;
  min-height: .04rem;
}
.feature-bar.highlight {
  background: var(--quantum-purple);
}
@media (max-width: 900px) {
  .flow-detail-body { grid-template-columns: 1fr; }
}

/* ===== 历史告警区 ===== */
.history-section {
  margin-top: .4rem;
}
.history-card {
  background: var(--card-bg);
  border-radius: .08rem;
  padding: .28rem;
}
.history-table {
  width: 100%;
  border-collapse: collapse;
}
.history-table th {
  font-size: max(14px, .14rem);          /* textTip:14px Regular */
  color: var(--text-sub);
  font-weight: 400;           /* 规范禁止加粗 */
  padding: .12rem .16rem;
  text-align: left;
  border-bottom: .01rem solid var(--border-line);
  background: var(--page-bg);
}
.history-table td {
  font-size: max(14px, .14rem);
  color: var(--text-title);
  padding: .12rem .16rem;
  border-bottom: .01rem solid var(--border-line);
}
.history-table tbody tr:hover {
  background: var(--card-bg-light);
}
.amount-cell {
  font-family: "DIN Pro", sans-serif;
  font-weight: 400;  /* 规范 textTip 绑定 Regular */
}
.amount-cell.fraud { color: var(--danger); }  /* 规范 danger */
.amount-cell.normal { color: var(--primary-deep); }  /* 规范 primary-deep 已完成态 */

.training-section { margin-top: .4rem; }
.training-card { background: var(--card-bg); border-radius: .08rem; padding: .28rem; }
.training-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: .3rem; margin-top: .2rem; }
.training-plot { min-width: 0; overflow-x: auto; }
.training-plot svg { display: block; width: 100%; }
.training-plot h3 { font-size: max(14px, .16rem); font-weight: 400; }
.training-note { color: var(--text-sub); overflow-wrap: anywhere; }
.training-legend { display: flex; flex-wrap: wrap; gap: .2rem; margin-top: .12rem; }
.training-legend .actual { color: var(--primary-deep); }
.training-legend .best, .training-legend .trained { color: var(--primary); }
.training-table { overflow-x: auto; margin-top: .2rem; }
.training-table table { width: 100%; text-align: left; border-collapse: collapse; }
.training-table td, .training-table th { padding: .08rem; border-bottom: 1px solid var(--border-line); font-weight: 400; }
@media (max-width: 1200px) { .training-grid { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 768px) { .training-plot svg { min-width: 480px; } }

/* ===== 页脚 ===== */
.footer {
  margin-top: .4rem;
  padding: .32rem 0;
  text-align: center;
  color: var(--text-body);
  font-size: max(14px, .14rem);          /* textTip:14px 规范最小字号 */
  border-top: .01rem solid var(--border-line);
}

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
  .page-header { width: 96%; }     /* 与 .main 同宽，保持对齐 */
  .main { width: 96%; padding: .2rem; }
  .top-grid { flex-direction: column; }
  .input-panel, .result-panel { width: 100%; }
  .showcase-grid { grid-template-columns: repeat(2, 1fr); }
  .flow-steps { grid-template-columns: repeat(2, 1fr); }
  .flow-step-arrow { display: none; }
}
@media (max-width: 768px) {
  .title-row { flex-direction: column; }
  .title-right { align-items: flex-start; max-width: 100%; }
  .title-row > div:first-child { width: 100%; }
  .risk-score { font-size: 28px; overflow-wrap: anywhere; }
  .risk-main { min-width: 0; }
  .form-grid { grid-template-columns: 1fr; }
  .risk-display { flex-direction: column; }
  .compare-panel { width: 100%; flex-direction: row; }
  .showcase-grid { grid-template-columns: 1fr; }
  .flow-steps { grid-template-columns: 1fr; }
  /* 规范禁止自定义字号缩放，保持 textH1 .40rem */
}
</style>
</head>
<body>

<div class="page-header" id="pageHeader" data-i18n="pageHeader">
  <span class="placeholder">加载中...</span>
</div>

<main class="main">

  <!-- 页面标题区 -->
  <div class="title-section">
    <div class="title-row">
      <div>
        <h1 id="app-title" data-i18n="appTitleDefault">量子增强应用</h1>
        <div class="subtitle" id="app-subtitle">Quantum-Enhanced QML Application</div>
      </div>
      <div class="title-right">
        <div class="lang-switch">
          <button class="lang-btn active" data-lang="zh">中</button>
          <button class="lang-btn" data-lang="en">EN</button>
        </div>
        <div class="service-status" data-testid="service-status">
          <span class="status-dot"></span>
          <span data-i18n="serviceStatus">正在连接服务</span>
        </div>
      </div>
    </div>
    <div class="title-bar"></div>
  </div>

  <!-- 顶部交互区 -->
  <section class="top-grid">

    <!-- 左侧：交易输入 -->
    <div class="input-panel">
      <h2 class="section-title"><span class="section-title-text" data-i18n="formTitle">输入参数</span></h2>
      <div class="input-card">
        <div id="input-form" class="form-grid"></div>

        <div class="action-row">
          <button class="btn-line" id="btnPreset" data-i18n="btnPreset">加载预设样本</button>
          <button class="btn-primary" id="btnDetect" disabled data-testid="infer-action" data-i18n="btnDetect">开始运行</button>
        </div>
      </div>
    </div>

    <!-- 右侧：运行结果 -->
    <div class="result-panel">
      <h2 class="section-title">
        <span class="section-title-text" data-i18n="resultTitle">运行结果</span>
        <span class="section-title-time" id="resultTime" data-i18n="resultWait">等待运行</span>
      </h2>
      <div class="result-card">
        <div class="risk-display">
          <!-- 主风险显示 -->
          <div class="risk-main" id="riskMain" data-testid="infer-result">
            <div class="risk-score" id="result-value" data-i18n="resultValueInit">等待运行</div>
            <div class="risk-level" id="result-unit" hidden></div>
            <div class="risk-level" id="riskLevel" data-i18n="riskInit">请点击"开始运行"</div>
            <div class="risk-level" id="result-meta" hidden></div>
            <div class="risk-tags" id="riskTags"></div>
          </div>
          <!-- 模型返回的分数及其含义 -->
          <div class="compare-panel">
            <div class="compare-box quantum">
              <div class="compare-label" data-i18n="quantumProbLabel">主要结果</div>
              <div class="compare-value" id="quantumProb">—</div>
            </div>
            <div class="compare-box classical">
              <div class="compare-label" data-i18n="scoreMeaning">分数含义</div>
              <div class="compare-value" id="scoreMeaning">等待模型输出</div>
            </div>
          </div>
        </div>

        <div class="tips-bar" id="tipsBar" data-i18n="tipsInit">
          请在左侧输入交易特征，点击 <b>开始运行</b> 查看量子增强模型的分析结果。
        </div>
      </div>
    </div>
  </section>

  <section class="graph-section" id="graphSection" data-testid="graph-partition" hidden>
    <h2 class="section-title"><span class="section-title-text" data-i18n="graphTitle">图与顶点二划分</span></h2>
    <div class="graph-card">
      <p id="graphStatus" role="status"></p>
      <svg id="graphSvg" viewBox="0 0 560 360" role="img" aria-label="Max-Cut 顶点划分"></svg>
      <p id="graphPartitionText"></p>
      <p class="graph-legend" data-i18n="graphLegend">蓝色圆点为 A 组，紫色方点为 B 组；蓝色实线为跨割边，灰色虚线为同组边。数字为顶点编号，边上标注权重。</p>
    </div>
  </section>

  <section class="convergence-section" id="convergenceSection" data-testid="solver-convergence" hidden>
    <h2 class="section-title"><span class="section-title-text" data-i18n="convergenceTitle">VQE 能量收敛</span></h2>
    <div class="convergence-card">
      <p id="convergenceStatus" role="status"></p>
      <div class="convergence-chart"><svg id="convergenceSvg" viewBox="0 0 800 320" role="img" aria-label="能量函数评估与同一实例的精确参考"></svg></div>
      <p id="convergenceSummary"></p>
      <p id="convergenceSemantics"></p>
      <p data-i18n="convergenceIntro">蓝线为实际能量评估，虚线为同一实例的参考能量，青色点为最终参数的独立复算。评估次数不等于优化迭代次数；线搜索中的能量可以上升。</p>
      <details><summary data-i18n="convergenceDetails">查看原始能量评估记录</summary><div class="convergence-table"><table><thead><tr><th data-i18n="convThEval">评估编号</th><th data-i18n="convThEnergy">能量</th></tr></thead><tbody id="convergenceRows"></tbody></table></div></details>
    </div>
  </section>

  <!-- ===== 算法主视觉展示区 ===== -->
  <section class="showcase-section" data-testid="algorithm-showcase">
    <h2 class="section-title">
      <span class="section-title-text" data-i18n="showcaseTitle">算法性能概览</span>
      <span class="section-title-time" id="showcase-updated"></span>
    </h2>
    <div class="showcase-card">
      <div id="showcase-content" class="showcase-grid"></div>
    </div>
  </section>

  <section class="training-section" data-testid="training-evidence" data-training-status="loading">
    <h2 class="section-title"><span id="trainingTitle" class="section-title-text">训练过程与模型参数</span></h2>
    <div class="training-card">
      <p id="trainingNote" class="training-note" role="status">正在读取离线训练记录</p>
      <div id="trainingCharts"></div>
    </div>
  </section>

  <!-- ===== 量子线路区 ===== -->
  <section class="circuit-section" data-testid="quantum-circuit" data-circuit-source="api">
    <h2 class="section-title">
      <span class="section-title-text" data-i18n="circuitTitle">量子线路</span>
      <span class="section-title-time" data-i18n="circuitSub">等待推理返回量子线路</span>
    </h2>
    <div class="circuit-card">
    <div class="circuit-source-hint" id="circuitHint" data-i18n="circuitHintInit">
      等待推理返回量子线路；q0 在上，时间从左向右
    </div>

      <div class="circuit-toolbar">
        <label><span data-i18n="circuitZoomLabel">线路缩放</span> <select id="circuitZoom" aria-label="线路缩放"><option value="0.5">50%</option><option value="0.75">75%</option><option value="1" selected>100%</option><option value="1.5">150%</option><option value="2">200%</option></select></label>
        <button id="circuitSvgExport" disabled data-i18n="circuitExportSvg">导出 SVG</button>
        <button id="circuitJsonExport" disabled data-i18n="circuitExportJson">导出线路数据</button>
        <span data-i18n="circuitLegend">● 控制位 · ⊕ X 目标位 · 参数单位为弧度</span>
      </div>
      <div class="circuit-container" tabindex="0" aria-label="量子线路，可横向滚动">
        <svg class="circuit-svg" viewBox="0 0 1200 360" xmlns="http://www.w3.org/2000/svg"><text x="30" y="60" fill="#939AAB" data-i18n="circuitPlaceholder">等待推理返回量子线路</text></svg>
      </div>
      <details class="circuit-details"><summary data-i18n="circuitDetails">查看门顺序与完整参数</summary><div class="circuit-table-scroll"><table><thead><tr><th data-i18n="circuitThOrder">顺序</th><th data-i18n="circuitThGate">门</th><th data-i18n="circuitThQubits">作用量子位（原始顺序）</th><th data-i18n="circuitThParams">参数（弧度）</th><th data-i18n="circuitThStage">阶段</th></tr></thead><tbody id="circuitGateRows"></tbody></table></div></details>
    </div>
  </section>

  <!-- ===== 方法流程区 ===== -->
  <section class="flow-section" data-testid="method-flow">
    <h2 class="section-title">
      <span class="section-title-text" data-i18n="flowTitle">算法流程</span>
      <span class="section-title-time" data-i18n="flowSub">点击步骤查看详情 · 数据 → 预处理 → 量子计算 → 结果解释</span>
    </h2>
    <div class="flow-card">
      <div id="flow-steps" class="flow-steps"></div>
      <!-- 流程详情面板 -->
      <div class="flow-detail" id="flowDetail">
        <div class="flow-detail-title" id="flowTitle"></div>
        <div class="flow-detail-desc" id="flowDesc"></div>
      </div>
    </div>
  </section>

  <!-- ===== 页脚 ===== -->
  <footer class="footer" id="app-footer"></footer>

</main>

<script>
let __apiHealth = null;
let __apiInfo = null;
let __lastQuantum = null;
let __trainingEvidence = {status: 'loading'};
let __trainingLang = 'zh';

/* ===== 框架界面 i18n（应用业务数据仍以后端 /api/* 返回的内容为准） ===== */
let __lang = 'zh';
let __serviceState = 'loading';        // loading | ready | down
let __bootError = '';
let __running = false;
let __inferenceState = 'idle';         // idle | running | success | error
let __stale = false;
let __lastResult = null;
let __lastError = '';
let __activeFlowStep = 0;

const I18N = {
  zh: {
    pageLoading: '加载中...',
    pageHeader: '加载中...',
    serviceConnecting: '正在连接服务',
    serviceStatus: '正在连接服务',
    serviceReady: '服务就绪',
    serviceUnavailable: '服务不可用',
    bootErrorConfig: '应用配置或运行时加载失败',
    bootNotReady: '应用尚未就绪',
    appTitleDefault: '量子增强应用',
    platformSuffix: ' | 天衍量子云平台',
    platformName: '天衍量子云平台',
    listSep: '；',
    formTitle: '输入参数',
    btnPresetDefault: '加载预设样本',
    btnPreset: '加载预设样本',
    btnDetectIdle: '开始运行',
    btnDetect: '开始运行',
    btnDetectRunning: '运行中...',
    resultTitle: '运行结果',
    resultWait: '等待运行',
    resultValueInit: '等待运行',
    riskInit: '请点击"开始运行"',
    quantumProbLabel: '主要结果',
    scoreMeaning: '分数含义',
    scoreAwait: '等待模型输出',
    tipsInit: '请在左侧输入交易特征，点击 <b>开始运行</b> 查看量子增强模型的分析结果。',
    showcaseTitle: '算法性能概览',
    showcaseUpdated: () => '最后更新: ',
    graphTitle: '图与顶点二划分',
    graphAria: 'Max-Cut 顶点划分',
    graphLegend: '蓝色圆点为 A 组，紫色方点为 B 组；蓝色实线为跨割边，灰色虚线为同组边。数字为顶点编号，边上标注权重。',
    graphPartitionBest: 'QAOA 最佳采样划分',
    graphPartitionMostProbable: 'QAOA 最可能样本划分',
    graphPartitionExact: '精确基线划分',
    graphPartitionGreedy: '贪心基线划分',
    graphStatus: (source, cut) => source + ' · 割值 ' + cut,
    graphEdgeTitle: (s, t2, w, crossing) => s + ' — ' + t2 + '; 权重 ' + w + '; ' + (crossing ? '跨割边' : '同组边'),
    graphNodeTitle: (n, group) => '顶点 ' + n + ': ' + group + ' 组',
    graphGroupEmpty: '空',
    graphPartitionText: (a, b) => 'A = {' + a + '}；B = {' + b + '}。割值为全部跨割边的权重之和。',
    convergenceTitle: 'VQE 能量收敛',
    convergenceAria: '能量函数评估与同一实例的精确参考',
    convergenceIntro: '蓝线为实际能量评估，虚线为同一实例的参考能量，青色点为最终参数的独立复算。评估次数不等于优化迭代次数；线搜索中的能量可以上升。',
    convergenceDetails: '查看原始能量评估记录',
    convThEval: '评估编号',
    convThEnergy: '能量',
    convergenceChartTitle: '实际 VQE 能量评估；横轴为评估编号，纵轴为能量',
    convergenceAxis: '能量函数评估编号',
    convergenceStatus: n => '本次求解：' + n + ' 次实际能量评估',
    convergenceSummary: (finalEnergy, unit, ref, abs) =>
      '最终能量 ' + finalEnergy + ' ' + unit +
      (Number.isFinite(ref)
        ? '；同一实例参考 ' + ref + ' ' + unit + '；绝对误差 ' + abs + ' ' + unit
        : '；未提供可比的精确参考'),
    circuitTitle: '量子线路',
    circuitSubInit: '等待推理返回量子线路',
    circuitSub: '等待推理返回量子线路',
    circuitHintInit: '等待推理返回量子线路；q0 在上，时间从左向右',
    circuitZoomLabel: '线路缩放',
    circuitExportSvg: '导出 SVG',
    circuitExportJson: '导出线路数据',
    circuitLegend: '● 控制位 · ⊕ X 目标位 · 参数单位为弧度',
    circuitPlaceholder: '等待推理返回量子线路',
    circuitContainerAria: '量子线路，可横向滚动',
    circuitDetails: '查看门顺序与完整参数',
    circuitThOrder: '顺序',
    circuitThGate: '门',
    circuitThQubits: '作用量子位（原始顺序）',
    circuitThParams: '参数（弧度）',
    circuitThStage: '阶段',
    circuitAria: (count, gates) => count + ' 量子比特、' + gates + ' 个门的量子线路',
    circuitSvgTitle: '量子线路：q0 在上，时间从左向右；完整参数见门表',
    circuitSourceHint: '线路来源: API 返回的模型门序列；q0 在上，时间从左向右。图上参数为缩略值，门表与导出保留原始数值；非硬件执行轨迹。',
    circuitTipPrefix: '量子线路: ',
    flowTitle: '算法流程',
    flowSub: '点击步骤查看详情 · 数据 → 预处理 → 量子计算 → 结果解释',
    staleResult: '输入已修改，请重新运行；下方为上一次结果',
    staleCircuit: '输入已修改：当前线路属于上一次结果，导出也对应上一次运行。',
    staleGraph: '输入已修改；当前划分属于上一次成功结果。',
    staleConvergence: '输入已修改；当前曲线属于上一次成功求解。',
    runningCircuit: '正在计算；当前线路与导出仍为上一次结果。',
    runningGraph: '正在求解；当前划分属于上一次成功结果。',
    runningConvergence: '正在求解；当前曲线属于上一次成功结果。',
    errorCircuit: '本次推理失败；当前线路与导出仍为上一次成功结果。',
    errorGraph: '本次求解失败；当前划分仍属于上一次成功结果。',
    errorConvergence: '本次求解失败；当前曲线仍属于上一次成功结果。',
    inferFailed: '推理失败',
    backendUnavailable: () => '后端不可用: ',
    resultEnergy: '能量求解结果',
    resultRegression: '回归预测结果',
    resultSolution: '组合优化结果',
    resultClassification: '模型分类结果',
    noLabel: '未提供类别',
    notProvided: '未提供',
    referenceInterval: (a, b, unit) => '参考区间 ' + a + ' – ' + b + ' ' + unit,
    intervalInvalid: '未提供有效预测区间',
    backendMainResult: '后端返回的主要结果',
    lastRun: (time, latency) => '最近运行: ' + time + (latency ? ' · ' + latency + ' ms' : ''),
    inferDone: '推理完成',
  },
  en: {
    pageLoading: 'Loading...',
    pageHeader: 'Loading...',
    serviceConnecting: 'Connecting to service',
    serviceStatus: 'Connecting to service',
    serviceReady: 'Service ready',
    serviceUnavailable: 'Service unavailable',
    bootErrorConfig: 'Application configuration or runtime failed to load',
    bootNotReady: 'Application is not ready yet',
    appTitleDefault: 'Quantum-Enhanced Application',
    platformSuffix: ' | TianYan Quantum Cloud Platform',
    platformName: 'TianYan Quantum Cloud Platform',
    listSep: '; ',
    formTitle: 'Input Parameters',
    btnPresetDefault: 'Load Preset Sample',
    btnPreset: 'Load Preset Sample',
    btnDetectIdle: 'Run',
    btnDetect: 'Run',
    btnDetectRunning: 'Running...',
    resultTitle: 'Results',
    resultWait: 'Waiting to run',
    resultValueInit: 'Waiting',
    riskInit: 'Click "Run" to start',
    quantumProbLabel: 'Primary Result',
    scoreMeaning: 'Score Meaning',
    scoreAwait: 'Awaiting model output',
    tipsInit: 'Enter transaction features on the left, then click <b>Run</b> to view the quantum-enhanced model analysis.',
    showcaseTitle: 'Algorithm Performance Overview',
    showcaseUpdated: () => 'Last updated: ',
    graphTitle: 'Graph Vertex Bipartition',
    graphAria: 'Max-Cut vertex partition',
    graphLegend: 'Blue circles are group A; purple squares are group B. Solid blue lines are crossing edges; dashed gray lines are within-group edges. Numbers are vertex indices; edge weights are annotated.',
    graphPartitionBest: 'QAOA best sampled partition',
    graphPartitionMostProbable: 'QAOA most probable partition',
    graphPartitionExact: 'Exact baseline partition',
    graphPartitionGreedy: 'Greedy baseline partition',
    graphStatus: (source, cut) => source + ' · cut value ' + cut,
    graphEdgeTitle: (s, t2, w, crossing) => s + ' — ' + t2 + '; weight ' + w + '; ' + (crossing ? 'crossing edge' : 'within-group edge'),
    graphNodeTitle: (n, group) => 'Vertex ' + n + ': group ' + group,
    graphGroupEmpty: 'empty',
    graphPartitionText: (a, b) => 'A = {' + a + '}; B = {' + b + '}. The cut value is the sum of weights of all crossing edges.',
    convergenceTitle: 'VQE Energy Convergence',
    convergenceAria: 'Energy evaluations and the exact reference for the same instance',
    convergenceIntro: 'The blue line shows actual energy evaluations, the dashed line the reference energy of the same instance, and the cyan dot an independent recomputation at the final parameters. The number of evaluations is not the number of optimizer iterations; energy can rise during line search.',
    convergenceDetails: 'View raw energy evaluation records',
    convThEval: 'Evaluation',
    convThEnergy: 'Energy',
    convergenceChartTitle: 'Actual VQE energy evaluations; x axis: evaluation index, y axis: energy',
    convergenceAxis: 'Energy evaluation index',
    convergenceStatus: n => 'Run: ' + n + ' actual energy evaluations',
    convergenceSummary: (finalEnergy, unit, ref, abs) =>
      'Final energy ' + finalEnergy + ' ' + unit +
      (Number.isFinite(ref)
        ? '; same-instance reference ' + ref + ' ' + unit + '; absolute error ' + abs + ' ' + unit
        : '; no comparable exact reference provided'),
    circuitTitle: 'Quantum Circuit',
    circuitSubInit: 'Waiting for circuit from inference',
    circuitSub: 'Waiting for circuit from inference',
    circuitHintInit: 'Waiting for circuit from inference; q0 on top, time flows left to right',
    circuitZoomLabel: 'Circuit zoom',
    circuitExportSvg: 'Export SVG',
    circuitExportJson: 'Export circuit data',
    circuitLegend: '● Control · ⊕ X target · parameters in radians',
    circuitPlaceholder: 'Waiting for circuit from inference',
    circuitContainerAria: 'Quantum circuit, scrollable horizontally',
    circuitDetails: 'View gate order and full parameters',
    circuitThOrder: 'Order',
    circuitThGate: 'Gate',
    circuitThQubits: 'Target qubits (original order)',
    circuitThParams: 'Parameters (radians)',
    circuitThStage: 'Stage',
    circuitAria: (count, gates) => 'Quantum circuit with ' + count + ' qubits and ' + gates + ' gates',
    circuitSvgTitle: 'Quantum circuit: q0 on top, time flows left to right; full parameters in the gate table',
    circuitSourceHint: 'Circuit source: model gate sequence returned by the API; q0 on top, time flows left to right. Chart parameters are abbreviated; the gate table and exports keep original values; not a hardware execution trace.',
    circuitTipPrefix: 'Quantum circuit: ',
    flowTitle: 'Algorithm Flow',
    flowSub: 'Click a step for details · Data → Preprocessing → Quantum computing → Interpretation',
    staleResult: 'Inputs changed, please rerun; the previous result is shown below.',
    staleCircuit: 'Inputs changed: the current circuit belongs to the previous result, and exports correspond to that run as well.',
    staleGraph: 'Inputs changed; the current partition is from the last successful result.',
    staleConvergence: 'Inputs changed; the current curve is from the last successful solve.',
    runningCircuit: 'Computing; the circuit and exports still reflect the previous result.',
    runningGraph: 'Solving; the current partition is from the last successful result.',
    runningConvergence: 'Solving; the current curve is from the last successful solve.',
    errorCircuit: 'This inference failed; the circuit and exports remain the last successful result.',
    errorGraph: 'This solve failed; the current partition remains the last successful result.',
    errorConvergence: 'This solve failed; the current curve remains the last successful solve.',
    inferFailed: 'Inference failed',
    backendUnavailable: () => 'Backend unavailable: ',
    resultEnergy: 'Energy result',
    resultRegression: 'Regression prediction',
    resultSolution: 'Combinatorial optimization result',
    resultClassification: 'Model classification result',
    noLabel: 'No label provided',
    notProvided: 'N/A',
    referenceInterval: (a, b, unit) => 'Reference interval ' + a + ' – ' + b + ' ' + unit,
    intervalInvalid: 'No valid prediction interval provided',
    backendMainResult: 'Primary result returned by the backend',
    lastRun: (time, latency) => 'Last run: ' + time + (latency ? ' · ' + latency + ' ms' : ''),
    inferDone: 'Inference complete',
  },
};

function t(key, ...args) {
  const table = I18N[__lang] || I18N.zh;
  let value = table[key];
  if (value == null) value = I18N.zh[key];
  if (value == null) return key;
  return typeof value === 'function' ? value(...args) : value;
}

/* Pick the localized business-data field. Backend contract: Chinese field is
   the base name (e.g. label), English field is base + '_en' (e.g. label_en).
   Falls back to Chinese when the English field is absent or empty. */
function L(obj, key) {
  if (obj == null) return '';
  if (__lang === 'en') {
    const en = obj[key + '_en'];
    if (en != null && en !== '') return en;
  }
  const zh = obj[key];
  return zh == null ? '' : zh;
}

/* Pick the localized business-data array. English array is base + '_en'. */
function LArr(zhArr, enArr) {
  if (__lang === 'en' && Array.isArray(enArr) && enArr.length > 0) return enArr;
  return Array.isArray(zhArr) ? zhArr : [];
}

function applyStaticI18n() {
  document.documentElement.lang = __lang === 'en' ? 'en' : 'zh-CN';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const value = t(key);
    if (value === key || typeof value === 'function') return;
    if (key === 'tipsInit') el.innerHTML = value;
    else el.textContent = value;
  });
  document.getElementById('graphSvg').setAttribute('aria-label', t('graphAria'));
  document.getElementById('convergenceSvg').setAttribute('aria-label', t('convergenceAria'));
  document.getElementById('circuitZoom').setAttribute('aria-label', t('circuitZoomLabel'));
  document.querySelector('.circuit-container').setAttribute('aria-label', t('circuitContainerAria'));
}

/* Re-apply framework-owned chrome that /api/info populated. Business data
   fields are bilingual via the L() helper (Chinese base + '_en' English). */
function refreshInfoChrome(info) {
  if (!info) return;
  const title = L(info, 'title');
  if (title) {
    document.title = title + t('platformSuffix');
    const h = document.getElementById('app-title');
    if (h) h.textContent = title;
  }
  const subEl = document.getElementById('app-subtitle');
  if (subEl) subEl.textContent = L(info, 'description') || L(info, 'scenario_summary') || '';
  const headerEl = document.getElementById('pageHeader');
  if (headerEl) headerEl.textContent = L(info, 'scenario_summary') || L(info, 'description') || '';
  const btnPreset = document.getElementById('btnPreset');
  if (btnPreset && info.presets && info.presets.length > 0) {
    btnPreset.textContent = L(info.presets[0], 'name') || t('btnPresetDefault');
  }
  renderShowcase(info.metrics || []);
  renderFlowSteps(info.method_steps || []);
  const footerEl = document.getElementById('app-footer');
  if (footerEl) {
    const parts = [];
    if (title) parts.push(title);
    parts.push(t('platformName'));
    footerEl.textContent = parts.join(' · ');
  }
}

function resetResultArea() {
  const riskMain = document.getElementById('riskMain');
  riskMain.removeAttribute('data-inference-state');
  const scoreEl = document.getElementById('result-value');
  scoreEl.textContent = t('resultValueInit');
  scoreEl.style.color = '';
  const unitEl = document.getElementById('result-unit');
  unitEl.textContent = '';
  unitEl.hidden = true;
  const metaEl = document.getElementById('result-meta');
  metaEl.textContent = '';
  metaEl.hidden = true;
  document.getElementById('riskLevel').textContent = t('riskInit');
  document.getElementById('riskTags').innerHTML = '';
  document.getElementById('quantumProb').textContent = '—';
  document.getElementById('scoreMeaning').textContent =
    (__apiHealth && L(__apiHealth, 'score_semantics')) || t('scoreAwait');
  document.getElementById('resultTime').textContent = t('resultWait');
  renderGraphPartition(null);
  renderConvergence(null);
  const tipsBar = document.getElementById('tipsBar');
  if (__serviceState === 'down') tipsBar.textContent = __bootError || t('serviceUnavailable');
  else if (__apiInfo) tipsBar.textContent = LArr(__apiInfo.scientific_boundary, __apiInfo.scientific_boundary_en).join(t('listSep'));
  else tipsBar.innerHTML = t('tipsInit');
  if (!__lastQuantum) {
    document.getElementById('circuitHint').textContent = t('circuitHintInit');
    document.querySelector('.circuit-section .section-title-time').textContent = t('circuitSubInit');
  }
}

function overlayRunningState() {
  document.getElementById('riskMain').dataset.inferenceState = 'running';
  const scoreEl = document.getElementById('result-value');
  scoreEl.textContent = '...';
  scoreEl.style.color = 'var(--text-body)';
  document.getElementById('btnDetect').textContent = t('btnDetectRunning');
  if (__lastQuantum) document.getElementById('circuitHint').textContent = t('runningCircuit');
  markGraphState('running', t('runningGraph'));
  markConvergenceState('running', t('runningConvergence'));
}

function overlayErrorState(message) {
  document.getElementById('riskMain').dataset.inferenceState = 'error';
  document.getElementById('result-value').textContent = t('inferFailed');
  document.getElementById('riskLevel').textContent = t('inferFailed');
  document.getElementById('tipsBar').textContent = t('backendUnavailable') + message;
  if (__lastQuantum) document.getElementById('circuitHint').textContent = t('errorCircuit');
  markGraphState('error', t('errorGraph'));
  markConvergenceState('error', t('errorConvergence'));
}

function applyLanguage(lang) {
  __lang = lang === 'en' ? 'en' : 'zh';
  __trainingLang = __lang;
  document.querySelectorAll('.lang-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.lang === __lang));
  applyStaticI18n();

  const status = document.querySelector('.service-status span:last-child');
  if (__serviceState === 'ready') {
    status.textContent = t('serviceReady') + ' · ' + (__apiHealth ? __apiHealth.service : '');
  } else if (__serviceState === 'down') {
    status.textContent = t('serviceUnavailable');
  } else {
    status.textContent = t('serviceConnecting');
  }

  if (__apiInfo) {
    refreshInfoChrome(__apiInfo);
    renderInputForm(__apiInfo.fields || []);
  }
  document.getElementById('btnDetect').textContent =
    __running ? t('btnDetectRunning') : t('btnDetectIdle');

  if (__lastResult) {
    renderInferenceResult(__lastResult);
    if (__running) overlayRunningState();
    else if (__inferenceState === 'error') overlayErrorState(__lastError);
    else if (__stale) markResultStale();
  } else {
    resetResultArea();
    if (__running) overlayRunningState();
  }

  renderTrainingEvidence(__trainingEvidence);
}

function markResultStale() {
  if (!__lastQuantum) return;
  __stale = true;
  document.getElementById('riskMain').dataset.inferenceState = 'stale';
  document.getElementById('resultTime').textContent = t('staleResult');
  document.getElementById('circuitHint').textContent = t('staleCircuit');
  markGraphState('stale', t('staleGraph'));
  markConvergenceState('stale', t('staleConvergence'));
}

function markGraphState(state, message) {
  const section = document.getElementById('graphSection');
  if (!section.hidden) {
    section.dataset.inferenceState = state;
    document.getElementById('graphStatus').textContent = message;
  }
}

function markConvergenceState(state, message) {
  const section = document.getElementById('convergenceSection');
  if (!section.hidden) {
    section.dataset.inferenceState = state;
    document.getElementById('convergenceStatus').textContent = message;
  }
}

document.addEventListener('DOMContentLoaded', async function() {
  try { await bootApi(); } catch(e) { console.warn('boot api failed:', e); }
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const lang = btn.dataset.lang;
      if (lang === __lang) return;
      applyLanguage(lang);
    });
  });
  const isSolver = __apiInfo && __apiInfo.execution_kind === 'solver';
  document.querySelector('[data-testid="training-evidence"]').hidden = isSolver;
  if (!isSolver) loadTrainingEvidence();
});

const TRAINING_UI = {
  zh: {
    title: '训练过程与模型参数', loading: '正在读取离线训练记录',
    missing: '此应用未提供变分训练记录。QSVC 量子核模型没有这组 VQC 损失曲线和旋转参数。',
    invalid: '训练记录无法验证或与当前模型不匹配，暂不绘图；可继续使用推理。',
    failed: '暂时无法读取训练记录，可继续使用推理。',
    source: '固定线路由代码定义；参数来自优化器的实际训练，JSON 由程序保存。损失下降不代表测试准确率或量子优势。',
    loss: '优化器根据训练数据调整参数', weights: '模型 JSON 中的实际训练参数',
    actual: '实际评估损失', best: '迄今最低损失', initial: '初始参数', trained: 'JSON 中的训练参数',
    evaluations: '目标函数评估次数', crossEntropy: '交叉熵损失', radians: '旋转角度（弧度）',
    details: '查看完整训练参数', parameter: '参数', samples: '训练样本', hash: '模型 SHA256',
  },
  en: {
    title: 'Training history and model parameters', loading: 'Loading offline training records',
    missing: 'No variational training record is available. QSVC kernel models do not have these VQC loss curves or rotation weights.',
    invalid: 'The training record is invalid or does not match this model. Inference remains available.',
    failed: 'Training records could not be loaded. Inference remains available.',
    source: 'Code defines the fixed circuit; the optimizer learns the weights from data, and code saves the JSON. Lower training loss does not prove test accuracy or quantum advantage.',
    loss: 'Optimizer evaluations on the training data', weights: 'Trained parameters stored in model JSON',
    actual: 'Evaluated loss', best: 'Best loss so far', initial: 'Initial weights', trained: 'Trained weights in JSON',
    evaluations: 'Objective evaluations', crossEntropy: 'Cross-entropy loss', radians: 'Rotation angle (radians)',
    details: 'Inspect full-precision weights', parameter: 'Parameter', samples: 'Training samples', hash: 'Model SHA256',
  },
};

async function loadTrainingEvidence() {
  try {
    const response = await fetch('/api/training');
    if (!response.ok) throw new Error('training evidence unavailable');
    __trainingEvidence = await response.json();
  } catch (_) { __trainingEvidence = {status: 'unavailable', reason: 'fetch_failed'}; }
  renderTrainingEvidence(__trainingEvidence);
}

function renderTrainingEvidence(evidence) {
  const ui = TRAINING_UI[__trainingLang] || TRAINING_UI.zh;
  const section = document.querySelector('[data-testid="training-evidence"]');
  const container = document.getElementById('trainingCharts');
  document.getElementById('trainingTitle').textContent = ui.title;
  section.dataset.trainingStatus = evidence.status;
  container.replaceChildren();
  const note = document.getElementById('trainingNote');
  if (evidence.status !== 'available') {
    note.textContent = evidence.status === 'loading' ? ui.loading :
      evidence.reason === 'not_recorded' ? ui.missing :
      evidence.reason === 'fetch_failed' ? ui.failed : ui.invalid;
    return;
  }
  note.textContent = `${ui.source} ${evidence.optimizer} · ${ui.samples}: ${evidence.training_samples}`;
  const fmt = value => Number(value.toPrecision(4)).toString();
  const text = (x, y, value, extra = '') => `<text x="${x}" y="${y}" fill="var(--text-sub)" font-size="16" ${extra}>${escapeHtml(value)}</text>`;
  const grid = (x1, y1, x2, y2) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--border-line)"/>`;
  const svg = (title, body, height = 330) => `<svg role="img" aria-label="${escapeHtml(title)}" viewBox="0 0 560 ${height}" xmlns="http://www.w3.org/2000/svg"><title>${escapeHtml(title)}</title>${body}</svg>`;
  const losses = evidence.loss;
  const low = Math.min(...losses), high = Math.max(...losses);
  const pad = Math.max((high - low) * 0.1, Math.abs(high) * 0.01, 0.001);
  const yLow = Math.max(0, low - pad), yHigh = high + pad;
  const px = index => 76 + index / Math.max(1, losses.length - 1) * 454;
  const py = value => 265 - (value - yLow) / (yHigh - yLow) * 235;
  let lossBody = '';
  for (let i = 0; i <= 4; i++) {
    const value = yLow + (yHigh - yLow) * i / 4, y = py(value);
    lossBody += grid(76, y, 530, y) + text(68, y + 5, fmt(value), 'text-anchor="end"');
  }
  const ticks = [...new Set([0, Math.floor((losses.length - 1) / 2), losses.length - 1])];
  ticks.forEach(index => { lossBody += text(px(index), 289, index + 1, 'text-anchor="middle"'); });
  lossBody += text(303, 320, ui.evaluations, 'text-anchor="middle"') + text(18, 150, ui.crossEntropy, 'text-anchor="middle" transform="rotate(-90 18 150)"');
  let best = Infinity;
  const bestLosses = losses.map(value => { best = Math.min(best, value); return best; });
  [losses, bestLosses].forEach((values, series) => {
    lossBody += `<polyline data-series="${series ? 'best' : 'actual'}" points="${values.map((value, i) => `${px(i)},${py(value)}`).join(' ')}" fill="none" stroke="var(--${series ? 'primary' : 'primary-deep'})" stroke-width="${series ? 3 : 2}"/>`;
  });
  losses.forEach((value, i) => { lossBody += `<circle cx="${px(i)}" cy="${py(value)}" r="3" fill="var(--primary-deep)"><title>${i + 1}: ${value}</title></circle>`; });
  const allWeights = [...evidence.initial_weights, ...evidence.trained_weights];
  const wLow = Math.min(...allWeights), wHigh = Math.max(...allWeights);
  const wPad = Math.max((wHigh - wLow) * 0.08, 0.1);
  const wx = value => 76 + (value - wLow + wPad) / (wHigh - wLow + 2 * wPad) * 454;
  const weightHeight = Math.max(330, evidence.parameter_names.length * 30 + 80);
  const bottom = weightHeight - 65;
  let weightBody = '';
  for (let i = 0; i <= 4; i++) {
    const value = wLow - wPad + (wHigh - wLow + 2 * wPad) * i / 4, x = wx(value);
    weightBody += grid(x, 20, x, bottom) + text(x, bottom + 24, fmt(value), 'text-anchor="middle"');
  }
  evidence.parameter_names.forEach((name, i) => {
    const y = 32 + i / Math.max(1, evidence.parameter_names.length - 1) * (bottom - 45);
    const x0 = wx(evidence.initial_weights[i]), x1 = wx(evidence.trained_weights[i]);
    weightBody += text(65, y + 5, name, 'text-anchor="end"') + `<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="var(--text-body)" stroke-width="2"/>`;
    weightBody += `<circle cx="${x0}" cy="${y}" r="5" fill="var(--card-bg)" stroke="var(--text-sub)" stroke-width="2"><title>${escapeHtml(ui.initial)}: ${evidence.initial_weights[i]}</title></circle>`;
    weightBody += `<polygon data-trained-weight="${i}" points="${x1},${y-6} ${x1+6},${y} ${x1},${y+6} ${x1-6},${y}" fill="var(--primary)"><title>${escapeHtml(ui.trained)}: ${evidence.trained_weights[i]}</title></polygon>`;
  });
  weightBody += text(303, weightHeight - 10, ui.radians, 'text-anchor="middle"');
  container.innerHTML = `<div class="training-grid"><div class="training-plot"><h3>${ui.loss}</h3><div class="training-legend"><span class="actual">━ ${ui.actual}</span><span class="best">━ ${ui.best}</span></div>${svg(ui.loss, lossBody)}</div><div class="training-plot"><h3>${ui.weights}</h3><div class="training-legend"><span>○ ${ui.initial}</span><span class="trained">◆ ${ui.trained}</span></div>${svg(ui.weights, weightBody, weightHeight)}</div></div><details class="training-table"><summary>${ui.details}</summary><table><thead><tr><th>${ui.parameter}</th><th>${ui.initial}</th><th>${ui.trained}</th></tr></thead><tbody>${evidence.parameter_names.map((name, i) => `<tr><td>${escapeHtml(name)}</td><td>${evidence.initial_weights[i]}</td><td>${evidence.trained_weights[i]}</td></tr>`).join('')}</tbody></table></details><p class="training-note">${ui.hash}: <code>${escapeHtml(evidence.model_sha256)}</code></p>`;
}

async function bootApi() {
  const status = document.querySelector('.service-status span:last-child');
  const button = document.getElementById('btnDetect');
  button.disabled = true;
  __serviceState = 'loading';
  status.textContent = t('serviceConnecting');
  try {
    const [healthResp, infoResp] = await Promise.all([fetch("/api/health"), fetch("/api/info")]);
    if (!healthResp.ok || !infoResp.ok) throw new Error(t('bootErrorConfig'));
    __apiHealth = await healthResp.json();
    __apiInfo = await infoResp.json();
    if (__apiHealth.status !== 'ok' || __apiHealth.model_loaded !== true) {
      throw new Error(t('bootNotReady'));
    }
    applyApiInfo(__apiInfo);
    __serviceState = 'ready';
    status.textContent = t('serviceReady') + ' · ' + __apiHealth.service;
    document.getElementById('scoreMeaning').textContent = L(__apiHealth, 'score_semantics');
    button.disabled = false;
  } catch (error) {
    __serviceState = 'down';
    __bootError = error.message;
    status.textContent = t('serviceUnavailable');
    document.getElementById('tipsBar').textContent = error.message;
  }
}

function applyApiInfo(info) {
  if (!info) return;
  refreshInfoChrome(info);
  renderInputForm(info.fields || []);

  const btnPreset = document.getElementById('btnPreset');
  if (btnPreset && info.presets && info.presets.length > 0) {
    btnPreset.onclick = () => applyPreset(info.presets[0]);
  } else if (btnPreset) {
    btnPreset.style.display = 'none';
  }
  document.getElementById('tipsBar').textContent = LArr(info.scientific_boundary, info.scientific_boundary_en).join(t('listSep'));
}

function renderInputForm(fields) {
  const container = document.getElementById('input-form');
  if (!container) return;
  // Preserve user-entered values when re-rendering (e.g. on language switch).
  const prevValues = {};
  fields.forEach(function(f) {
    const el = document.getElementById('field-' + f.id);
    if (el && el.value !== '') prevValues[f.id] = el.value;
  });
  container.innerHTML = '';
  fields.forEach(function(f) {
    const item = document.createElement('div');
    item.className = 'form-item';
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = L(f, 'label');
    item.appendChild(label);
    const input = document.createElement('input');
    input.type = 'number';
    input.className = 'form-input';
    input.id = 'field-' + f.id;
    input.name = f.id;
    // The API accepts any finite value in range; suggested increments must not
    // block valid defaults, presets, or manually entered decimal values.
    input.min = f.min; input.max = f.max; input.step = 'any';
    input.value = prevValues[f.id] != null ? prevValues[f.id] : f.default;
    input.required = true;
    input.addEventListener('input', markResultStale);
    label.htmlFor = input.id;
    item.appendChild(input);
    container.appendChild(item);
  });
}

function renderShowcase(metrics) {
  const container = document.getElementById('showcase-content');
  if (!container) return;
  container.innerHTML = '';
  const styles = ['', 'quantum', 'danger', 'success'];
  metrics.forEach(function(m, i) {
    const cls = styles[i % styles.length];
    const div = document.createElement('div');
    div.className = 'showcase-metric' + (cls ? ' ' + cls : '');
    div.innerHTML = '<div class="metric-value">' + escapeHtml(String(m.value)) + '</div><div class="metric-label">' + escapeHtml(L(m, 'label')) + '</div>';
    container.appendChild(div);
  });
  const updatedEl = document.getElementById('showcase-updated');
  if (updatedEl) {
    const now = new Date();
    const pad = function(n) { return n < 10 ? '0' + n : '' + n; };
    updatedEl.textContent = t('showcaseUpdated') + now.getFullYear() + '-' + pad(now.getMonth()+1) + '-' + pad(now.getDate()) + ' ' + pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
  }
}

function renderFlowSteps(steps) {
  const container = document.getElementById('flow-steps');
  if (!container) return;
  container.innerHTML = '';
  steps.forEach(function(step, idx) {
    const div = document.createElement('div');
    div.className = 'flow-step' + (idx === Math.floor(steps.length/2) ? ' core' : '');
    div.dataset.step = idx;
    div.onclick = function() { showFlowStep(idx, steps); };
    div.innerHTML = '<div class="flow-step-icon">' + (idx + 1) + '</div>' +
      '<div class="flow-step-name">' + escapeHtml(L(step, 'title')) + '</div>' +
      '<div class="flow-step-desc">' + escapeHtml((L(step, 'detail') || '').substring(0, 28)) + '</div>' +
      (idx < steps.length - 1 ? '<span class="flow-step-arrow">→</span>' : '');
    container.appendChild(div);
  });
  if (steps.length > 0) showFlowStep(Math.min(__activeFlowStep, steps.length - 1), steps);
}

function showFlowStep(idx, steps) {
  if (!steps || steps.length === 0) return;
  const step = steps[idx];
  if (!step) return;
  __activeFlowStep = idx;
  document.querySelectorAll('.flow-step').forEach(function(el) {
    el.classList.toggle('active', parseInt(el.dataset.step) === idx);
  });
  const detail = document.getElementById('flowDetail');
  if (detail) detail.style.display = 'block';
  const titleEl = document.getElementById('flowTitle');
  const descEl = document.getElementById('flowDesc');
  if (titleEl) titleEl.textContent = (idx + 1) + '. ' + L(step, 'title');
  if (descEl) descEl.textContent = L(step, 'detail');
}

function applyPreset(preset) {
  const values = preset.values || {};
  Object.keys(values).forEach(function(id) {
    const el = document.getElementById('field-' + id);
    if (el) el.value = values[id];
  });
  markResultStale();
}

function buildApiPayload() {
  const fields = (__apiInfo && __apiInfo.fields) || [];
  const payload = {};
  fields.forEach(function(f) {
    const el = document.getElementById('field-' + f.id);
    let val = el ? parseFloat(el.value) : f.default;
    if (!Number.isFinite(val)) val = f.default;
    payload[f.id] = val;
  });
  return payload;
}

document.getElementById('btnDetect').onclick = async function() {
  const btn = document.getElementById('btnDetect');
  const inputs = [...document.querySelectorAll('#input-form input')];
  if (inputs.some(input => !input.reportValidity())) return;
  const payload = buildApiPayload();
  const presetButton = document.getElementById('btnPreset');
  inputs.forEach(input => { input.disabled = true; });
  presetButton.disabled = true;

  __running = true;
  __inferenceState = 'running';
  btn.disabled = true;
  overlayRunningState();

  try {
    const resp = await fetch("/api/infer", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    renderInferenceResult(data);
    __lastResult = data;
    __stale = false;
    __lastError = '';
    __inferenceState = 'success';
  } catch(e) {
    __inferenceState = 'error';
    __lastError = e.message;
    overlayErrorState(e.message);
  } finally {
    __running = false;
    inputs.forEach(input => { input.disabled = false; });
    presetButton.disabled = false;
    btn.textContent = t('btnDetectIdle'); btn.disabled = false;
  }
};

function renderInferenceResult(data) {
  const scoreEl = document.getElementById('result-value');
  const levelEl = document.getElementById('riskLevel');
  const riskMain = document.getElementById('riskMain');
  const tagsEl = document.getElementById('riskTags');
  const quantumEl = document.getElementById('quantumProb');
  const meaningEl = document.getElementById('scoreMeaning');
  const resultTime = document.getElementById('resultTime');
  const tipsBar = document.getElementById('tipsBar');

  const pred = data.prediction || {};
  const quantum = data.quantum || {};

  const scalar = pred.kind === 'regression' || pred.kind === 'energy';
  scoreEl.textContent = scalar ? String(pred.value) : (L(pred, 'label') || t('noLabel'));
  const unitEl = document.getElementById('result-unit');
  const metaEl = document.getElementById('result-meta');
  unitEl.textContent = scalar ? String(L(pred, 'unit') || '') : '';
  unitEl.hidden = unitEl.textContent.length === 0;
  levelEl.textContent = pred.kind === 'energy' ? t('resultEnergy') : (pred.kind === 'regression' ? t('resultRegression') : (pred.kind === 'solution' ? t('resultSolution') : t('resultClassification')));
  if (pred.kind === 'regression') {
    const interval = pred.interval;
    const validInterval = Array.isArray(interval) && interval.length === 2
      && interval.every(value => typeof value === 'number' && Number.isFinite(value))
      && interval[0] <= interval[1];
    metaEl.textContent = validInterval
      ? t('referenceInterval', interval[0], interval[1], unitEl.textContent)
      : t('intervalInvalid');
  } else {
    metaEl.textContent = L(pred, 'score_semantics') || '';
  }
  metaEl.hidden = !metaEl.textContent;
  scoreEl.style.color = 'var(--text-body)';
  riskMain.classList.remove('low', 'medium', 'high');
  const scores = pred.scores || [];
  const selected = scores.find(item => item.label === pred.label);
  quantumEl.textContent = pred.kind === 'classification'
    ? (Number.isFinite(pred.decision_value) ? String(pred.decision_value) : t('notProvided'))
    : (scalar || pred.kind === 'solution' ? String(pred.value) : (selected ? String(selected.value) : t('notProvided')));
  meaningEl.textContent = L(pred, 'score_semantics') || (__apiHealth && L(__apiHealth, 'score_semantics')) || t('backendMainResult');
  tagsEl.innerHTML = '';
  scores.forEach(function(score) {
    const tag = document.createElement('span');
    tag.className = 'tag tag-primary';
    tag.textContent = L(score, 'label') + ': ' + score.value;
    tagsEl.appendChild(tag);
  });
  renderCircuit(quantum);
  renderGraphPartition(data.graph);
  renderConvergence(data.convergence);

  resultTime.textContent = t('lastRun', new Date().toLocaleTimeString(), data.latency_ms);

  let tipParts = [...LArr(data.explanations, data.explanations_en), ...LArr(data.boundary, data.boundary_en)].map(escapeHtml);
  const gateCount = (quantum.gates || []).length;
  const qubitCount = quantum.qubits || 0;
  if (qubitCount > 0) {
    tipParts.push(t('circuitTipPrefix') + qubitCount + ' qubits · ' + gateCount + ' gates · depth ' + (quantum.depth || '?') + ' · ' + escapeHtml(quantum.backend || ''));
  }
  if (tipParts.length === 0) tipParts.push(t('inferDone'));
  tipsBar.innerHTML = tipParts.join('<br>');
  riskMain.dataset.inferenceState = 'success';
}

function renderConvergence(convergence) {
  const section = document.getElementById('convergenceSection');
  const svg = document.getElementById('convergenceSvg');
  if (!convergence) {
    section.hidden = true;
    svg.innerHTML = '';
    document.getElementById('convergenceRows').innerHTML = '';
    return;
  }
  const points = convergence.points;
  const energies = points.map(p => p.energy).concat([convergence.final_energy]);
  const reference = convergence.reference_energy;
  if (Number.isFinite(reference)) energies.push(reference);
  const low = Math.min(...energies), high = Math.max(...energies);
  const span = Math.max(high - low, 1e-9);
  const xmin = points[0].evaluation, xmax = points[points.length - 1].evaluation;
  const x = value => 100 + (value - xmin) / Math.max(xmax - xmin, 1) * 660;
  const y = value => 265 - (value - low + span * .08) / (span * 1.16) * 230;
  const line = points.map(p => `${x(p.evaluation)},${y(p.energy)}`).join(' ');
  let markup = '<title>' + t('convergenceChartTitle') + '</title><path d="M100 25V270H765" fill="none" stroke="#939aab"/>';
  for (let i = 0; i <= 4; i++) {
    const value = low + span * i / 4;
    markup += `<text x="90" y="${y(value) + 4}" text-anchor="end" font-size="12" fill="#41464f">${value.toFixed(8)}</text>`;
  }
  if (Number.isFinite(reference)) markup += `<line data-testid="convergence-reference" x1="100" y1="${y(reference)}" x2="760" y2="${y(reference)}" stroke="var(--quantum-purple)" stroke-dasharray="6 4"/>`;
  markup += `<polyline data-testid="convergence-trace" points="${line}" fill="none" stroke="#1664ff" stroke-width="2"/>`;
  markup += `<circle data-testid="convergence-final" cx="${x(xmax)}" cy="${y(convergence.final_energy)}" r="5" fill="var(--cyan)"/>`;
  markup += `<text x="100" y="292" font-size="12" fill="#41464f">${xmin}</text><text x="760" y="292" text-anchor="end" font-size="12" fill="#41464f">${xmax}</text><text x="430" y="314" text-anchor="middle" font-size="13" fill="#41464f">${t('convergenceAxis')}</text>`;
  svg.innerHTML = markup;
  section.hidden = false;
  section.dataset.inferenceState = 'success';
  section.dataset.evaluationCount = String(points.length);
  document.getElementById('convergenceStatus').textContent = t('convergenceStatus', points.length);
  document.getElementById('convergenceSummary').textContent = t(
    'convergenceSummary',
    convergence.final_energy,
    L(convergence, 'unit'),
    Number.isFinite(reference) ? reference : NaN,
    Number.isFinite(reference) ? Math.abs(convergence.final_energy - reference).toExponential(3) : NaN
  );
  document.getElementById('convergenceSemantics').textContent = L(convergence, 'semantics');
  document.getElementById('convergenceRows').innerHTML = points.map(p => `<tr><td>${p.evaluation}</td><td>${p.energy}</td></tr>`).join('');
}

function renderGraphPartition(graph) {
  const section = document.getElementById('graphSection');
  const svg = document.getElementById('graphSvg');
  if (!graph) {
    section.hidden = true;
    svg.innerHTML = '';
    return;
  }
  const count = graph.num_nodes;
  const position = Array.from({length: count}, (_, node) => {
    const angle = -Math.PI / 2 + node * 2 * Math.PI / count;
    return [280 + 220 * Math.cos(angle), 180 + 140 * Math.sin(angle)];
  });
  let markup = '';
  graph.edges.forEach(([source, target, weight]) => {
    const [x1, y1] = position[source], [x2, y2] = position[target];
    const crossing = graph.partition[source] !== graph.partition[target];
    markup += `<g data-graph-edge="${source}-${target}" data-crossing="${crossing}"><title>${escapeHtml(t('graphEdgeTitle', source, target, weight, crossing))}</title><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${crossing ? '#1664ff' : '#939aab'}" stroke-width="${crossing ? 3 : 1.5}" ${crossing ? '' : 'stroke-dasharray="6 5"'}/><text x="${(x1+x2)/2}" y="${(y1+y2)/2-6}" text-anchor="middle" fill="#41464f" stroke="white" stroke-width="3" paint-order="stroke" font-size="13">${weight}</text></g>`;
  });
  graph.partition.forEach((group, node) => {
    const [x, y] = position[node];
    const shape = group === 0
      ? `<circle cx="${x}" cy="${y}" r="16" fill="#1664ff"/>`
      : `<rect x="${x-16}" y="${y-16}" width="32" height="32" rx="3" fill="#bb79e1"/>`;
    markup += `<g data-graph-node="${node}" data-partition="${group}"><title>${escapeHtml(t('graphNodeTitle', node, group === 0 ? 'A' : 'B'))}</title>${shape}<text x="${x}" y="${y+5}" text-anchor="middle" fill="white" font-size="15">${node}</text></g>`;
  });
  svg.innerHTML = markup;
  const nameKeys = {best_sample: 'graphPartitionBest', most_probable_sample: 'graphPartitionMostProbable', exact: 'graphPartitionExact', greedy: 'graphPartitionGreedy'};
  section.hidden = false;
  section.dataset.inferenceState = 'success';
  document.getElementById('graphStatus').textContent = t('graphStatus', t(nameKeys[graph.partition_source] || 'graphPartitionBest'), graph.cut_value);
  const members = group => graph.partition.flatMap((bit, node) => bit === group ? [node] : []).join(', ') || t('graphGroupEmpty');
  document.getElementById('graphPartitionText').textContent = t('graphPartitionText', members(0), members(1));
}

function renderCircuit(quantum) {
  __lastQuantum = quantum;
  const count = quantum.qubits;
  const gates = quantum.gates || [];
  const svg = document.querySelector('.circuit-svg');
  // Preserve order on every occupied wire, including a controlled gate's span.
  const busy = Array(count).fill(-1);
  const columns = [];
  const placements = gates.map(gate => {
    const first = Math.min(...gate.qubits), last = Math.max(...gate.qubits);
    const column = Math.max(...busy.slice(first, last + 1)) + 1;
    for (let wire = first; wire <= last; wire++) busy[wire] = column;
    const label = String(gate.gate);
    columns[column] = Math.max(columns[column] || 110, Math.min(300, label.length * 9 + 30), gate.params?.length ? 196 : 0);
    return column;
  });
  const offsets = [];
  let width = 70;
  columns.forEach(size => { offsets.push(width + size / 2); width += size; });
  width = Math.max(320, width + 30);
  const height = Math.max(150, count * 76 + 40);
  const wireY = wire => 50 + wire * 76;
  svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', t('circuitAria', count, gates.length));
  let markup = '<title>' + t('circuitSvgTitle') + '</title><rect width="100%" height="100%" fill="#F3F7FF" rx="8"/>';
  for (let index = 0; index < count; index += 1) {
    const y = wireY(index);
    markup += `<g data-testid="quantum-wire"><text x="15" y="${y + 5}" fill="#020814" font-size="16">q${index}</text><line x1="55" y1="${y}" x2="${width - 20}" y2="${y}" stroke="#939AAB"/></g>`;
  }
  gates.forEach(function(gate, index) {
    const x = offsets[placements[index]], wires = gate.qubits;
    const name = String(gate.gate).toUpperCase();
    const params = gate.params || [];
    const full = `${index + 1}. ${gate.gate}(${params.join(', ')}) · ${wires.map(q => 'q' + q).join(', ')} · ${gate.stage} · ${L(gate, 'detail')}`;
    markup += `<g data-gate-index="${index}" data-gate-name="${escapeHtml(name)}"><title>${escapeHtml(full)}</title>`;
    const circle = (wire, radius, fill) => `<circle cx="${x}" cy="${wireY(wire)}" r="${radius}" fill="${fill}" stroke="#1664FF" stroke-width="2"/>`;
    const box = (wire, label) => {
      const boxWidth = Math.min(280, Math.max(56, label.length * 9 + 16));
      const short = label.length > 28 ? label.slice(0, 27) + '…' : label;
      return `<rect x="${x - boxWidth / 2}" y="${wireY(wire) - 20}" width="${boxWidth}" height="40" rx="5" fill="#1664FF"/><text x="${x}" y="${wireY(wire) + 5}" text-anchor="middle" font-size="16" fill="white">${escapeHtml(short)}</text>`;
    };
    const low = Math.min(...wires), high = Math.max(...wires);
    if (wires.length > 1) markup += `<line x1="${x}" x2="${x}" y1="${wireY(low)}" y2="${wireY(high)}" stroke="#1664FF" stroke-width="2"/>`;
    const controlled = wires.length === 2 && ['CX', 'CNOT', 'CY', 'CZ', 'CH', 'CRX', 'CRY', 'CRZ', 'CP'].includes(name);
    if (controlled) {
      markup += circle(wires[0], 5, '#1664FF');
      if (name === 'CX' || name === 'CNOT') {
        markup += circle(wires[1], 15, '#F3F7FF');
        markup += `<path d="M${x - 15} ${wireY(wires[1])}h30 M${x} ${wireY(wires[1]) - 15}v30" stroke="#1664FF" stroke-width="2"/>`;
      } else if (name === 'CZ') markup += circle(wires[1], 5, '#1664FF');
      else markup += box(wires[1], name.slice(1));
    } else if (name === 'SWAP' && wires.length === 2) {
      wires.forEach(wire => { markup += `<path d="M${x - 9} ${wireY(wire) - 9}l18 18 M${x - 9} ${wireY(wire) + 9}l18 -18" stroke="#1664FF" stroke-width="2"/>`; });
    } else if (wires.length === 1) markup += box(wires[0], name);
    else {
      // Unknown multi-qubit operations remain one labeled block, not N copies.
      markup += `<rect x="${x - 42}" y="${wireY(low) - 22}" width="84" height="${wireY(high) - wireY(low) + 44}" rx="5" fill="#1664FF"/>`;
      wires.forEach((wire, operand) => { markup += `<text x="${x - 36}" y="${wireY(wire) + 5}" fill="white" font-size="14">${operand}</text>`; });
      markup += `<text x="${x + 4}" y="${(wireY(low) + wireY(high)) / 2 + 5}" text-anchor="middle" fill="white" font-size="14">${escapeHtml(name.length > 7 ? name.slice(0, 6) + '…' : name)}</text>`;
    }
    if (params.length) {
      const shortParams = params.map(value => Number(value).toPrecision(4)).join(', ');
      const label = shortParams.length > 22 ? shortParams.slice(0, 21) + '…' : shortParams;
      markup += `<text x="${x}" y="${wireY(high) + 38}" text-anchor="middle" fill="#020814" font-size="14">${escapeHtml(label)}</text>`;
    }
    markup += '</g>';
  });
  svg.innerHTML = markup;
  document.getElementById('circuitGateRows').innerHTML = gates.map((gate, index) => `<tr><td>${index + 1}</td><td>${escapeHtml(gate.gate)}</td><td>${gate.qubits.map(q => 'q' + q).join(', ')}</td><td>${escapeHtml((gate.params || []).join(', ') || '—')}</td><td>${escapeHtml(gate.stage)}</td></tr>`).join('');
  document.querySelector('.circuit-section .section-title-time').textContent = count + ' qubits · ' + gates.length + ' gates · depth ' + quantum.depth + ' · ' + quantum.backend;
  document.getElementById('circuitHint').textContent = t('circuitSourceHint');
  document.getElementById('circuitSvgExport').disabled = false;
  document.getElementById('circuitJsonExport').disabled = false;
  updateCircuitZoom();
}

function updateCircuitZoom() {
  const svg = document.querySelector('.circuit-svg');
  svg.style.width = svg.viewBox.baseVal.width * Number(document.getElementById('circuitZoom').value) + 'px';
}
document.getElementById('circuitZoom').onchange = updateCircuitZoom;
function downloadCircuit(content, type, extension) {
  const url = URL.createObjectURL(new Blob([content], {type}));
  const link = document.createElement('a');
  link.href = url; link.download = 'quantum-circuit.' + extension;
  document.body.appendChild(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
document.getElementById('circuitSvgExport').onclick = () => {
  if (!__lastQuantum) return;
  const svg = document.querySelector('.circuit-svg').cloneNode(true);
  svg.removeAttribute('style');
  svg.setAttribute('width', svg.viewBox.baseVal.width);
  svg.setAttribute('height', svg.viewBox.baseVal.height);
  downloadCircuit(new XMLSerializer().serializeToString(svg), 'image/svg+xml;charset=utf-8', 'svg');
};
document.getElementById('circuitJsonExport').onclick = () => {
  if (__lastQuantum) downloadCircuit(JSON.stringify(__lastQuantum, null, 2), 'application/json;charset=utf-8', 'json');
};

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, function(c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}
</script>
</body>
</html>
