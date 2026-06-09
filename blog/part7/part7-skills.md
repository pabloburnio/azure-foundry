# Part 7 — Skills and the azure-ai-projects SDK (Preview)

> **Series:** Building Production AI Agents on Azure AI Foundry
> **Level:** Intermediate
> **Docs:** [azure-ai-projects SDK](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects) | SDK version `>= 2.2.0` required

---

## Introduction

<!-- Write intro here. Angle: the newest SDK features — register named, reusable capabilities and compose agents from them. -->

---

## What are Skills in Foundry?

- **A Skill is a named, versioned capability — a tool with metadata**

  > Skills are the registry layer on top of tools. Where a tool is an implementation (a function, an MCP endpoint, an OpenAPI operation), a Skill is a named, versioned, discoverable wrapper around that implementation. Think of it as a tool with an identity.

- **Registered once, discoverable and reusable across projects**

  > Skills are registered at the project level. Any agent in the project can reference a skill by name without re-defining the schema. Another team can register a Skill and you can use it without knowing the implementation details.

- **Different from ad-hoc function calling**
  > Function calling (Part 3) requires you to define the schema inline every time you create an agent. Skills separate definition from use — define once, reference many times.

---

## SDK version requirements

- **`azure-ai-projects >= 2.2.0` and preview APIs**
  > This is an important caveat to be upfront about. Preview APIs can have breaking changes between SDK versions. Pin to a specific version in `requirements.txt` and check the SDK changelog before upgrading. The `project.beta` namespace is the entry point for preview features.

```bash
pip install "azure-ai-projects>=2.2.0"
```

---

## Code: Define a Skill

<!-- Name, description, version, input/output schema, underlying implementation -->

```python
# skill definition goes here
```

---

## Code: Register the Skill

```python
# skill registration goes here
```

---

## Code: Attach a Skill to an agent

- **Reference by name rather than re-defining the schema**
  > This is the payoff. Instead of copy-pasting the function schema into every agent definition, you reference the skill by name. The schema lives in the registry.

```python
# attaching a skill to an agent goes here
```

---

## Code: Skill discovery

<!-- List available skills in the project. Use a skill another team registered. -->

```python
# listing and discovering skills goes here
```

---

## Toolboxes vs. Skills — when to use which

- **Toolboxes: bundle multiple tools, manage auth, expose via MCP endpoint**
- **Skills: named, versioned, discoverable single capabilities**
- **They compose — a Toolbox can contain Skills**
  > In practice: start with tools (Parts 3–5), graduate to Toolboxes (Part 6) when you have multiple tools to manage, and use Skills when you need organisational discoverability and versioning at the capability level. Skills are most valuable in larger teams where different squads own different capabilities.

---

## What's still preview and what to watch for

- **Breaking changes risk**

  > Skills are in the `project.beta` namespace. Microsoft can change the API shape before GA. Don't build production systems on this yet without a plan to adapt.

- **GA timeline expectations**
  > No official GA date at time of writing. Monitor the [azure-ai-projects release notes](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/CHANGELOG.md) for updates.

---

## Summary

<!-- 2–3 sentence wrap-up -->

**Key takeaway:** Skills are the registry layer — they make agent tooling discoverable and governable at org scale.

**Next:** [Part 8 — Multi-Agent: Agents Calling Agents](./part8-multi-agent.md)
