# Part 9 — Evaluating and Monitoring Your Agent in Production

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate–Advanced
> **Docs:** [Agent development lifecycle](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle) | [Monitor agents dashboard](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)

---

## Introduction

<!-- Write intro here. Angle: shipping is the beginning. Close the loop with evaluation and monitoring so you know when your agent degrades. -->

---

## Why evaluation is different for agents

- **Non-deterministic outputs**

  > You can't use `assert response == "expected string"`. The same question asked twice may get different phrasings of a correct answer. Evaluation requires scoring criteria, not exact matching.

- **Multi-turn conversations**

  > Quality at turn N depends on the full conversation history. An agent can give a correct answer to turn 1 but a wrong answer to turn 5 because it lost track of context. Your eval dataset needs multi-turn examples, not just single Q&A pairs.

- **Tool calls add a new failure surface**
  > An agent can fail in three distinct ways: (a) wrong final answer, (b) correct answer but wrong tool called, (c) correct tool called but with wrong arguments. A good eval suite covers all three.

---

## Evaluation strategies

- **LLM-as-judge**

  > Use a second model (typically larger/slower) to score the agent's responses against criteria. Examples: "Is the response factually correct?", "Did the agent stay on topic?", "Was the tone appropriate?" Score 1–5 or pass/fail. Foundry has built-in LLM-as-judge evaluators.

- **Groundedness**

  > Specifically relevant for RAG agents (File Search, Azure AI Search). Did the response stay faithful to the retrieved documents, or did the agent hallucinate? Foundry has a built-in groundedness evaluator.

- **Task completion**

  > Did the agent actually do the thing the user asked? This is harder to automate and often requires human review or a custom evaluator.

- **Human review: when automated eval isn't enough**

---

## Foundry's built-in evaluators

From the Foundry development lifecycle docs, the platform supports three evaluation modes:

- **Trace-based evaluation** — evaluate specific runs from traces
- **Dataset-based evaluation** — run a golden dataset through the agent and score in bulk
- **Continuous evaluation** — sample live production traffic and evaluate automatically

> All accessible from the Foundry portal under your project's Evaluation section.

---

## Code: Run an evaluation

<!-- Prepare a golden dataset, run the agent against it, score with LLM-as-judge, review in portal -->

```python
# agent_evaluation.py — evaluation pipeline goes here
```

```jsonl
# golden_dataset.jsonl — example entries:
# {"input": "What is the status of order 1234?", "expected_tool": "get_order_status", "expected_args": {"order_id": "1234"}}
```

---

## Continuous evaluation on live traffic

- **Sample production runs for evaluation**

  > Don't eval every run — it's expensive. Sample 5–10% of production traffic and run evaluators against it. Set up alerts when scores drop below a threshold.

- **Alert on score degradation**
  > Connect evaluation scores to Application Insights alerts. A sudden drop in groundedness score, for example, often signals that your data source has changed and the agent is hallucinating to compensate.

---

## Monitoring with Application Insights

- **What Foundry emits via OpenTelemetry**

  > Foundry Agent Service automatically emits traces when connected to Application Insights. Every model call, tool invocation, and run lifecycle event is a span. You get error rate, latency, token usage, and tool call success rate out of the box.

- **Key metrics to watch**

  > Error rate, run latency (p50/p95), token usage per run, tool call success rate, groundedness score trend.

- **Wiring up alerts**

---

## Custom agent monitoring (agents not hosted on Foundry)

- **Register via Foundry Control Plane**
  > For agents running outside Foundry (your own process, a different platform), register them in Foundry Control Plane and route through AI Gateway. Send OTel traces to the same Application Insights resource. You get unified observability across Foundry-hosted and external agents in one dashboard.

---

## The full development lifecycle

From docs, the lifecycle is: **Create → Test → Trace → Evaluate → Optimize → Publish → Monitor**

Parts 1–8 covered Create through Publish. This part closes the loop on Trace, Evaluate, and Monitor.

> The **Agent Optimizer** (available in the portal) can automatically improve agent instructions based on evaluation results — a good "next steps" pointer for readers who want to go further.

---

## Summary

<!-- 2–3 sentence wrap-up. This is the final post — round off the series. -->

**Key takeaway:** An agent you can't measure is an agent you can't trust in production.

---

## Series wrap-up

You've now covered the full journey:

| Part | Topic                                           |
| ---- | ----------------------------------------------- |
| 1    | First agent — the managed loop                  |
| 2    | Built-in tools — web, code, files               |
| 3    | Function calling — custom dispatch              |
| 4    | OpenAPI tools — any REST API                    |
| 5    | MCP server — reusable, framework-agnostic tools |
| 6    | Toolboxes — centralised tool management         |
| 7    | Skills — org-scale discoverability              |
| 8    | Multi-agent — agents calling agents             |
| 9    | Eval & monitoring — close the loop              |
