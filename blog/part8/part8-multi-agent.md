# Part 8 — Multi-Agent: Agents Calling Agents

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate–Advanced
> **Docs:** [Agent-to-Agent (A2A) tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent)

---

## Introduction

<!-- Write intro here. Angle: not every problem fits in one agent. Learn when splitting makes sense and how to wire agents together properly. -->

---

## When does multi-agent actually make sense?

- **Specialisation: different system prompts, tools, models per domain**
- **Scale: parallelism, independent scaling**
- **Governance: different auth boundaries per agent**
- **Red flags: complexity for its own sake**
  > Multi-agent adds latency (each agent-to-agent call is a network hop), cost (multiple model inference calls), and debugging complexity. Don't split unless you have a concrete reason.

---

## A2A tool vs. multi-agent workflows

This is an important distinction the docs make explicitly:

- **Using the A2A tool:**

  > Agent A calls Agent B, gets the answer back, then Agent A summarises and responds to the user. Agent A stays in control and handles all subsequent user input.

- **Using a workflow:**

  > Agent B takes full responsibility — Agent A hands off entirely and is out of the loop. Agent B handles all subsequent user input. See [Build a workflow in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/workflow).

- **Important migration note for readers who've seen older Foundry docs:**
  > _"The Connected Agents tool from the previous (classic) Agents API isn't available in the new Foundry Agent Service."_ The old `agent.as_tool()` pattern is gone. The replacement is the A2A tool (this part) or Workflows. Many tutorials still show the old pattern — worth calling this out explicitly.

---

## Patterns

- **Orchestrator + specialists (most common)**
- **Peer-to-peer handoff**
- **Fan-out / fan-in (parallel sub-tasks)**

---

## How A2A works in Foundry

- **Expose an agent as an A2A endpoint**

  > A Foundry agent can be exposed as an A2A-compatible endpoint via **Enable incoming A2A** on the agent. The agent gets a stable URL. Foundry generates an agent card at `/.well-known/agent-card.json` describing capabilities.

- **Create an A2A connection**

  > Before adding the A2A tool, create a project connection pointing to the sub-agent's A2A endpoint. This stores the auth details. Auth options: key-based, managed identity, OAuth OBO, project managed identity.

- **Add the A2A tool to the orchestrator**
  > `A2APreviewTool(project_connection_id=a2a_connection.id)` added to the orchestrator's tools list. The orchestrator calls the sub-agent like any other tool, passing natural language input.

---

## Code: Create two specialist agents

```python
# research_agent: Bing Grounding + File Search
# writer_agent: optimised system prompt for drafting content
# code goes here
```

---

## Code: Create an orchestrator agent

```python
# orchestrator with both specialists registered as A2A tools
# code goes here
```

---

## Code: Run an end-to-end task

<!-- User asks for a researched blog post. Orchestrator calls research_agent, passes results to writer_agent. -->

```python
# end-to-end multi-agent run goes here
```

---

## Calling non-Foundry agents

- **The A2A protocol is open — any A2A-compatible endpoint works**
  > You're not limited to Foundry agents. Any agent implementing the A2A spec ([a2a-protocol.org](https://a2a-protocol.org/latest/)) can be called. You can also register external A2A agents in Foundry Control Plane for centralised governance and observability.

---

## Durable orchestration for long-running tasks

- **Azure Durable Functions + SignalR for agents that survive restarts**

  > Agents that pause for hours or days (e.g. waiting for human approval) need durable state. Azure Durable Functions provides checkpointed execution — if the process restarts, the workflow resumes from the last checkpoint. SignalR handles real-time notification when the agent resumes.

- **Human-in-the-loop approval gates**
  > Pattern: agent produces a proposed action → pauses → sends notification → human reviews and approves/rejects → agent continues. This is the `require_approval` pattern at the workflow level rather than per-tool call.

---

## Observability across agents

- **Tracing a request across multiple agent runs**

  > Each agent run generates its own trace. Cross-agent tracing requires propagating trace context (W3C TraceContext headers). Foundry's built-in tracing handles this automatically when using the A2A tool — you get end-to-end traces in Application Insights.

- **OpenTelemetry and Application Insights**

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** Multi-agent is a design choice, not a default — use it when isolation or specialisation genuinely earns its complexity.

**Next:** [Part 9 — Evaluating and Monitoring Your Agent in Production](./part9-evaluation-monitoring.md)
