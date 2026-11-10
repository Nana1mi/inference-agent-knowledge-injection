# 检索与证据边界

日期：2026-11-10（Asia/Hong_Kong），截止同日；范围：2025–2026公开材料。研究助理单人（AI）叙述性/范围综述；没有声称PRISMA系统综述，也没有用网页命中数估计纳入研究数。

## 实际检索

1. 起点逐项：PLAN列出的全部arXiv ID与Apple仓库；分别取abstract和HTML全文，MetaInfer明确取v1/v3。官方博客取Together PDF。URL与时间逐请求保存在 [manifest](../data/raw/manifest.jsonl)。arXiv串行且间隔不短于3秒；没有用镜像/缓存弥补失败。
2. Web发现式检索，完整或可用的结果快照保存于 [search目录](../data/raw/search/)。查询包括：
   - `"SEIS" "Self-Evolving Inference Systems"`
   - `"Together Compiler" continual compilation knowledge`
   - `"KernelSeek" "Ask"`；`"KernelSeek" github`；`"KernelSeek" "github.com" "Oliaro"`；`"KernelSeek" repository`
   - `"InferenceBench" agent`；`"VibeSys" github skills`；`"ISO-Bench" github`
   - `"coding agents" "AGENTS.md" evaluation context files 2026`
   - `coding agent memory RAG skills ablation 2025 2026`（arxiv.org过滤）
   - `"KernelBench" "traces" public 2025`；`"OpenEvolve" "logs" kernel optimization 2025`；`"OpenEvolve" "GPU" "logs"`
   - `"coding agents" "retrieval" "ablation" "2025" memory`
   - `"Agentic Context Engineering" 2510.04618`
   - `"Context Rot" Chroma research`
3. 二级学术索引Semantic Scholar：`coding agent retrieval augmented memory ablation`、`agent skills context files coding`，2025–2026，limit=10；两次均HTTP429，未取得结果，**不能记为无相关论文**。脚本 [search_scholar.py](../scripts/search_scholar.py) 和请求记录 [scholar_queries.json](../data/raw/search/scholar_queries.json)。
4. GitHub/HuggingFace官方树、README、数据卡用于查artifact与许可，不当作独立效果实验。arXiv正文定位后的链接再核验；网页、摘要或第三方新闻仅用于发现，不用于替代受控结果。
5. Context7按resolve→query查opencode非交互JSON输出、PyTorch数值开关、Pier任务运行/轨迹；作为接口事实核验，**不计入文献效果对照**。上游dev文档与本地版本不保证完全一致。
   查询与文档URL的提取笔记见 [api_docs_notes.json](../data/extractions/api_docs_notes.json)，该文件明确是笔记而非伪装的原始API响应。

## 纳入与排除

- PLAN强制工作全部列入T1/T3；无独立知识消融者单列架构/行为线索。
- 补充效果研究仅采用已取得正文、可定位对照/消融和结果的AGENTS.md、Two-Agent、Stale、CODESKILL、Demystifying、ACE、Context Rot。后两者保留跨领域限制。
- CAMG-RL等搜索中出现但未完成本文所需消融全文提取的工作不作为证据；社区帖子、二手解读、商业平台对论文的自动评分不纳入。
- SEIS论文与项目README链接的早期scaffold分开；MetaInfer两个版本分开；InferenceBench论文main pool、网站leaderboard、atlas三种分母分开。

没有完整、去重的多数据库导出，Semantic Scholar又限流，因此不报告“所有符合条件研究已覆盖”。缺失全文/原始轨迹列PROGRESS，不以“未定位”断言“未发布”。证据ledger中的每行是提取记录，不是互相独立研究；版本与同一研究附录不能当作重复样本。
