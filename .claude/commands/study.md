You are entering this repo as a contributor who wants to study AI topics. Follow these steps:

## 1. Orient yourself

Read `STATUS.md` to see what threads are active. Then scan `distill/` for any files related to $ARGUMENTS. If `$ARGUMENTS` is empty, look for any open `distilling` threads and pick the most active one.

## 2. Read the thread

For the topic you've chosen:
- Read every file in `distill/` for that topic, in rung order (lowest to highest step number)
- Follow the `refs` — if a file refs something from another topic, read that too
- Check `output/` to see if a synthesis already exists

## 3. Assess the state of the thread

After reading, report:
- **What the thread is about** — one sentence
- **Where it stands** — what's been established, what's contested, what's unresolved
- **What `next_step` the latest rung is asking for**
- **Your honest read** — do you agree with the direction? Is there a gap, a counterpoint, or a synthesis waiting to happen?

## 4. Decide what to contribute

You have four options:
- **Expand** — build on the latest rung's reasoning
- **Counterpoint** — push back on something established in the thread
- **Synthesize** — if the thread has enough signal, write the output
- **Fork** — if you see a distinct sub-question worth separating out, start a new topic_id

If $ARGUMENTS specifies a direction (e.g. "counterpoint", "synthesize", "expand on rung 3"), follow that.

## 5. Write your contribution

Create `distill/[topic-id]-[N+1]-[short-desc].md` with valid frontmatter:

```yaml
---
topic_id: <id>
state: distilling
contributors: [claude]
refs: [distill/<file-you-read>.md]
next_step: <what you want the next agent to do>
---
```

Then write your contribution. Be direct. Take a position. Don't hedge everything — this is a thinking pipeline, not a literature review.

## 6. Commit

Use the structured format:
```
[topic-id] distilling | rung N | short description
```

Then push to main.

---

If no threads exist yet, seed one: drop your topic into `intake/` as a raw note, then create `distill/[new-topic-id]-1-seed.md` to frame the question. Set `next_step` to what kind of thinking would be most useful next.
