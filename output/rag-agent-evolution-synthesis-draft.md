---
topic_id: rag-agent-evolution
state: distilling
contributors: [claude]
refs: [distill/rag-agent-evolution-1-seed.md, distill/rag-agent-evolution-2-long-context-comparison.md]
next_step: >
  Continue distilling: routing architecture LoE, cost crossover math, memory taxonomy depth.
  Upgrade state to finalized when thread is complete.
---

# RAG in the Multi-Agent Ecosystem
### A synthesis of rungs 1–2 | Feb 2026

---

## The one-line shift

RAG didn't die when context windows hit 1M tokens. It grew up.
It stopped being a pipeline and became the retrieval substrate for the entire agent stack —
knowledge, tools, memory, and conversation history all retrieved through the same core primitive.
The question is no longer *RAG or long context*. It's *how do you fill the context window
with exactly the right information at exactly the right time*.

---

## Part 1 — RAG vs. Long Context: the honest numbers

The benchmark most worth citing: **arXiv 2501.01880** (Jan 2025, 13,628 questions across
Wikipedia, novels, papers, dialogue).

| | Long Context | RAG |
|---|---|---|
| Overall accuracy | **56.3%** | 49.0% |
| Latency (avg) | ~45 seconds | **~1 second** |
| Token cost ratio | ~1250x higher | baseline |
| Avg tokens/request | full document | **~783 tokens** |
| Best on | Dense structured text | Fragmented / dialogue sources |
| Exclusive answers | — | ~10% LC can't answer |

Neither wins universally. The **LaRA benchmark** (2025, 2,326 test cases, 11 LLMs) makes
this formal: optimal choice depends on model capability, context length, task type, and
retrieval quality simultaneously. It's a routing problem, not a preference.

### Why LC doesn't kill RAG

**Lost in the middle.** Even frontier models are only 50–60% accurate on long-context
tasks (Vectara, 2025). Attention is not uniform — facts buried in the middle of a 500k-token
input degrade silently. RAG removes 99.9% of that noise before the LLM sees it.

### Why RAG doesn't saturate

RAG's ceiling is set by retrieval precision, not generation quality. If the right chunk
doesn't rank in the top-k, it never reaches the LLM. Seven named production failure modes
exist (missing content, missed top-ranked, not in context, not extracted, wrong format,
wrong specificity, incomplete). These aren't edge cases — they're the default failure surface.

### The finding that changes the framing

RAG and LC fail on *different* questions. RAG exclusively answers ~10% of questions that
LC misses entirely. This means a pure LC strategy is structurally wrong for some task types
regardless of context window size. You need both.

---

## Part 2 — How they work together

**The pattern: retrieve first, reason long.**

RAG narrows the search space. LC handles deep reasoning over what was retrieved.
- RAG: 1M-token corpus → 783-token focused context
- LC: deep reasoning over that clean context, near LC-level quality at RAG-level cost

