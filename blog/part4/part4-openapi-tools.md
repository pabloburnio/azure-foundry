# Part 4 — OpenAPI Tools: Connect Your Agent to Any REST API

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate
> **Docs:** [OpenAPI tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi)

---

## Introduction

<!-- Write intro here. Angle: you probably already have REST APIs. This is how you expose them to an agent without writing glue code per endpoint. -->

---

## OpenAPI tools vs. function calling

- **Function calling: you write the schema by hand and execute the code**

- **OpenAPI tools: point at a spec, Foundry handles the HTTP calls**

  > Key difference: with OpenAPI tools, Foundry makes the HTTP call for you. You don't write any execution code. The agent reads the spec, picks the right operation, and Foundry executes the HTTP request and returns the response. No `requires_action` polling loop needed.

- **When to choose each**
  > Use **function calling** when: you need custom logic, database access, internal systems without HTTP APIs, or complex data transformation. Use **OpenAPI tools** when: you have an existing REST API with an OpenAPI spec and just need the agent to call it. OpenAPI tools are faster to wire up but less flexible.

---

## What Foundry needs from your OpenAPI spec

- **Valid OpenAPI 3.0 or 3.1 JSON or YAML**

  > Must be 3.0 or 3.1 — not Swagger 2.0. The spec is passed as a dict to the `OpenApiFunctionDefinition`.

- **Good `operationId` and `description` fields**

  > The model reads `operationId` and `description` to understand what each endpoint does and when to call it. Auto-generated IDs like `getV2UsersId` confuse the model. Use readable IDs like `get_user_by_id` with clear descriptions.

- **Auth configuration**
  > Three auth options: `OpenApiAnonymousAuthDetails` (no auth), `OpenApiKeyAuthDetails` (API key stored in a project connection), managed identity. Store credentials in a project connection — never hardcode keys in the spec or agent definition.

---

## Code: Load an OpenAPI spec and create an OpenAPI tool

<!-- Use Open-Meteo weather API — no auth required, good for demos -->

```python
# openapi tool creation goes here
```

---

## Code: Run the agent

<!-- Ask a question that requires an API call. Show which operation the agent chose and why. -->

```python
# agent run with openapi tool goes here
```

---

## Adding authentication

- **API key via header**

- **Connection references for secrets**

  > Create a connection in your Foundry project (Settings → Connections) that stores the API key. Reference it by `project_connection_id` in `OpenApiKeyAuthDetails`. This keeps secrets out of code and makes rotation easy.

- **Your OpenAPI spec must include `securitySchemes` and `security` sections for key auth**
  > Foundry needs to know where to inject the credential. The spec's security section maps to the project connection.

```python
# authenticated openapi tool goes here
```

---

## Pointing at your own API

- **Generate an OpenAPI spec from FastAPI / ASP.NET Core**

  > FastAPI generates a spec automatically at `/openapi.json`. ASP.NET Core with Swashbuckle does the same. Download the spec and pass it to `OpenApiFunctionDefinition`.

- **Expose it to Foundry (public URL or private networking)**

---

## Limits and gotchas

- **Operations with large response payloads**

  > Large API responses consume context tokens. If an API returns a 50KB JSON blob, most of it will be wasted context. Filter responses server-side, or wrap the API in a function calling tool that post-processes the response.

- **APIs that require session state**

  > OpenAPI tools are stateless — each call is independent. APIs that require cookies or session tokens won't work. Use function calling for those.

- **Spec size limits**
  > Very large specs (hundreds of operations) should be split. Only include the operations the agent actually needs — don't dump your entire API surface into one tool.

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** If it has an OpenAPI spec, your agent can call it.

**Next:** [Part 5 — Building a Custom MCP Server with Azure Functions](./part5-mcp-server.md)
