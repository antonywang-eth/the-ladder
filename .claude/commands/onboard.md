You are orienting a new contributor to the-ladder. Walk them through the repo structure, philosophy, and workflows clearly.

## What this repo is

The-ladder is a **thinking pipeline for AI research**. Each topic moves through a structured distillation process: raw note → seed → rungs of reasoning → synthesis output. The goal is not a literature review — it's a position. Every rung should take a stance, not just summarize.

## Directory structure

```
intake/          Raw notes and seeds for new topics
distill/         The thinking pipeline — one file per rung per topic
output/          Final synthesized reading files (produced by /study or /research)
.claude/commands/ Skills (this file lives here)
STATUS.md        Auto-generated list of active threads
```

### File naming conventions

**Intake:**
```
intake/[topic-id]-raw.md
```

**Distill rungs:**
```
distill/[topic-id]-[N]-[short-desc].md
```
e.g. `distill/rag-agent-evolution-2-long-context-comparison.md`

**Output:**
```
output/[topic-id]-[type].md
```
e.g. `output/multi-agent-benefits-reading.md`

### Frontmatter every distill file must have

```yaml
---
topic_id: rag-agent-evolution
state: distilling          # or: complete
contributors: [claude]
refs: [distill/rag-agent-evolution-1-seed.md]
next_step: >
  What you want the next agent to do — be specific.
---
```

## The two main workflows

### 1. Study and contribute to an existing thread → `/study [topic]`

Use when you want to read an existing thread and add a rung. The skill will:
- Orient you in STATUS.md and distill/
- Have you read rungs in order
- Ask you to assess what's settled vs. open
- Have you write the next rung or a synthesis

### 2. Deep research on a new or existing topic → `/research [topic]`

Use when a topic needs substantial new research before you can write a rung. The skill dispatches parallel Opus agents (one per perspective), waits for results, synthesizes them into a reading file in `output/`, and optionally seeds a new distill thread.

## Commit format

Always use the structured format:
```
[topic-id] distilling | rung N | short description
```

Examples:
```
[rag-agent-evolution] distilling | rung 2 | RAG vs long context, routing layer
[multi-agent-benefits] distilling | rung 1 | seed: three structural mechanisms
```

For output files:
```
[topic-id] output | synthesis | short description
```

## What makes a good rung

- **Takes a position.** "The evidence supports X" not "some say X, others say Y."
- **Has a specific next_step.** The next agent should know exactly what to do.
- **Refs what it builds on.** Always link to the files you read.
- **Is honest about gaps.** Name what's unsettled rather than papering over it.

## Active topics (check STATUS.md for current state)

- `rag-agent-evolution` — RAG vs. long context, routing layer, context engineering
- `multi-agent-benefits` — multi-agent architecture benefits, hallucination/bias correction

## Quick start

To pick up an existing thread:
```
/study rag-agent-evolution
```

To start a new topic from scratch:
```
/research [your topic]
```

To do a deep dive with parallel agents before writing:
```
/research multi-agent architecture benefits
```
