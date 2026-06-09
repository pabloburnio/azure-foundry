# Part 6 — Foundry Toolboxes: Manage Tools Once, Use Everywhere

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate
> **Docs:** [Create and use a Foundry Toolbox](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)

---

## Introduction

<!-- Write intro here. Angle: you now have multiple tools. Toolboxes let you bundle them, handle auth centrally, and point any agent at the same endpoint. -->

---

## The problem Toolboxes solve

- **Adding the same tool to 10 agents means 10 places to update credentials**

  > Without Toolboxes, every agent definition independently configures its tools and auth. Rotate an API key and you update 10 agents. Add a new tool and you update 10 agents.

- **From the docs, the specific problems named are:**
  > _"Tool Duplication: Teams re-implement the same tools independently. Credential Sprawl: Credentials get duplicated across multiple agents. Governance Gaps: Little visibility into what tools exist or who's using them. Integration Bottleneck: Developers stall waiting for tool integration."_

---

## How Toolboxes work

- **A Toolbox exposes a single MCP-compatible endpoint**

  > The Toolbox itself is an MCP server. Any MCP-capable agent runtime can consume it — Foundry Agent Service, LangGraph, Microsoft Agent Framework, GitHub Copilot SDK, custom code. Toolboxes are not Foundry-specific.

- **Versioning: immutable snapshots with explicit promotion**

  > Each Toolbox version is an immutable snapshot. Creating a new version doesn't automatically promote it. You test against the version-specific endpoint, then promote to `default_version` when ready. Agents using the consumer endpoint automatically pick up the new default — no agent code changes.

- **Two endpoint patterns**

  > **Developer endpoint** (version-specific): `{project_endpoint}/toolboxes/{name}/versions/{version}/mcp?api-version=v1` — use for testing.
  > **Consumer endpoint** (always serves default): `{project_endpoint}/toolboxes/{name}/mcp?api-version=v1` — use in agent definitions.

- **Required header**
  > Every request must include `Foundry-Features: Toolboxes=V1Preview`. Easy to miss — causes silent failures.

---

## What can go in a Toolbox?

Full list: Web Search, Azure AI Search, Code Interpreter, File Search, OpenAPI tools, MCP servers, Agent-to-Agent (A2A), Fabric IQ, Work IQ, Browser Automation.

- **One unnamed tool per type limit**
  > You can only have one unnamed instance of each tool type. To add multiple Azure AI Search indexes, give each a `name` field to differentiate them. Common gotcha: `400 Multiple tools without identifiers` error.

---

## Code: Create a Toolbox

```python
# toolbox creation via SDK goes here
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, WebSearchTool

toolbox_version = project.beta.toolboxes.create_toolbox_version(
    toolbox_name="my-toolbox",
    description="Web search and MCP server",
    tools=[
        WebSearchTool(),
        MCPTool(
            server_label="myserver",
            server_url="https://your-mcp-server.example.com",
            require_approval="never",
            project_connection_id="my-key-auth-connection",
        ),
    ],
)
```

---

## Code: Connect agents to the Toolbox

<!-- Agent A: customer support. Agent B: internal ops. Both point at the same Toolbox endpoint. -->

```python
# agent_toolbox.py — wiring agents to the toolbox goes here
```

---

## Updating a tool without touching your agents

- **Update the MCP server, redeploy the Function — neither agent needs reconfiguring**
  > This is the key operational win. Create a new Toolbox version, test it against the version-specific endpoint, promote it to default. All agents pick it up on next invocation.

---

## Auth deep dive

- **The Toolbox handles credential injection, token refresh, and policy enforcement**

  > Consuming agents don't manage credentials for individual tools. They authenticate to the Toolbox endpoint with Entra credentials, and the Toolbox handles everything downstream.

- **Auth options: No auth, Key-based, OAuth 2.0, Microsoft Entra**

  > From docs tip: _"When in doubt, start with Microsoft Entra authentication if the MCP server supports it. It eliminates the need to manage secrets and provides built-in token rotation."_

- **OAuth first-time consent flow**
  > OAuth tools generate a `CONSENT_REQUIRED` error (`-32007`) on first use, with a consent URL. The user completes OAuth in a browser, then retries. Design your app to handle this gracefully.

---

## Troubleshooting (worth including in the post)

From the official docs:

| Problem                                  | Cause                          | Fix                                            |
| ---------------------------------------- | ------------------------------ | ---------------------------------------------- |
| `tools/list` returns 0 tools             | Invalid connection credentials | Verify `project_connection_id` and credentials |
| `400 Multiple tools without identifiers` | Two unnamed tools of same type | Add `name` field to each                       |
| `CONSENT_REQUIRED (-32007)`              | OAuth first-time consent       | Open consent URL in browser                    |
| `401` on calls                           | Wrong token scope              | Use scope `https://ai.azure.com/.default`      |
| Tools missing after creation             | Provisioning delay             | Wait 10 seconds and retry                      |

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** Toolboxes are infrastructure for your tools — separation of concerns at the agent layer.

**Next:** [Part 7 — Skills and the azure-ai-projects SDK](./part7-skills.md)
