# Blog Series Outline: Building Production AI Agents on Azure AI Foundry

A hands-on series for developers. Each post introduces a concept, then builds working code.
Written in order — each part builds on the last.

> **Author notes** appear as blockquotes throughout. These explain the *why* behind each point,
> link to source docs, and flag things to watch out for when writing.

---

## Part 1 — Your First Agent with Azure AI Foundry Agent Service

**Angle:** Cut through the marketing. What is Foundry Agent Service actually doing under the hood, and how is it different from just calling an LLM?

**What the reader will build:** A minimal agent that can answer questions using a system prompt. Run it from the terminal via the `azure-ai-projects` SDK.

**Docs:** [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)

---

### Outline

**1. What problem does Agent Service solve?**

- LLM calls are stateless — you manage conversation history yourself
  > Raw LLM calls via the Chat Completions API require you to manually track and resend every message in the conversation on each request. As conversations grow, this becomes expensive and error-prone.

- Agent Service manages threads, state, tool dispatch, and runs for you
  > Foundry's Agent Runtime is the managed loop. It hosts the agent, manages conversation state in threads, handles tool call dispatch, and retries. You don't write the orchestration loop — the platform runs it. Quote from docs: *"There's no application code to maintain, no compute to pay for, and no containers or packages to optimize, scale, or patch."*

- When to use it vs. raw LLM calls
  > Use Agent Service when you need: persistent conversation state, tool calling, or a managed endpoint you can publish. Use raw Chat Completions when you're doing one-shot inference with no tools and want maximum control. The new **Responses API** is the single entry point behind both — you can call it directly from your own code and get Foundry models + tools without even creating an agent resource.

---

**2. Core concepts (keep it brief)**

