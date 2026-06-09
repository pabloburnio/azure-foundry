# Part 2 — Built-in Tools: Search, Code Interpreter, and File Search

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Beginner–Intermediate
> **Docs:** [Agent tools overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog)

---

## Introduction

<!-- Write intro here. Angle: before writing a single custom tool, get as far as possible with what Foundry gives you for free. -->

---

## Why start with built-in tools?

- **Understand the pattern before going custom**

  > Built-in tools teach you how tool dispatch works without you having to handle the execution side. Once you understand the loop here, function calling (Part 3) is just adding your own handler.

- **Built-in tools are production-ready and handle auth/sandboxing for you**
  > Quote from docs: _"Foundry Agent Service provides built-in tools as preconfigured capabilities. You enable these tools on your agent, and the service handles execution. These tools don't require external hosting or custom code."_ Code Interpreter runs in a managed sandbox, File Search manages vector indexing, Web Search handles Bing auth.

---

## Web Search

<!-- Write section here -->

- **Enable the tool on your agent**

  > Add `WebSearchTool()` to the agent's `tools` list. No Bing key needed for the basic web search tool. For advanced scenarios (market-specific filtering, custom Bing instance) there's a separate Bing Grounding tool with more config.

- **Code: ask the agent a question that requires current information**

  > Good demo query: "What were the major announcements at Microsoft Build 2026?" — forces the agent to search rather than rely on training data.

- **How citations work in the response**
  > Web Search returns inline citations automatically. The model includes source links in the response content as annotations — worth showing readers how to extract and display them.

```python
# web search agent code goes here
```

---

## Code Interpreter

<!-- Write section here -->

- **What the sandbox can and can't do**

  > **Can:** Write and run Python, perform data analysis, generate charts, do maths. **Cannot:** Make outbound network calls, access the filesystem outside the sandbox, persist state between runs. Each run gets a fresh container. Common packages (pandas, matplotlib, numpy) are pre-installed.

- **Code: ask the agent to analyse data and produce a chart**

  > Upload a CSV file to the code interpreter container, then ask "plot a bar chart of sales by region." The agent writes the Python, runs it, and the image is returned as a file in the run output.

- **Retrieving generated files from the run**
  > Files produced by Code Interpreter are accessible via `project.agents.get_file_content(file_id)` after the run completes.

```python
# code interpreter agent code goes here
```

---

## File Search

<!-- Write section here -->

- **Upload a document to a vector store**

  > File Search uses vector search against uploaded documents. Step 1: upload files to a vector store (`project.agents.create_vector_store_and_poll`). Step 2: attach the vector store ID to a `FileSearchTool`. Supported types: PDF, DOCX, TXT, MD, HTML and more. Size limit: 512 MB per file, 10,000 files per vector store.

- **How chunking and retrieval works under the hood**

  > Foundry automatically chunks documents, generates embeddings, and stores them. At query time it runs semantic search against the chunks and injects the top results into context. You don't configure this — it's managed. This lets you ground responses in private data without fine-tuning.

- **Code: ask questions against the document**
  > Good demo: upload a product manual PDF, ask "What's the warranty period for the Pro model?" The agent retrieves the relevant chunk and answers with a citation.

```python
# file search agent code goes here
```

---

## Combining tools on one agent

<!-- Write section here -->

- **An agent can have multiple tools — when does that make sense?**

  > Pass multiple tool objects in the `tools` list at agent creation. The model decides which tool to call based on the query and the tool descriptions. Tip: _"In your agent instructions, describe what each tool is for and when to use it."_ Without explicit instructions the model may call the wrong tool.

- **Token and cost implications**
  > Each tool adds to the system prompt (tool schemas are injected into context). Many tools = larger context = higher cost per call. Don't add tools "just in case."

---

## Gotchas and limits

- **Region availability varies — check before assuming a tool works**

  > Check the [tool support by region table](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-best-practice#tool-support-by-region-and-model). Code Interpreter is **not** available in `southcentralus` or `spaincentral`.

- **Code Interpreter: no outbound network, no persistent state between runs**

  > State is lost between runs. If you need to reuse a file across multiple runs, re-upload it each time or use the same container ID.

- **Tool availability requires both model AND region support**
  > From docs: _"Tool availability requires support from both the model and the region. If either shows No, the tool can't run."_ This is a common gotcha that will save readers a debugging session.

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** You can build genuinely useful agents without writing a single custom tool.

**Next:** [Part 3 — Custom Tools with Function Calling](./part3-function-calling.md)
