# T2：优化轨迹编码方案 v1.0

日期：2026-11-10。编码对象是**可观察动作**，不是不可见的推理过程。

## 单位与抽样

- `tool_call`：一次真实工具调用及其按 tool_use_id 配对的返回；同一 shell 内多种活动只记主活动，解释中注明。异步启动不代表测量完成。
- `episode`：来源发布者把多次调用压缩成的活动段。与 tool_call 分表，绝不合并计算比例，也不把 n_events 复制成同样数量的标签。
- `agent_step`：ISO-Bench原始导出的一个step，可能含一次/多次工具调用或终止错误；按JSON Pointer定位，不能与调用级合并。
- 完整导出会话可全部规则初标，再复核所有可识别方向改变、数值失败和最终确认。超长会话允许前后连续片段加转折点，但必须记录选取范围与遗漏。
- 本轮 KernelBench 覆盖两份完整 JSONL 导出中的全部工具调用；InferenceBench 覆盖数据文件前两个 run 的完整压缩 episode 序列。选择与访问失败见 `data/raw/kernelbench/selection.json` 和 `manifest.jsonl`。这是方便样本，不具总体代表性。
- ISO-Bench追加正式sglang运行目录按路径排序前两份trajectory.json，48/10个agent_step全部逐项复核；二者末尾API错误中止，完整导出不等于任务成功完成。

## 字段定义与判定优先级

| 字段 | 判定规则 |
|---|---|
| phase | 探索代码、profile、提出假设、修改代码、测量、接受、回滚、写报告、等待；另设环境准备/其他，避免把安装与编译失败硬归为优化 |
| tool | 按实际执行分类：NCU/nsys/torch profiler/端到端 benchmark/kernel benchmark/正确性检查/读源码/查文档/其他。which ncu 或阅读说明不算 NCU 使用 |
| layer | 优化对象的主要层；attention 与 kernel 冲突时用 attention。对等待且无法归属的动作填不可判定；辅助测试脚本归测量工具 |
| hypothesis | 有原文或源码注释写 explicit；只能从 diff 解读写 inferred；没有可观察假设填 null/missing。不得给每次编辑补写假设 |
| evidence | 有：有可定位测量/规范支持；无：有明确假设却未找到支持；数据有误：另有检查反证该数据；不可判定：摘要/缺失妨碍判断；不适用：本步无假设评估。数值探针不自动证明性能瓶颈 |
| outcome | 成功指当前明确检查返回 PASS，非“优化收益已证实”；失败指工具/编译/运行失败；正确性不过需明确数值或语义检查失败；后台启动、编辑成功和纯读取均不证明候选成功 |
| turning_point | 改算法/路径/层次、推翻结论、引入或写入危险结论；规则初标的 false 是未标记，不能解释为“确认无转折” |
| component | 按此动作职责映射 miner/profiler/optimizer/selector/skills/accumulation；这是分析者映射，不保证原框架有该组件 |
| annotation_method | 规则初标与研究助理逐项复核分别统计；这里的研究助理是本次 AI agent，不是独立人类双人标注 |
| duration_seconds | 只有可信开始/结束与并发归属才填数字，否则 null。调用数占比不能改名为耗时占比 |

优先级：候选显式编辑 → 实际 profiler 调用 → 正确性/性能测量 → 轮询等待 → 读取 → 环境/其他。读取已经完成的逐 kernel 计时可记 profile；读取空日志记等待。静态规范、硬件规格与实测瓶颈需在 rationale 中区分。

## 质量控制与指标

