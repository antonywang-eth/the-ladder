# Raw Note: Multi-Agent Architecture Benefits

**Topic:** Multi-agent architecture through the lens of its benefits — particularly
bias correction and hallucination correction in LLMs.

**Why this matters:**
Single-agent reliability improvements (better prompting, CoT, fine-tuning, RAG) all
reduce error rates but don't change the *type* of error. The model is still one model
failing in correlated ways. Multi-agent introduces structurally different failure modes.

**Core question:**
What does multi-agent architecture *uniquely enable* that single-agent cannot achieve
with better prompting or more compute? Is the benefit just redundancy (vote), or is
there something deeper (adversarial grounding, specialization, separated concerns)?

**Papers/concepts to track:**
- Self-Consistency (Wang et al., 2022) — sample CoT paths, majority vote
- LLM Debate (Du et al., arXiv 2305.14325, 2023) — multiagent debate improves factuality
- Self-Refine (Madaan et al., 2023) — iterative self-improvement with feedback
- Mixture-of-Agents (TogetherAI, arXiv 2406.04692, 2024) — hierarchical aggregation
- Constitutional AI (Anthropic, 2022) — critic/reviser loop
- ChatEval (Chan et al., 2023) — multi-agent for evaluation quality
- MAD (Multi-Agent Debate) — reduces sycophancy
- MetaGPT — structured agent role separation
- AutoGen (Microsoft, 2023)

**Open tensions:**
- Does multi-agent debate just converge on the dominant agent's view (echo chamber)?
- Sycophancy: do RLHF-trained agents just agree with the most confident peer?
- Adversarial agents that are the same model with same biases — are errors truly non-correlated?
- Cost: is multi-agent reliability worth the 3-10x latency/token overhead vs. self-consistency sampling?