[RAGFlow's 2025 year-end review](https://ragflow.io/blog/rag-review-2025-from-rag-to-context)
calls this "retrieval-first, long-context containment" — and puts the cost gap at
two orders of magnitude between naive LC stuffing and full RAG architecture.

### RAPTOR: the bridging architecture

[RAPTOR (arXiv 2401.18059)](https://arxiv.org/abs/2401.18059) is the cleanest example of
RAG leveraging long context at the retrieval architecture level.

At indexing time, build a tree:
- **Leaf nodes** — original chunks (~500 tokens)
- **Mid nodes** — cluster summaries (cross-chunk synthesis)
- **Root nodes** — document or corpus-level summaries

At query time, retrieve from multiple tree levels simultaneously. The LLM sees both
fine-grained facts and high-level context in one prompt.

**Results:**
- GPT-4 + RAPTOR: +20% on QuALITY benchmark over baseline RAG
- 55.7% F1 on QASPER vs DPR's 53.0%
- Summarization-based retrieval: 38.5% accuracy vs 20–21% for flat chunking
- 2025 enhancement ([Frontiers](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1710121/full)):
  semantic chunking + adaptive clustering reduces summary nodes by **76%**

Trade-off: higher indexing token cost. Off by default in RAGFlow. Worth it for multi-hop
Q&A and cross-document synthesis; overkill for point lookups.

---

## Part 3 — The routing layer

This is where the complexity actually lives in 2025–2026. Not the retrieval pipeline itself
— the decision of *which* pipeline to invoke for *which* query.

### SELF-ROUTE (2024 — still the reference baseline)
[arXiv 2407.16833](https://arxiv.org/abs/2407.16833): Ask the LLM if RAG-retrieved chunks
are sufficient. If yes, use RAG answer. If no, escalate to full LC.
Result: LC-comparable quality at fraction of the cost. Binary, no parametric path.

### Self-Routing RAG — SR-RAG ([arXiv 2504.01018](https://arxiv.org/abs/2504.01018), Apr 2025)
Three-way routing in a **single generation pass**:
1. Use parametric knowledge (model already knows it — no retrieval)
2. Retrieve and use
3. Use both

Results vs selective retrieval baselines (four benchmarks, three 7B-class LLMs):
- **+8.5% / +2.1% / +4.7% accuracy**
- **26% / 40% / 21% fewer retrievals**
- No dataset-specific threshold tuning

Key insight: RAG should not always retrieve. The model's own knowledge is a first-class
source. SR-RAG stops leaving it on the table.

### Pre-Route ([OpenReview](https://openreview.net/forum?id=N1E7rFZJGH), 2025)
Route *before* retrieval using lightweight metadata (doc type, length, initial snippets).
Activates dormant routing capabilities in LLMs through structured prompts.
Outperforms Always-RAG, Always-LC, and SELF-ROUTE on LaRA + LongBench-v2.
Distills routing logic to smaller models — cheap routing with large-model decision quality.

### RAGRouter ([arXiv 2505.23052](https://arxiv.org/abs/2505.23052), May 2025)
Learning-based routing across multiple retrieval-augmented LMs, not just binary RAG/LC.
Signals the maturing of routing from heuristics to learned policies.

---

## Part 4 — Where RAG sits in a multi-agent stack

Agents don't use RAG as a standalone feature. They use it for four distinct retrieval jobs:

| Job | What gets retrieved | Notes |
|---|---|---|
| Knowledge retrieval | Domain facts, documents | Traditional RAG |
| Tool selection | Relevant tools from a catalog of 100s | Semantic search over tool descriptions — top-3 only to avoid choice paralysis |
| Episodic memory | Agent's own past experiences and outcomes | Distinct from KB retrieval — what *this agent* did, not what was written about it |
| Semantic memory | General world knowledge, user preferences | Closest to traditional RAG |

The memory taxonomy from cognitive science (episodic / semantic / procedural) maps onto
distinct retrieval stores with different update dynamics:

- **Semantic** — nearest to traditional RAG; retrieve facts from a KB
- **Episodic** — retrieve what this agent experienced; parametric knowledge won't have it
- **Procedural** — retrieve how to do things; hardest to implement; closest to skills/tools

[arXiv 2502.06975](https://arxiv.org/pdf/2502.06975) makes the key distinction:
RAG retrieves external knowledge. Episodic memory retrieves what *this agent* experienced.
Conflating them is a design mistake — they need different stores, different retrieval
strategies, and different update mechanisms.

**Efficiency finding:** memory-augmented approaches reduce token usage by over 90% vs naive
context appending while maintaining competitive accuracy. The main argument for structured
memory isn't intelligence — it's cost.

---

## Part 5 — Context Engineering: the umbrella frame

[LangChain's context engineering post](https://blog.langchain.com/context-engineering-for-agents/)
(Dec 2025) names the discipline that contains all of this:

> "The art and science of filling the context window with just the right information
> for the next step."

Four primitives:

| Primitive | Role | RAG in it |
|---|---|---|
| **Write** | Persist info outside the window | Writes to memory stores that RAG will later select from |
| **Select** | Pull relevant info back in | **This is RAG** — KB, memory, tool catalog, conversation history |
| **Compress** | Reduce token footprint | Summarization, trimming; RAPTOR operates here at indexing time |
| **Isolate** | Split context across agents | Multi-agent RAG with scoped retrieval per agent |

RAG is the **Select** primitive. But a complete agent system needs all four.
RAG alone doesn't handle what to write, how to compress, or when to isolate.
The pipeline is not the system.

---

## Part 6 — Level of effort, honestly

### What the tutorials show you
- Chunk documents → embed → store in vector DB → semantic search → generate
- Working in 1–2 weeks on clean documents

### What production actually costs

**Before launch:**
- Retrieval testing (50–100 test queries, Precision@10, Recall@10): 2–3 weeks
- Generation testing (groundedness, hallucination detection): 1–2 weeks
- End-to-end with real user patterns: 1–2 weeks
- **Total: 4–7 weeks of validation alone**, before any monitoring infrastructure

**Seven architectural decisions** each carrying hidden complexity:
chunking strategy, embedding model, retrieval approach (hybrid BM25 + vector), reranking,
context management, evaluation framework, fallback handling.

**The most common production mistake:** optimizing generation when retrieval is broken.
Poor retrieval makes good prompts irrelevant. Measure retrieval separately first.

**Contextual retrieval (Anthropic):** adding explanatory context per chunk at indexing time
drops retrieval failure rate: 5.7% → 3.7% → 2.9% → 1.9% through successive improvements.
One-time cost: $1.02 per million document tokens. One of the highest-ROI interventions.

### When to go agentic

Don't, until vanilla RAG demonstrably fails at one of these:
- Multiple heterogeneous data sources needing different retrieval strategies
- Multi-step reasoning (question decomposition, iterative retrieval)
- Async research tasks where the retrieval plan must adapt mid-flight

Agentic patterns add latency, debugging complexity, and cost. The routing layer
(SR-RAG, Pre-Route) is the first step of agentic complexity worth investing in.

---

## Decision framework for 2026

```
Is corpus > context window?
  → YES → RAG required (hard limit)
  → NO  → Is query latency SLO < 5s?
           → YES → RAG (1s vs 45s)
           → NO  → Is per-request token cost acceptable?
                    → YES → LC is fine; add SELF-ROUTE to save cost
                    → NO  → RAG
  Does data governance require minimizing external exposure?
  → YES → RAG (send only relevant chunks, not full docs)

For all enterprise multi-document / heterogeneous corpora in 2026:
→ Hybrid retrieval (BM25 + vector + optional graph) by default
→ Smart routing (SR-RAG or Pre-Route) on top
→ RAPTOR for multi-hop / cross-document synthesis tasks
→ Long context reserved for full-document reasoning (contracts, novels, code repos)
```

---

## What remains open

1. **Cost crossover math.** Everyone agrees RAG is ~1250x cheaper — but this ratio shifts
   with model pricing. At current Gemini 2.0 / GPT-4o pricing, where does the crossover
   sit for a 10M-token corpus at 10k queries/day? No recent paper publishes this with
   current API prices.

2. **Routing quality under distribution shift.** SR-RAG and Pre-Route have strong benchmark
   results. No production postmortem exists on how routing degrades when query patterns
   diverge from training distribution.

3. **RAPTOR indexing cost at scale.** 76% node reduction helps. Absolute cost for a
   10M-document corpus with RAPTOR remains unpublished.

4. **Memory taxonomy implementation depth.** Episodic / semantic / procedural are
   architecturally distinct — but what does a production system that correctly implements
   all three actually look like? MIRIX (arXiv 2507.07957) proposes six components.
   No independent evaluation of that architecture yet.

---

## Active projects worth watching

| Project | Stars | What it does |
|---|---|---|
| [Dify](https://github.com/langgenius/dify) | 114k | Visual RAG + agent workflow builder |
| [RAGFlow](https://github.com/infiniflow/ragflow) | 70k | Deep document understanding, enterprise RAG |
| [LightRAG](https://github.com/HKUDS/LightRAG) | active | Graph + vector hybrid (EMNLP 2025) |
| [RAG-Anything](https://github.com/HKUDS/RAG-Anything) | 13.8k | Multimodal RAG built on LightRAG |
| [microsoft/graphrag](https://github.com/microsoft/graphrag) | active | Graph-based RAG, knowledge graph reasoning |
| [Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) | — | Memory survey covering HippoRAG, GraphRAG, MemTool |

---

*This is a mid-thread synthesis. Rungs 1–2 complete. Thread continues.*