1. 核查记录的原始行确实包含工具调用，且 result_line 对应匹配的 tool_use_id。保留来源 URL、修订哈希和本地定位。
2. 含复合活动或摘要矛盾时降低结论强度，不擅自拆出不存在的动作。InferenceBench 的 `n_edits=0` 也可能与摘要“写脚本”并存；不拿该字段推断没有编辑。
3. 首次候选修改定义为第一次 Write/Edit solution.py；scratch 原型和辅助 benchmark 另列。先 profile 比例只在 tool_call 可观察完整会话计算。
4. 无证据假设比例只用可明确提取的 explicit 假设为分母；同时报告 missing 和 inferred。加密 reasoning、只提取工具调用会漏掉语言层假设，不能声称无假设。
5. 正式研究应让第二位独立标注者复核盲抽样，逐字段报告一致率与分歧解决记录。本轮没有独立复标，不报告虚假的 kappa。
6. 工具/layer/phase 频率是结构性初标统计；机制结论须回到逐项复核例子。样本任务本来就是 kernel，不能将 kernel 占比当作自发层次偏好。

## 可执行 JSON Schema

与 [schema.json](../data/annotations/schema.json) 内容完全一致。重建：`python scripts/annotate_traces.py`，再运行 `python scripts/build_codebook.py`。

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "优化轨迹编码 v1.0",
  "type": "object",
  "required": [
    "source",
    "unit",
    "session_id",
    "step_id",
    "raw_file",
    "source_locator",
    "source_url",
    "phase",
    "tool",
    "layer",
    "hypothesis",
    "hypothesis_origin",
    "evidence",
    "outcome",
    "turning_point",
    "component",
    "annotation_method",
    "annotation_rationale",
    "duration_seconds"
  ],
  "properties": {
    "source": {
      "type": "string"
    },
    "unit": {
      "enum": [
        "tool_call",
        "episode",
        "agent_step"
      ]
    },
    "session_id": {
      "type": "string"
    },
    "step_id": {
      "type": "integer",
      "minimum": 1
    },
    "raw_file": {
      "type": "string"
    },
    "source_locator": {
      "type": "string"
    },
    "source_url": {
      "type": "string",
      "format": "uri"
    },
    "source_line": {
      "type": [
        "integer",
        "null"
      ]
    },
    "result_line": {
      "type": [
        "integer",
        "null"
      ]
    },
    "candidate_edit": {
      "type": [
        "boolean",
        "null"
      ]
    },
    "upstream_event_count": {
      "type": "integer",
      "minimum": 1
    },
    "upstream_label_source": {
      "type": [
        "string",
        "null"
      ]
    },
    "phase": {
      "enum": [
        "探索代码",
        "profile",
        "提出假设",
        "修改代码",
        "测量",
        "接受",
        "回滚",
        "写报告",
        "等待",
        "环境准备",
        "其他"
      ]
    },
    "tool": {
      "enum": [
        "NCU",
        "nsys",
        "torch profiler",
        "端到端 benchmark",
        "kernel benchmark",
        "正确性检查",
        "读源码",
        "查文档",
        "其他"
      ]
    },
    "layer": {
      "enum": [
        "kernel",
        "算子融合",
        "attention",
        "调度器",
        "runtime 与 host 开销",
        "并行配置",
        "运行参数",
        "量化",
        "推测解码",
        "测量工具",
        "其他",
        "不可判定"
      ]
    },
    "hypothesis": {
      "type": [
        "string",
        "null"
      ]
    },
    "hypothesis_origin": {
      "enum": [
        "explicit",
        "inferred",
        "missing"
      ]
    },
    "evidence": {
      "enum": [
        "有",
        "无",
        "数据有误",
        "不可判定",
        "不适用"
      ]
    },
    "outcome": {
      "enum": [
        "成功",
        "失败",
        "正确性不过",
        "未测"
      ]
    },
    "turning_point": {
      "type": "boolean"
    },
    "component": {
      "enum": [
        "miner",
        "profiler",
        "optimizer",
        "selector",
        "accumulation",
        "skills"
      ]
    },
    "annotation_method": {
      "enum": [
        "规则初标",
        "研究助理逐项复核"
      ]
    },
    "annotation_rationale": {
      "type": "string"
    },
    "duration_seconds": {
      "type": [
        "number",
        "null"
      ],
      "minimum": 0
    }
  },
  "additionalProperties": false
}
```

## 三个逐项复核示例

### 示例 1

```json
{
  "phase": "profile",
  "tool": "kernel benchmark",
  "layer": "attention",
  "hypothesis": null,
  "hypothesis_origin": "missing",
  "evidence": "有",
  "outcome": "未测",
  "turning_point": false,
  "component": "profiler",
  "annotation_method": "研究助理逐项复核",
  "annotation_rationale": "读取 A/B/C 逐 kernel 实测计时；B 耗时占主导。",
  "source": "KernelBench-Hard",
  "unit": "tool_call",
  "session_id": "20260613_042257_claude_claude-opus-4-8_02_kda_cutlass",
  "step_id": 60,
  "raw_file": "data/raw/kernelbench/traces/20260613_042257_claude_claude-opus-4-8_02_kda_cutlass.jsonl",
  "source_locator": "L180",
  "source_line": 180,
  "result_line": 181,
  "source_url": "https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/blob/c2c764c8b5a5fdad493592a2fde1055684e0f064/20260613_042257_claude_claude-opus-4-8_02_kda_cutlass.jsonl",
  "candidate_edit": false,
  "duration_seconds": null
}
```

### 示例 2

```json
{
  "phase": "修改代码",
  "tool": "其他",
  "layer": "attention",
  "hypothesis": "预计算 kd/decay，减少 state kernel 内重复计算",
  "hypothesis_origin": "inferred",
  "evidence": "有",
  "outcome": "未测",
  "turning_point": true,
  "component": "optimizer",
  "annotation_method": "研究助理逐项复核",
  "annotation_rationale": "结合事件60计时和61–66连续 diff 解读；只确认数据先于编辑。",
  "source": "KernelBench-Hard",
  "unit": "tool_call",
  "session_id": "20260613_042257_claude_claude-opus-4-8_02_kda_cutlass",
  "step_id": 61,
  "raw_file": "data/raw/kernelbench/traces/20260613_042257_claude_claude-opus-4-8_02_kda_cutlass.jsonl",
  "source_locator": "L183",
  "source_line": 183,
  "result_line": 184,
  "source_url": "https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/blob/c2c764c8b5a5fdad493592a2fde1055684e0f064/20260613_042257_claude_claude-opus-4-8_02_kda_cutlass.jsonl",
  "candidate_edit": true,
  "duration_seconds": null
}
```

### 示例 3

```json
{
  "phase": "修改代码",
  "tool": "其他",
  "layer": "runtime 与 host 开销",
  "hypothesis": "改变全局 reduction 开关，使 reference 与候选数值对齐",
  "hypothesis_origin": "explicit",
  "evidence": "有",
  "outcome": "未测",
  "turning_point": true,
  "component": "optimizer",
  "annotation_method": "研究助理逐项复核",
  "annotation_rationale": "源码注释与事件58记忆明确说会影响 reference；这是评测污染风险，尚未在隔离进程独立复现。",
  "source": "KernelBench-Hard",
  "unit": "tool_call",
  "session_id": "20260613_153211_claude_claude-opus-4-8_01_fp8_gemm",
  "step_id": 53,
  "raw_file": "data/raw/kernelbench/traces/20260613_153211_claude_claude-opus-4-8_01_fp8_gemm.jsonl",
  "source_locator": "L159",
  "source_line": 159,
  "result_line": 160,
  "source_url": "https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/blob/c2c764c8b5a5fdad493592a2fde1055684e0f064/20260613_153211_claude_claude-opus-4-8_01_fp8_gemm.jsonl",
  "candidate_edit": true,
  "duration_seconds": null
}
```

这些示例来自官方数据的可见动作；不是虚构的示范会话，也不是我们重新运行 kernel 的结果。
