# Agent Skills 合集

一组可复用的 [Agent Skills](https://skills.sh/)，面向量子应用工程、量子云交付以及 Skill 开发场景。

每个 skill 都是一个自包含的能力包，可将通用 AI 智能体转变为专业助手：必需的 `SKILL.md`（YAML frontmatter + 指令），以及可选的 `references/`、`scripts/`、`assets/`、`evals/` 目录。Skill 采用渐进式加载模型——平时只加载元数据，正文与捆绑资源按需加载。

## Skill 清单

### 量子应用交付流水线

这一组 skill 可组合成端到端工作流：需求澄清 → 证据调研 → 方案规划 → 算法实现 → 云端执行 → 交付验证。

| Skill | 用途 |
| --- | --- |
| [`quantum-application-intake`](quantum-application-intake/SKILL.md) | 在调研和实现之前澄清量子应用需求，记录当前机器的执行契约。 |
| [`quantum-evidence-research`](quantum-evidence-research/SKILL.md) | 调研有出处的证据：经典基线、数据集、Cqlib/Qiskit/PennyLane 中持续维护的组件及评估协议。 |
| [`quantum-solution-ranking`](quantum-solution-ranking/SKILL.md) | 将调研证据转化为有边界、可执行的量子应用计划，并对实验结果进行复盘。 |
| [`quantum-algorithm-qaoa`](quantum-algorithm-qaoa/SKILL.md) | 与 SDK 无关的 QAOA 工程实践，覆盖 QUBO/伊辛优化（MaxCut、投资组合、调度、背包/TSP 类问题）。 |
| [`quantum-algorithm-vqe`](quantum-algorithm-vqe/SKILL.md) | 与 SDK 无关的 VQE 工程实践，覆盖基态能与分子能量、ansatz 设计及参考能量校验。 |
| [`quantum-algorithm-qml`](quantum-algorithm-qml/SKILL.md) | 量子机器学习路由，覆盖量子核、变分监督、混合神经、量子储备池、生成式、表征学习与强化学习等方向。 |
| [`quantum-cloud-execution`](quantum-cloud-execution/SKILL.md) | 在天衍量子计算云平台上执行有边界、经用户授权的验证作业，并记录回执。 |
| [`quantum-application-verification`](quantum-application-verification/SKILL.md) | 在隔离快照中运行聚焦的交付检查，记录观察到的结果，但不对正确性做认证。 |

### 应用工程

| Skill | 用途 |
| --- | --- |
| [`qccp-service`](qccp-service/SKILL.md) | 后端/API 契约与可运行 FastAPI 应用打包，以及 Java/Spring Cloud 平台集成指引。 |
| [`tianyan-ui-suite`](tianyan-ui-suite/SKILL.md) | 为可运行量子应用构建精致的天衍 UI 2.0 界面：独立页面、响应式结果视图与量子线路可视化。 |

### 元 Skill

| Skill | 用途 |
| --- | --- |
| [`skill-creator`](skill-creator/SKILL.md) | 创建、改进、基准测试和打包 skill；分析并优化 skill 的触发描述。 |
| [`find-skills`](find-skills/SKILL.md) | 从开放的 [skills.sh](https://skills.sh/) 生态中发现可安装的 skill。 |

## Skill 结构

```text
skill-name/
├── SKILL.md        # 必需：YAML frontmatter（name、description）+ 指令正文
├── references/     # 可选：按需加载到上下文中的参考文档
├── scripts/        # 可选：确定性的可执行脚本（Python/Bash）
├── assets/         # 可选：产出物中使用的模板与文件
└── evals/          # 可选：评测提示词与预期结果
```

## 许可证

基于 Apache License, Version 2.0 开源，详见 [LICENSE](LICENSE)。
