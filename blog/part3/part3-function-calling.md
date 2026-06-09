# Part 3 — Custom Tools with Function Calling

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate
> **Docs:** [Function calling](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/function-calling)

---

## Introduction

<!-- Write intro here. Angle: this is the foundation of everything custom. Understand this and the rest of the series makes sense. -->

---

## How function calling works

- **You define the tool schema (name, description, parameters as JSON Schema)**

  > The schema is what the model reads to understand what the tool does and when to use it. It's not code — it's a description. The model never sees your actual function implementation.

- **The LLM decides when to call it and with what arguments**

  > The model outputs a _tool call request_ (structured JSON with tool name + arguments) rather than a text response. The run enters `requires_action` status and pauses, waiting for you to execute the function and return the result.

- **You execute the function and return the result**

  > This is the critical distinction from built-in tools: **you** are responsible for executing the function. Foundry dispatches the request and waits. Your function can do anything — database query, API call, file read, calculation.

- **The LLM incorporates the result into its reply**
  > Once you submit the tool output, the run continues. The model sees the result as context and generates its final response. The entire loop (model → tool call → your code → model) is one run.

---

## Why description quality matters

<!-- Write section here — this is the thing most tutorials skip -->

- **The LLM reads your description to decide whether to use the tool**

  > The `description` field is the most important thing you write. The model uses it to decide: (a) whether this tool is relevant, and (b) when to call it vs. another tool. Vague descriptions = wrong tool called = wrong answers.

- **Good vs. bad tool descriptions**
  > **Bad:** `"Gets order info"` — too vague, model can't judge when to use it.
  > **Good:** `"Returns the current status and estimated delivery date for a given order ID. Use this when the user asks about a specific order."` — tells the model exactly when and why.
  > From official docs tip: _"In your agent instructions, describe what each tool is for and when to use it."_

---

## Define a tool schema

<!-- Write section here -->

- **JSON Schema structure**

  > The schema follows standard JSON Schema: `type`, `properties`, `required`. The model reads `description` at both the function level and per-parameter level. Good per-parameter descriptions help the model extract the right argument from natural language.

- **Required vs. optional parameters**

  > List only truly required params in `required`. Optional params should have defaults your code handles. Don't make the model guess values it shouldn't have to provide.

- **Enum types for constrained inputs**
  > Use `"enum": ["pending", "shipped", "delivered"]` for parameters with a fixed set of values. This prevents the model from hallucinating invalid values.

```python
# tool schema definition goes here
```

---

## Code: Register a function tool on an agent

<!-- Write section here -->

```python
# agent creation with function tool goes here
```

---

## Code: Handle tool calls in the run loop

<!-- This is the core mechanic — worth going step by step -->

- **Poll for `requires_action` status**

  > After submitting a message, poll the run status. When status is `requires_action`, the model has produced tool call requests. The `run.required_action.submit_tool_outputs.tool_calls` list contains one or more tool calls to execute.

- **Extract the tool name and arguments**

  > Each tool call has `function.name` (the tool to call) and `function.arguments` (a JSON string). Parse the arguments with `json.loads()`.

- **Execute your function**

- **Submit the tool output back to the run**
  > Call `project.agents.submit_tool_outputs_to_run(...)` with a list of `ToolOutput` objects — one per tool call, matched by `tool_call_id`. The run then continues from where it paused.

```python
# run loop with tool call handling goes here
```

---

## Code: A realistic example

<!-- get_order_status(order_id) — simulated lookup in a local dict -->

```python
# realistic function calling example goes here
```

---

## Multiple functions on one agent

<!-- Add a second tool: list_recent_orders(customer_id) -->

- **The agent decides which to call and when**
  > This is where clear descriptions pay off. With two tools, the model needs to understand which to pick. Add a decision rule to the system prompt: e.g. "Use `list_recent_orders` when the user doesn't have a specific order ID. Use `get_order_status` when they provide an order ID."

```python
# multi-function agent goes here
```

---

## Error handling

- **What happens if your function throws?**

  > Catch exceptions inside your function and return an error string as the tool output. Don't let exceptions propagate — a crashed tool call leaves the run in `requires_action` permanently.

- **Returning an error message vs. raising**
  > Return a descriptive error string (e.g. `"Order 1234 not found"`) so the model can communicate it to the user gracefully. The model handles error outputs well and will typically inform the user and ask for clarification.

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** Function calling is a dispatch pattern — the LLM routes, you execute.

**Next:** [Part 4 — OpenAPI Tools: Connect Your Agent to Any REST API](./part4-openapi-tools.md)
