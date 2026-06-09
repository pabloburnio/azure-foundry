# Part 5 — Building a Custom MCP Server with Azure Functions

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate
> **Docs:** [Build and register an MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server) | [Connect to MCP servers](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)

---

## Introduction

<!-- Write intro here. Angle: MCP is the emerging standard for agent tool connectivity. Build one properly — hosted, versioned, reusable by any agent or client. -->

---

## What is MCP and why does it matter?

- **The problem: every agent framework had its own tool protocol**

  > Before MCP, LangChain tools only worked with LangChain, Semantic Kernel tools only with Semantic Kernel. You'd build the same integration multiple times for different frameworks. MCP is an open protocol ([modelcontextprotocol.io](https://modelcontextprotocol.io)) that standardises the interface.

- **MCP standardises the interface — build once, use from Claude, Foundry, Copilot Studio, VS Code, etc.**

  > From docs: _"The MCP tool allows you to connect your agent to tools hosted on an MCP server endpoint... best for tools shared across multiple agents or maintained by a different team."_ The same MCP server can be called by Foundry Agent Service, VS Code AI Toolkit, Claude Code, and any other MCP-compatible client.

- **Remote vs. local MCP servers**
  > **Remote**: hosted on a URL, callable over HTTPS — what you build here. **Local**: runs on the developer's machine, used for development/testing. Foundry Agent Service connects to remote servers only.

---

## MCP concepts

- **Tools (callable functions)**

  > The main thing you'll implement. Each tool has a name, description, input schema, and handler function — same concept as function calling, but exposed over the MCP protocol.

- **Resources (readable data)**

  > Data sources the client can read from (files, database rows, API responses). Less commonly used than tools for agent scenarios.

- **Prompts (reusable prompt templates)**

  > Pre-defined prompts the client can request. Useful for standardising how agents initiate certain interactions.

- **Transport: Streamable HTTP**
  > MCP uses Streamable HTTP for remote servers. The Azure Functions MCP extension exposes this at `/runtime/webhooks/mcp`. SSE (Server-Sent Events) was the previous transport — it's being deprecated.

---

## Set up an Azure Functions project

- **Use the official sample template**
  > Don't start from scratch. Microsoft provides `remote-mcp-functions-python` via `azd init --template remote-mcp-functions-python`. This gives you the Functions project structure, MCP extension config, and deployment scripts pre-wired.

```bash
azd init --template remote-mcp-functions-python -e mcpserver-python
```

- **The MCP webhook endpoint**
  > The Azure Functions MCP extension exposes your tools at `https://{function_app_name}.azurewebsites.net/runtime/webhooks/mcp`. This is your MCP server URL — note it's different from the function's HTTP trigger URL.

---

## Code: Define and expose tools via MCP

<!-- Example: a product catalogue tool (search_products, get_product_details) -->

```python
# mcp_server/function_app.py — tool definitions go here
```

---

## Deploy to Azure

```bash
func start        # test locally first
azd up            # deploy to Azure
```

- **Note the public endpoint URL after deployment**
  > `https://{function_app_name}.azurewebsites.net/runtime/webhooks/mcp`

---

## Secure your MCP server

- **Authentication options**

  > Four options mapped to Foundry: **Function keys** (`x-functions-key` header) → key-based auth. **Microsoft Entra** → agent identity or project managed identity. **OAuth OBO** → identity passthrough. **Unauthenticated** → not recommended for production.

- **Security baseline before sharing**
  > From docs: require authentication (avoid anonymous), treat credentials as secrets (use Azure Key Vault, not hardcoded values), implement least privilege for downstream calls, log and monitor tool calls. MCP servers are a new attack surface — worth emphasising.

---

## Register in Azure API Center (optional but recommended)

- **Acts as your private tool catalogue**

  > Azure API Center becomes your organisation's internal MCP server registry. Once registered, the server appears in Foundry's tool catalog under your org's filter. Other teams can discover and use it without you sharing URLs manually.

- **Governance and discoverability**

  > API Center lets you configure authentication schemes, manage access (which users/groups can use this server), and publish to Foundry's catalog. The catalog name in Foundry is the API Center resource name — choose it carefully.

- **Note: API Center registration is separate from connecting to Foundry**
  > If you skip API Center, you can still add the MCP server directly as a custom tool in Foundry (no catalog entry, just the URL + auth). API Center is the enterprise governance layer on top.

---

## Connect to Foundry Agent Service

- **Public vs. private endpoint options**

  > **Public endpoint**: works with both Basic and Standard agent setups. Your Functions app must be publicly reachable. **Private endpoint**: requires Standard Agent Setup with BYO VNet and MCP subnet injection. The Function App lives inside your VNet — no public egress.

- **`require_approval` setting**
  > Each MCP tool can have `require_approval: "always"` or `"never"`. Use `"always"` for tools with side effects (write operations, sending emails). Default to `"never"` for read-only tools.

```python
# agent_mcp_tool.py — connecting the agent to the MCP server goes here
```

---

## Code: Test the agent

<!-- Ask a product question, watch it route through MCP -->

```python
# test run goes here
```

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** MCP turns your tools into reusable, framework-agnostic services.

**Next:** [Part 6 — Foundry Toolboxes: Manage Tools Once, Use Everywhere](./part6-toolboxes.md)
