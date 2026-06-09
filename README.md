# Building Production AI Agents on Azure AI Foundry

Sample code for a hands-on blog series that takes you from zero to production-ready AI agents using **Azure AI Foundry Agent Service** and the `azure-ai-projects` Python SDK. Each part introduces a concept and builds working code — written in order, each part builds on the last.

## Prerequisites

- An Azure subscription with an AI Foundry project
- A model deployed in that project (GPT-4o recommended from Part 2 onwards)
- Python 3.11+, [uv](https://docs.astral.sh/uv/)

## Getting Started

```bash
uv sync
cp .env.example .env   # fill in PROJECT_ENDPOINT and MODEL_NAME
uv run python src/part1/agent_hello.py
```

## The Series

### Part 1 — Your First Agent

Build a minimal agent with a system prompt and run a conversation from the terminal. Covers authentication, the `AIProjectClient`, versioned agent creation, and the Responses API.

### Part 2 — Built-in Tools: Search, Code Interpreter, and File Search

Get as far as possible without writing custom code. Add web search, a Python sandbox, and document Q&A to an agent using Foundry's managed tools.

### Part 3 — Custom Tools with Function Calling

The foundation of everything custom. Define a tool schema, handle the `requires_action` dispatch loop, and execute your own functions in response to model requests.

### Part 4 — OpenAPI Tools: Connect Your Agent to Any REST API

Point an agent at an OpenAPI spec and let Foundry make the HTTP calls. No glue code per endpoint — if it has a spec, your agent can call it.

### Part 5 — Building a Custom MCP Server with Azure Functions

Build a remote MCP server on Azure Functions and connect it to a Foundry agent. MCP is the open standard for agent tool connectivity — build once, reuse from any MCP-compatible client.

### Part 6 — Foundry Toolboxes: Manage Tools Once, Use Everywhere

Bundle tools into a single versioned endpoint. Toolboxes centralise credentials, enable tool governance, and let any agent consume the same tools without duplicating configuration.

### Part 7 — Skills and the `azure-ai-projects` SDK

Register named, versioned capabilities at the project level. Skills are the registry layer on top of tools — define once, reference from any agent, and make tooling discoverable across teams.

### Part 8 — Multi-Agent: Agents Calling Agents

Build an orchestrator agent that delegates to specialist sub-agents via the Agent-to-Agent (A2A) protocol. Covers when multi-agent is worth the complexity and how to maintain observability across agent hops.

### Part 9 — Evaluating and Monitoring Your Agent in Production

Close the loop. Build an evaluation pipeline using LLM-as-judge and groundedness scoring, wire up Application Insights tracing, and set up continuous monitoring against live traffic.

## Repository Structure - Example code

```
src/
  part1/   agent_hello.py              — minimal agent, Responses API  ✅
  part2/   agent_builtin_tools.py      — web search, code interpreter, file search  🚧 coming soon
  part3/   agent_function_calling.py   — custom function tools  🚧 coming soon
  part4/   agent_openapi_tool.py       — OpenAPI tool + spec  🚧 coming soon
  part5/   agent_mcp_server/           — Azure Functions MCP server  🚧 coming soon
  part6/   agent_toolbox.py            — Foundry Toolboxes  🚧 coming soon
  part7/   agent_skills.py             — Skills preview API  🚧 coming soon
  part8/   multi_agent_orchestrator.py — A2A multi-agent  🚧 coming soon
  part9/   agent_evaluation.py         — evaluation + monitoring  🚧 coming soon
```