- Agent — the configured AI with a system prompt and tools
  > An agent is defined by three things: a **model** from the Foundry catalog, **instructions** (system prompt), and **tools**. There are two agent types: *Prompt agents* (defined by config, fully managed runtime — no code to maintain) and *Hosted agents* (your code packaged as a container, Foundry runs it). For this series we use Prompt agents. [Agent types comparison table](https://learn.microsoft.com/en-us/azure/foundry/agents/overview#agent-types)

- Thread — a conversation session
  > A thread stores the conversation history. Multiple runs can happen on the same thread, building up context. Threads persist server-side — you don't send the history back on each call.

- Run — a single execution triggered on a thread
  > A run is what happens when you send a message and ask the agent to respond. The agent reasons, potentially calls tools, then produces a reply. Runs have a lifecycle: `queued → in_progress → requires_action (tool call) → completed`.

- Messages — the content in a thread
  > Messages are the turns of conversation stored in a thread. Each has a role (`user` or `assistant`) and content. Tool call results are also stored as messages.

---

**3. Prerequisites**

- Azure subscription with Foundry access
  > Readers need an AI Foundry project created in the Azure portal. The project is the container for models, connections, agents, and tools. Worth linking to the [quickstart: create a project](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent).

- A deployed model (e.g. GPT-4o in your Foundry project)
  > Not every model supports every tool. For Part 1 any model works. From Part 2 onwards, recommend `gpt-4o` or `gpt-4.1` — these have the broadest tool support. See the [model/tool support matrix](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-best-practice#tool-support-by-region-and-model).

- `azure-ai-projects` SDK installed (`pip install azure-ai-projects`)
  > Require `>= 2.0.0` for GA agent features. Some Parts (7 onwards) need `>= 2.2.0` for Skills/Toolboxes preview.

---

**4. Code: Create an agent**

- Authenticate with `DefaultAzureCredential`
  > `DefaultAzureCredential` tries several auth methods in order: environment variables, managed identity, Azure CLI. For local dev, `az login` is all you need. Don't use API keys in code — they're secrets.

- Create a project client
  > The client is `AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=...)`. The endpoint format is `https://<resource_name>.ai.azure.com/api/projects/<project_name>`. Both are visible in the Foundry portal overview page.

- Define an agent with a name, model, and system prompt
  > Use `project.agents.create_version(agent_name=..., definition=PromptAgentDefinition(...))`. Agents are versioned — each call to `create_version` creates a new immutable snapshot. You reference agents by name at invocation time.

---

**5. Code: Run a conversation**

- Create a thread
  > In the new Foundry API, you don't explicitly create threads — the Responses API manages session state internally. Mention this has changed from the classic (Azure AI Studio) Assistants API which used explicit thread objects. Worth flagging for readers who've seen older tutorials.

- Add a user message and trigger a run
  > Using `openai.responses.create(input=..., extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}})`. The `agent_reference` body param is how you point the Responses API at a specific named agent.

- Poll until complete and read the reply
  > The Responses API supports streaming (`stream=True`) or blocking. For Part 1 use blocking to keep the code simple. Introduce streaming in a later part when it matters for UX.

---

**6. What just happened? (trace the execution)**

- Walk through what Foundry did behind the scenes
  > This is worth a simple diagram: user message → Responses API → Agent Runtime → model inference → response. Mention that **agent tracing** is built in — every model call, tool invocation, and decision is recorded. In the Foundry portal under your project you can see the full trace. [Agent tracing docs](https://learn.microsoft.com/en-us/azure/foundry/foundry-classic/how-to/develop/trace-application)

---

**7. Tidy up**

- Delete the agent version
  > Use `project.agents.delete_version(agent_name=..., agent_version=...)`. Good habit to show cleanup in tutorials so readers don't accumulate unused resources. Agents are billed per use, not per existence, but it's tidy practice.

---

**Code files:** `agent_hello.py`

**Key takeaway:** Agent Service is a managed loop — it handles the orchestration so you don't have to.

---

## Part 2 — Built-in Tools: Search, Code Interpreter, and File Search

**Angle:** Before writing a single custom tool, get as far as possible with what Foundry gives you for free.

**What the reader will build:** An agent that can search the web, write and run Python, and answer questions from an uploaded document.

**Docs:** [Agent tools overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog)

---

### Outline

**1. Why start with built-in tools?**

- Understand the pattern before going custom
  > Built-in tools teach you how tool dispatch works without you having to handle the execution side. Once you understand the loop here, function calling (Part 3) is just adding your own handler.

- Built-in tools are production-ready and handle auth/sandboxing for you
  > Quote from docs: *"Foundry Agent Service provides built-in tools as preconfigured capabilities. You enable these tools on your agent, and the service handles execution. These tools don't require external hosting or custom code."* That's the key value — Code Interpreter runs in a managed sandbox, File Search manages vector indexing, Web Search handles Bing auth.

---

**2. Web Search**

- Enable the tool on your agent
  > Add `WebSearchTool()` to the agent's `tools` list. That's it — no Bing key needed for the basic web search tool. For advanced scenarios (market-specific filtering, custom Bing instance) there's a separate Bing Grounding tool with more config.

- Code: ask the agent a question that requires current information
  > Good demo query: "What were the major announcements at Microsoft Build 2026?" — forces the agent to search rather than rely on training data.

- How citations work in the response
  > Web Search returns inline citations automatically. The model is instructed to include source links. These appear in the response content as annotations — worth showing readers how to extract and display them.

---

**3. Code Interpreter**

- What the sandbox can and can't do
  > **Can:** Write and run Python, perform data analysis, generate charts, do maths. **Cannot:** Make outbound network calls, access the filesystem outside the sandbox, persist state between runs. Each run gets a fresh container. Common packages like pandas, matplotlib, numpy are pre-installed.

- Code: ask the agent to analyse data and produce a chart
  > Upload a CSV file to the code interpreter container, then ask "plot a bar chart of sales by region." The agent writes the Python, runs it, and the image is returned as a file in the run output.

- Retrieving generated files from the run
  > Files produced by Code Interpreter are accessible via `project.agents.get_file_content(file_id)` after the run completes. Show how to save the chart to disk.

---

**4. File Search**

- Upload a document to a vector store
  > File Search uses vector search against uploaded documents. Step 1: upload files to a vector store (`project.agents.create_vector_store_and_poll`). Step 2: attach the vector store ID to a `FileSearchTool`. Supported types: PDF, DOCX, TXT, MD, HTML and more. Size limit: 512 MB per file, 10,000 files per vector store.

- How chunking and retrieval works under the hood
  > Foundry automatically chunks documents, generates embeddings, and stores them. At query time it runs a semantic search against the chunks and injects the top results into the model context. You don't configure this — it's managed. Worth explaining *why* this matters: it lets you ground responses in your private data without fine-tuning.

- Code: ask questions against the document
  > Good demo: upload a product manual PDF, ask "What's the warranty period for the Pro model?" The agent retrieves the relevant chunk and answers with a citation to the document.

---

**5. Combining tools on one agent**

- An agent can have multiple tools — when does that make sense?
  > Pass multiple tool objects in the `tools` list at agent creation. The model decides which tool to call based on the query and the tool descriptions. Tip from official docs: *"In your agent instructions, describe what each tool is for and when to use it."* Without explicit instructions, the model may call the wrong tool or none at all.

- Token and cost implications
  > Each tool adds to the system prompt (tool schemas are injected into context). Many tools = larger context = higher cost per call. Don't add tools "just in case" — only include what the agent will actually need.

---

**6. Gotchas and limits**

- File Search: region availability varies
  > Check the [tool support by region table](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-best-practice#tool-support-by-region-and-model) before assuming a tool is available. For example, Code Interpreter is **not** available in `southcentralus` or `spaincentral`.

- Code Interpreter: no outbound network, no persistent state between runs
  > State is lost between runs. If you need to reuse a file across multiple runs, re-upload it each time or use the same container ID.

- Tool availability requires **both** the model and the region to support it
  > From docs: *"Tool availability requires support from both the model and the region. Check both tables — if either shows No, the tool can't run."* This is a common gotcha that will save readers a debugging session.

---

**Code files:** `agent_builtin_tools.py`, sample PDF for File Search

**Key takeaway:** You can build genuinely useful agents without writing a single custom tool.

---

## Part 3 — Custom Tools with Function Calling

**Angle:** The foundation of everything custom. Understand this and the rest of the series makes sense.

**What the reader will build:** An agent that can call a real function via function calling.

**Docs:** [Function calling](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/function-calling)

---

### Outline

**1. How function calling works**

- You define the tool schema (name, description, parameters as JSON Schema)
  > The schema is what the model reads to understand what the tool does and when to use it. It's not code — it's a description. The model never sees your actual function implementation.

- The LLM decides when to call it and with what arguments
  > The model outputs a *tool call request* (structured JSON with tool name + arguments) rather than a text response. The run enters `requires_action` status and pauses, waiting for you to execute the function and return the result.

- You execute the function and return the result
  > This is the critical distinction from built-in tools: **you** are responsible for executing the function. Foundry just dispatches the request and waits. This means your function can do anything — database query, API call, file read, calculation.

- The LLM incorporates the result into its reply
  > Once you submit the tool output, the run continues. The model sees the result as context and generates its final response. The entire loop (model → tool call → your code → model) is one run.

---

**2. Why description quality matters**

- The LLM reads your description to decide whether to use the tool
  > The `description` field on your function schema is the most important thing you write. The model uses it to decide: (a) whether this tool is relevant, and (b) when to call it vs. another tool. Vague descriptions = wrong tool called = wrong answers.

- Good vs. bad tool descriptions — examples
  > **Bad:** `"Gets order info"` — too vague, model can't judge when to use it.
  > **Good:** `"Returns the current status and estimated delivery date for a given order ID. Use this when the user asks about a specific order."` — tells the model exactly when and why.
  > From official docs tip: *"In your agent instructions, describe what each tool is for and when to use it."*

---

**3. Define a tool schema**

- JSON Schema structure
  > The schema follows standard JSON Schema: `type`, `properties`, `required`. The model reads `description` at both the function level and per-parameter level. Good per-parameter descriptions help the model extract the right argument from natural language.

- Required vs. optional parameters
  > List only truly required params in `required`. Optional params should have defaults your code handles. Don't make the model guess values it shouldn't have to provide.

- Enum types for constrained inputs
  > Use `"enum": ["pending", "shipped", "delivered"]` for parameters with a fixed set of values. This prevents the model from hallucinating invalid values.

---

**4. Code: Handle tool calls in the run loop**

- Poll for `requires_action` status
  > After submitting a message, poll the run status. When status is `requires_action`, the model has produced tool call requests. The `run.required_action.submit_tool_outputs.tool_calls` list contains one or more tool calls to execute.

- Extract the tool name and arguments
  > Each tool call has `function.name` (the tool to call) and `function.arguments` (a JSON string of the arguments). Parse the arguments with `json.loads()`.

- Submit the tool output back to the run
  > Call `project.agents.submit_tool_outputs_to_run(...)` with a list of `ToolOutput` objects — one per tool call, matched by `tool_call_id`. The run then continues from where it paused.

---

**5. Error handling**

- What happens if your function throws?
  > If your function raises an exception, catch it and return an error string as the tool output. Don't let it propagate — a crashed tool call leaves the run in `requires_action` permanently. The model can handle an error message gracefully (e.g. "Order not found") and communicate it to the user.

---

**Code files:** `agent_function_calling.py`

**Key takeaway:** Function calling is a dispatch pattern — the LLM routes, you execute.

---

## Part 4 — OpenAPI Tools: Connect Your Agent to Any REST API

**Angle:** You probably already have REST APIs. This is how you expose them to an agent without writing glue code per endpoint.

**What the reader will build:** An agent that calls a public REST API defined by an OpenAPI spec.

**Docs:** [OpenAPI tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi)

---

### Outline

**1. OpenAPI tools vs. function calling**

- Function calling: you write the schema by hand and execute the code
- OpenAPI tools: point at a spec, Foundry handles the HTTP calls
  > Key difference: with OpenAPI tools, Foundry makes the HTTP call for you. You don't write any execution code. The agent reads the spec, picks the right operation, and Foundry executes the HTTP request and returns the response. No `requires_action` polling loop needed.

- When to choose each
  > Use **function calling** when: you need custom logic, database access, internal systems without HTTP APIs, or complex data transformation. Use **OpenAPI tools** when: you have an existing REST API with an OpenAPI spec and just need the agent to call it. OpenAPI tools are faster to wire up but less flexible.

---

**2. What Foundry needs from your OpenAPI spec**

- Valid OpenAPI 3.0 or 3.1 JSON or YAML
  > Must be 3.0 or 3.1 — not Swagger 2.0. The spec is passed as a dict to the `OpenApiFunctionDefinition`.

- Good `operationId` and `description` fields
  > The model reads `operationId` and `description` to understand what each endpoint does and when to call it. If your spec has auto-generated operation IDs like `getV2UsersId`, the model will struggle. Readable IDs like `get_user_by_id` and clear descriptions are essential.

- Auth configuration
  > Three auth options: `OpenApiAnonymousAuthDetails` (no auth), `OpenApiKeyAuthDetails` (API key stored in a project connection), managed identity. Store credentials in a project connection — never hardcode keys in the spec or agent definition.

---

**3. Adding authentication**

- Connection references for secrets
  > Create a connection in your Foundry project (under Settings → Connections) that stores the API key. Reference it by `project_connection_id` in `OpenApiKeyAuthDetails`. This keeps secrets out of code and makes rotation easy.

- Your OpenAPI spec must include `securitySchemes` and `security` sections for key auth
  > Foundry needs to know where to inject the credential. The spec's security section maps to the project connection.

---

**4. Limits and gotchas**

- Operations with large response payloads
  > Large API responses consume context tokens. If an API returns a 50KB JSON blob, most of it will be wasted context. Either filter responses server-side or post-process them in a function calling wrapper instead.

- APIs that require session state
  > OpenAPI tools are stateless — each call is independent. APIs that require cookies or session tokens won't work. Use function calling for those.

---

**Code files:** `agent_openapi_tool.py`, `weather_openapi.json`

**Key takeaway:** If it has an OpenAPI spec, your agent can call it.

---

## Part 5 — Building a Custom MCP Server with Azure Functions

**Angle:** MCP is the emerging standard for agent tool connectivity. Build one properly — hosted, versioned, reusable by any agent or client.

**What the reader will build:** A remote MCP server on Azure Functions, registered in Azure API Center, connected to a Foundry agent.

**Docs:** [Build and register an MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server) | [Connect to MCP servers](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)

---

### Outline

**1. What is MCP and why does it matter?**

- The problem: every agent framework had its own tool protocol
  > Before MCP, LangChain tools only worked with LangChain, Semantic Kernel tools only with Semantic Kernel, etc. You'd build the same integration multiple times for different frameworks. MCP is an open protocol (modelcontextprotocol.io) that standardises the interface.

- MCP standardises the interface — build once, use from Claude, Foundry, Copilot Studio, VS Code, etc.
  > From docs: *"The MCP tool allows you to connect your agent to tools hosted on an MCP server endpoint... best for tools shared across multiple agents or maintained by a different team."* The same MCP server can be called by Foundry Agent Service, VS Code AI Toolkit, Claude Code, and any other MCP-compatible client.

- Remote vs. local MCP servers
  > **Remote**: hosted on a URL, callable over HTTPS. This is what you build here. **Local**: runs on the developer's machine, used for development/testing. Foundry Agent Service connects to remote servers only.

---

**2. MCP concepts**

- Tools (callable functions)
  > The main thing you'll implement. Each tool has a name, description, input schema, and handler function. Same concept as function calling, but exposed over the MCP protocol.

- Resources (readable data)
  > Data sources the client can read from (files, database rows, API responses). Less commonly used than tools for agent scenarios.

- Prompts (reusable prompt templates)
  > Pre-defined prompts the client can request. Useful for standardising how agents initiate certain interactions.

- Transport: Streamable HTTP (the current standard)
  > MCP uses Streamable HTTP transport for remote servers. The Azure Functions MCP extension exposes this at `/runtime/webhooks/mcp`. SSE (Server-Sent Events) was the previous transport — it's being deprecated.

---

**3. Set up an Azure Functions project**

- Use the official sample template
  > Don't start from scratch. Microsoft provides `remote-mcp-functions-python` via `azd init --template remote-mcp-functions-python`. This gives you the Functions project structure, MCP extension config, and deployment scripts pre-wired.

- The MCP webhook endpoint
  > The Azure Functions MCP extension exposes your tools at `https://{function_app_name}.azurewebsites.net/runtime/webhooks/mcp`. This is your MCP server URL. Note this is different from the function's HTTP trigger URL.

---

**4. Deploy and secure**

- Authentication options
  > Four options, mapped to Foundry: **Function keys** (`x-functions-key` header) → key-based auth in Foundry. **Microsoft Entra** → agent identity or project managed identity in Foundry. **OAuth OBO** → identity passthrough. **Unauthenticated** → not recommended for production.

- Security baseline before sharing
  > From docs: require authentication (avoid anonymous), treat credentials as secrets (use Azure Key Vault, not hardcoded values), implement least privilege for downstream calls, log and monitor tool calls. Worth emphasising — MCP servers are a new attack surface.

---

**5. Register in Azure API Center (optional but recommended)**

- Acts as your private tool catalogue
  > Azure API Center becomes your organisation's internal MCP server registry. Once registered, the server appears in Foundry's tool catalog under your organisation's filter. Other teams can discover and use it without you sharing URLs manually.

- Governance and discoverability
  > API Center lets you configure authentication schemes, manage access (which users/groups can use this server), and publish to Foundry's catalog. The catalog name in Foundry is the API Center resource name — choose it carefully.

- Note: API Center registration is separate from connecting to Foundry
  > If you skip API Center, you can still add the MCP server directly as a custom tool in Foundry (no catalog entry, just the URL + auth). API Center is the enterprise governance layer on top.

---

**6. Connect to Foundry Agent Service**

- Public vs. private endpoint options
  > **Public endpoint**: works with both Basic and Standard agent setups. Your Functions app must be publicly reachable. **Private endpoint**: requires Standard Agent Setup with BYO VNet and MCP subnet injection. The Function App lives inside your VNet — no public egress.

- `require_approval` setting
  > Each MCP tool can have `require_approval: "always"` or `"never"`. `"always"` means the agent asks the user to confirm before each tool invocation. Use this for tools with side effects (write operations, sending emails). Default to `"never"` for read-only tools.

---

**Code files:** `mcp_server/function_app.py`, `agent_mcp_tool.py`

**Key takeaway:** MCP turns your tools into reusable, framework-agnostic services.

---

## Part 6 — Foundry Toolboxes: Manage Tools Once, Use Everywhere

**Angle:** You now have multiple tools. Toolboxes let you bundle them, handle auth centrally, and point any agent at the same endpoint.

**What the reader will build:** A Toolbox combining File Search, an MCP server, and an OpenAPI tool — then wired to two different agents.

**Docs:** [Create and use a Foundry Toolbox](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)

---

### Outline

**1. The problem Toolboxes solve**

- Adding the same tool to 10 agents means 10 places to update credentials
  > Without Toolboxes, every agent definition independently configures its tools and auth. Rotate an API key and you update 10 agents. Add a new tool and you update 10 agents. Toolboxes centralise this.

- From the docs, the specific problems named are:
  > *"Tool Duplication: Teams re-implement the same tools independently. Credential Sprawl: Credentials get duplicated across multiple agents. Governance Gaps: Little visibility into what tools exist or who's using them. Integration Bottleneck: Developers stall waiting for tool integration."*

---

**2. How Toolboxes work**

- A Toolbox exposes a single MCP-compatible endpoint
  > The Toolbox itself is an MCP server. Any MCP-capable agent runtime can consume it — Foundry Agent Service, LangGraph, Microsoft Agent Framework, GitHub Copilot SDK, custom code. This is why Toolboxes are powerful: they're not Foundry-specific.

- Versioning: immutable snapshots with explicit promotion
  > Each Toolbox version is an immutable snapshot. Creating a new version doesn't automatically promote it. You test against the version-specific endpoint, then promote to `default_version` when ready. Agents using the consumer endpoint automatically pick up the new default — no agent code changes. This is proper infrastructure-style versioning for tools.

- Two endpoint patterns
  > **Developer endpoint** (version-specific): `{project_endpoint}/toolboxes/{name}/versions/{version}/mcp?api-version=v1` — use for testing.
  > **Consumer endpoint** (always serves default): `{project_endpoint}/toolboxes/{name}/mcp?api-version=v1` — use in agent definitions.

- Required header
  > Every request must include `Foundry-Features: Toolboxes=V1Preview`. Easy to miss, causes silent failures.

---

**3. What can go in a Toolbox?**

Full list from docs: Web Search, Azure AI Search, Code Interpreter, File Search, OpenAPI tools, MCP servers, Agent-to-Agent (A2A), Fabric IQ, Work IQ, Browser Automation.

- One unnamed tool per type limit
  > You can only have one unnamed instance of each tool type per Toolbox. To add multiple Azure AI Search indexes, give each a `name` field to differentiate them. Common gotcha: `400 Multiple tools without identifiers` error.

---

**4. Auth in Toolboxes**

- The Toolbox handles credential injection, token refresh, and policy enforcement
  > Consuming agents don't manage credentials for individual tools. They authenticate to the Toolbox endpoint with Entra credentials, and the Toolbox handles everything downstream. This is the key governance win.

- Auth options: No auth, Key-based (project connection), OAuth 2.0 (managed or custom), Microsoft Entra (agent identity or OBO)
  > From docs tip: *"When in doubt, start with Microsoft Entra authentication if the MCP server supports it. It eliminates the need to manage secrets and provides built-in token rotation."*

- OAuth first-time consent flow
  > OAuth tools in a Toolbox generate a `CONSENT_REQUIRED` error (`-32007`) on first use, with a consent URL. The user completes the OAuth flow in a browser, then retries. Design your app to handle this gracefully.

---

**5. Troubleshooting section (worth including)**

From docs:
> - `tools/list` returns 0 tools → check `project_connection_id` and credentials
> - `400 Multiple tools without identifiers` → add `name` field to differentiate same-type tools
> - `CONSENT_REQUIRED (-32007)` → user needs to complete OAuth in browser
> - `401` → use scope `https://ai.azure.com/.default`
> - Tools missing after creation → wait 10 seconds and retry (provisioning delay)

---

**Code files:** `agent_toolbox.py`

**Key takeaway:** Toolboxes are infrastructure for your tools — separation of concerns at the agent layer.

---

## Part 7 — Skills and the `azure-ai-projects` SDK (Preview)

**Angle:** The newest SDK features — register named, reusable capabilities and compose agents from them.

**What the reader will build:** A named skill registered via the SDK, attached to an agent, and callable by name.

**Docs:** Skills are documented in the `azure-ai-projects` SDK changelog and preview release notes. As of `2.2.0` this is still early preview — check the [GitHub repo](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects) for latest samples.

---

### Outline

**1. What are Skills in Foundry?**

- A Skill is a named, versioned capability — a tool with metadata
  > Skills are the registry layer on top of tools. Where a tool is an implementation (a function, an MCP endpoint, an OpenAPI operation), a Skill is a named, versioned, discoverable wrapper around that implementation. Think of it as a tool with an identity.

- Registered once, discoverable and reusable across projects
  > Skills are registered at the project level. Any agent in the project can reference a skill by name, without re-defining the schema. Another team can register a Skill and you can use it without knowing the implementation details.

- Different from ad-hoc function calling
  > Function calling (Part 3) requires you to define the schema inline every time you create an agent. Skills separate definition from use — define once, reference many times.

---

**2. SDK version requirements**

- `azure-ai-projects >= 2.2.0` and preview APIs
  > This is an important caveat to be upfront about. Preview APIs can have breaking changes between SDK versions. Recommend pinning to a specific version in `requirements.txt` and checking the SDK changelog before upgrading. The `project.beta` namespace is the entry point for preview features.

---

**3. Toolboxes vs. Skills — when to use which**

- Toolboxes: bundle multiple tools, manage auth, expose via MCP endpoint
- Skills: named, versioned, discoverable single capabilities
- They compose — a Toolbox can contain Skills
  > In practice: start with tools (Parts 3–5), graduate to Toolboxes (Part 6) when you have multiple tools to manage, and use Skills when you need organisational discoverability and versioning at the capability level. Skills are most valuable in larger teams where different squads own different capabilities.

---

**Code files:** `agent_skills.py`

**Key takeaway:** Skills are the registry layer — they make agent tooling discoverable and governable at org scale.

---

## Part 8 — Multi-Agent: Agents Calling Agents

**Angle:** Not every problem fits in one agent. Learn when splitting makes sense and how to wire agents together properly.

**What the reader will build:** An orchestrator agent that delegates to two specialist sub-agents via the A2A protocol.

**Docs:** [Agent-to-Agent (A2A) tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent)

---

### Outline

**1. When does multi-agent actually make sense?**

- Specialisation, scale, governance
  > Good reasons: different agents need different models (e.g. a fast cheap model for triage, a powerful one for analysis), different tool sets, or different auth boundaries (data the orchestrator shouldn't have direct access to).

- Red flags: complexity for its own sake
  > Multi-agent adds latency (each agent-to-agent call is a network hop), cost (multiple model inference calls), and debugging complexity. Don't split unless you have a concrete reason.

---

**2. A2A vs. multi-agent workflows**

- This is an important distinction the docs make explicitly:
  > **Using the A2A tool**: Agent A calls Agent B, gets the answer back, then Agent A summarises and responds to the user. Agent A stays in control. **Using a workflow**: Agent B takes full responsibility — Agent A hands off entirely and is out of the loop. For this part we cover the A2A tool pattern (orchestrator stays in control).

- **Important migration note for readers who've seen older Foundry docs:**
  > *"The Connected Agents tool from the previous (classic) Agents API isn't available in the new Foundry Agent Service."* The old `agent.as_tool()` pattern is gone. The replacement is the A2A tool (this part) or Workflows. Worth calling this out explicitly as many tutorials still show the old pattern.

---

**3. How A2A works in Foundry**

- Expose an agent as an A2A endpoint
  > A Foundry agent can be exposed as an A2A-compatible endpoint via **Enable incoming A2A** on the agent. The agent gets a stable URL that other agents can call. Foundry generates an agent card at `/.well-known/agent-card.json` that describes capabilities.

- Create an A2A connection
  > Before adding the A2A tool, create a project connection pointing to the sub-agent's A2A endpoint. This stores the auth details. Auth options: key-based, managed identity, OAuth OBO, project managed identity.

- Add the A2A tool to the orchestrator
  > `A2APreviewTool(project_connection_id=a2a_connection.id)` added to the orchestrator's tools list. The orchestrator calls the sub-agent like any other tool, passing natural language input. The sub-agent processes it and returns a response.

---

**4. Calling non-Foundry agents**

- The A2A protocol is open — any A2A-compatible endpoint works
  > You're not limited to Foundry agents. Any agent implementing the A2A spec (`a2a-protocol.org`) can be called. You can also register external A2A agents in Foundry Control Plane for centralised governance and observability.

---

**5. Durable orchestration for long-running tasks**

- Azure Durable Functions + SignalR for agents that survive restarts
  > Agents that pause for hours or days (e.g. waiting for human approval) need durable state. Azure Durable Functions provides checkpointed execution — if the process restarts, the workflow resumes from the last checkpoint. SignalR handles real-time notification when the agent resumes.

- Human-in-the-loop approval gates
  > Pattern: agent produces a proposed action → pauses → sends notification → human reviews and approves/rejects → agent continues. This is the `require_approval` pattern at the workflow level rather than per-tool call.

---

**6. Observability across agents**

- Tracing a request across multiple agent runs
  > Each agent run generates its own trace. Cross-agent tracing requires propagating trace context (W3C TraceContext headers) between the orchestrator and sub-agents. Foundry's built-in tracing handles this when using the A2A tool — you get end-to-end traces in Application Insights automatically.

---

**Code files:** `multi_agent_orchestrator.py`

**Key takeaway:** Multi-agent is a design choice, not a default — use it when isolation or specialisation genuinely earns its complexity.

---

## Part 9 — Evaluating and Monitoring Your Agent in Production

**Angle:** Shipping is the beginning. Close the loop with evaluation and monitoring so you know when your agent degrades.

**What the reader will build:** An evaluation pipeline and a monitoring dashboard wired to the agent from the series.

**Docs:** [Agent development lifecycle](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle) | [Monitor agents dashboard](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)

---

### Outline

**1. Why evaluation is different for agents**

- Non-deterministic outputs
  > You can't use `assert response == "expected string"`. The same question asked twice may get different phrasings of a correct answer. Evaluation requires scoring criteria, not exact matching.

- Multi-turn conversations
  > Quality at turn N depends on the full conversation history. An agent can give a correct answer to turn 1 but a wrong answer to turn 5 because it lost track of context. Your eval dataset needs multi-turn examples, not just single Q&A pairs.

- Tool calls add a new failure surface
  > An agent can fail in three distinct ways: (a) wrong final answer, (b) correct answer but wrong tool called, (c) correct tool called but with wrong arguments. A good eval suite covers all three.

---

**2. Evaluation strategies**

- LLM-as-judge
  > Use a second model (typically a larger, slower one) to score the agent's responses against criteria. Criteria examples: "Is the response factually correct?", "Did the agent stay on topic?", "Was the tone appropriate?". Score 1–5 or pass/fail. Foundry has built-in LLM-as-judge evaluators.

- Groundedness
  > Specifically relevant for RAG agents (File Search, Azure AI Search). Did the response stay faithful to the retrieved documents, or did the agent hallucinate? Foundry has a built-in groundedness evaluator.

- Task completion
  > Did the agent actually do the thing the user asked? This is harder to automate and often requires human review or a custom evaluator.

---

**3. Foundry's built-in evaluators**

- From the Foundry development lifecycle docs, the platform supports:
  > **Trace-based evaluation** — evaluate specific runs from traces. **Dataset-based evaluation** — run a golden dataset through the agent and score in bulk. **Continuous evaluation** — sample live production traffic and evaluate automatically. These are all accessible from the Foundry portal under your project's Evaluation section.

---

**4. Monitoring with Application Insights**

- What Foundry emits via OpenTelemetry
  > Foundry Agent Service automatically emits traces to Application Insights when connected. Every model call, tool invocation, and run lifecycle event is a span. You get error rate, latency, token usage, and tool call success rate out of the box.

- Custom agent monitoring (agents not hosted on Foundry)
  > For agents running outside Foundry (your own process, a different platform), register them in **Foundry Control Plane** and route through **AI Gateway**. Send OTel traces to the same Application Insights resource. You get unified observability across Foundry-hosted and external agents in one dashboard.

---

**5. The development lifecycle (frame the whole part around this)**

- From docs, the full lifecycle is:
  > Create → Test → **Trace** → **Evaluate** → Optimize → Publish → **Monitor**. Parts 1–8 covered Create through Publish. This part closes the loop on Trace, Evaluate, and Monitor — completing the cycle. The **Agent Optimizer** (mentioned in docs) can automatically improve instructions based on eval results — worth mentioning as a next step.

---

**Code files:** `agent_evaluation.py`, `golden_dataset.jsonl`

**Key takeaway:** An agent you can't measure is an agent you can't trust in production.

---

## Series Notes

### Recommended reading order
Start at Part 1 and work forward — each part assumes the code from the previous one.

### Code repository structure (suggested)
```
foundry-agent-series/
├── part1-hello-agent/
├── part2-builtin-tools/
├── part3-function-calling/
├── part4-openapi-tools/
├── part5-mcp-server/
├── part6-toolboxes/
├── part7-skills/
├── part8-multi-agent/
├── part9-evaluation/
└── shared/          # auth helpers, common config
```

### Prerequisites across the series
- Azure subscription with AI Foundry access provisioned
- A deployed model in your Foundry project (`gpt-4o` or `gpt-4.1` recommended for broadest tool support)
- Python 3.11+
- `azure-ai-projects >= 2.2.0`
- Azure CLI logged in (`az login`)

### Quick-start version (Parts 1–4)
Covers agent fundamentals through connecting to real APIs. Good stopping point if you just want a working custom agent without the MCP/Toolbox infrastructure.

### Key docs to bookmark
- [Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Tool catalog](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog)
- [Tool best practices + region/model support matrix](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-best-practice)
- [Build and register an MCP server](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server)
- [Toolbox docs](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [Agent-to-Agent (A2A)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent)
- [Agent development lifecycle](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle)
