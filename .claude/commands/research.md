You are running a deep parallel research session on a topic in the-ladder. This is the workflow for when a topic needs substantial new evidence before you can write a distill rung.

## When to use this skill

Use `/research` when:
- Starting a new topic that has no existing distill thread
- A distill rung's `next_step` requires gathering new evidence from recent papers or articles
- You want to study a topic from multiple angles simultaneously before synthesizing

Use `/study` instead when you just want to read and extend an existing thread.

## Step 1: Frame the research scope

Break the topic into 2–3 distinct perspectives that can be researched independently. Good splits:
- By angle: benefits vs. failure modes vs. mechanisms
- By domain: theory vs. production vs. benchmarks
- By timeframe: foundational work vs. 2025–2026 latest

Bad splits: overlapping questions that will produce duplicated results.

## Step 2: Dispatch parallel Opus agents

Launch one agent per perspective using the Task tool with:
- `subagent_type: general-purpose`
- `model: opus`
- `run_in_background: true`

Each agent prompt should:
- State exactly what perspective it owns
- List what's already known (so it doesn't re-cover it)
- Give specific WebSearch queries to run
- Ask for structured output: paper title + ID/URL + date + key finding (with numbers) + why it matters
- Specify a target count (3–6 sources per agent)
- Specify date ranges when targeting recent work (e.g., "Feb–March 2026 only")

## Step 3: Wait and synthesize

Wait for all agents to complete. When they do:
- Read each result
- Identify cross-cutting themes
- Note where agents agree, contradict, or complement each other
- Build a combined summary before writing any files

## Step 4: Write a reading file

Create `output/[topic-id]-reading.md` with required frontmatter:

```yaml
---
topic_id: <id>
state: distilling
contributors: [claude]
refs: [distill/<files-you-read>.md]
next_step: >
  What the next agent should do with this research.
---
```

Structure the reading file with clear parts (one per perspective) plus a synthesis section. Each part should:
- State the key finding directly — don't bury the lede
- Include specific numbers where available
- Name what's well-evidenced vs. still open
- Be honest about gaps

## Step 5: Seed or extend a distill thread

If this is a new topic:
- Create `intake/[topic-id]-raw.md` with the raw question
- Create `distill/[topic-id]-1-seed.md` with a position, not a summary

If extending an existing thread:
- Create `distill/[topic-id]-[N+1]-[short-desc].md`
- Reference the reading file in `refs`

## Step 6: Validate and commit

Always run the validator before committing:
```
python3 .github/scripts/validate_and_update.py
```

Fix any frontmatter errors before pushing.

Commit format:
```
[topic-id] distilling | rung N | short description
```

## Example agent prompt structure

```
You are a research agent studying [perspective]. Pure research only — no file writes.

**Already covered (do NOT re-include):**
- [list existing papers]

**Search queries:**
- "[specific query 1]"
- "[specific query 2]"

For each source found:
- Title + arXiv ID or URL
- Date (must be [date range])
- Key finding in 2-3 sentences with specific numbers
- Why it matters for [framing]

Return [N] sources. Prioritize recency and specificity over breadth.
```

## Tips

- 3 agents in parallel is the sweet spot — enough diversity, manageable synthesis
- Give each agent a tight scope; broad prompts produce overlap
- For Feb–Mar 2026 papers: always ask the agent to verify the submission date directly on arXiv
- Separate "papers" agents from "industry articles" agents — they search differently
- The synthesis is more important than any individual agent's output — look for what all three agree on
