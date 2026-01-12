---
name: cc-agent-sdk
description: Practical, agent-oriented entry point for using the Claude Agent SDK (Python/TypeScript) to build autonomous coding agents with Claude Code as the runtime, including permissions, sessions, MCP, structured outputs, Skills, and deployment guidance.
---

# Claude Agent SDK (Skill)

Use this Skill when you (or another coding agent) need to build, run, or integrate an autonomous agent using the Claude Agent SDK.

This Skill is designed as an **on-ramp + index**. The full official docs are mirrored into `references/` so you can work offline and grep quickly.

## Minimum setup checklist

- Claude Code installed and authenticated (`claude` runs successfully).
- SDK installed:
  - Python: `pip install claude-agent-sdk`
  - TypeScript: `npm install @anthropic-ai/claude-agent-sdk`
- Auth:
  - Prefer Claude Code auth (recommended by the docs), otherwise set `ANTHROPIC_API_KEY`.
- Settings for Claude Code: see `references/settings.md`

## Recommended defaults for coding agents

When writing SDK code, prefer these defaults unless you have a reason not to:

- **Streaming mode** for interactive agent loops (progress updates, interrupts, dynamic permissions).
- **Use Claude Code’s system prompt** so the agent gets proven tool-use and coding conventions:
  - Python: `system_prompt={"type":"preset","preset":"claude_code","append":"...optional..."}`  
  - TypeScript: `systemPrompt:{type:"preset",preset:"claude_code",append:"...optional..."}`
- **Load project filesystem settings** so the agent reads `CLAUDE.md` and discovers `.claude/*` artifacts (Skills, commands):
  - Python: `setting_sources=["project"]` (add `"user"` only if you explicitly want personal Skills/settings)
  - TypeScript: `settingSources:["project"]`
- **Least-privilege tools**: start with `["Read","Glob","Grep"]`, then add `Edit/Write/Bash/WebFetch/WebSearch/MCP/Task/Skill` as needed.
- **Permissions**:
  - Default: `permission_mode="default"` / `permissionMode:"default"`
  - For trusted local refactors: `acceptEdits`
  - For production: prefer hooks + explicit allow/deny rules; avoid blanket bypass.
- **Sessions**: capture the initial `session_id` and use `resume` when you need multi-step workflows across calls.

## Quickstart pattern (what “good” looks like)

- Use `query()` and stream messages.
- Restrict tools via `allowed_tools` / `allowedTools`.
- If you want Claude Code behavior + project instructions, combine:
  - `system_prompt/systemPrompt` preset `claude_code`
  - `setting_sources/settingSources` includes `"project"`

For a complete runnable example, read `references/quickstart.md`.

## How to navigate the local docs (start here)

- `references/overview.md` — capabilities, concepts, and “how it fits together”
- `references/quickstart.md` — end-to-end getting started (Python + TypeScript)
- `references/python.md` — full Python API surface (`ClaudeAgentOptions`, `query`, sessions, MCP, output formats)
- `references/typescript.md` — full TypeScript API surface (`Options`, `Query`, hooks, tools, etc.)

## Key topics (pick what you need)

- Permissions and safe tool use: `references/permissions.md` and `references/settings.md`
- Claude Code hooks (how to author hooks): `references/hooks.md`
- Streaming vs single-message mode: `references/streaming-vs-single-mode.md`
- Session resume/fork/continue: `references/sessions.md`
- Structured, validated JSON outputs (schemas): `references/structured-outputs.md`
- MCP integrations (stdio/HTTP/SSE, auth/env, resources): `references/mcp.md`
- Custom tools via SDK MCP servers: `references/custom-tools.md`
- Subagents/delegation: `references/subagents.md`
- Slash commands (discover/send/custom): `references/slash-commands.md`
- Skills (filesystem loading + enabling `"Skill"` tool): `references/skills.md`
- Cost + budget controls: `references/cost-tracking.md`
- TODO tracking patterns: `references/todo-tracking.md`
- Plugins: `references/plugins.md`
- Hosting + deployment patterns: `references/hosting.md`, `references/secure-deployment.md`
- System prompt + CLAUDE.md behavior: `references/modifying-system-prompts.md`
- Migrating from the old Claude Code SDK name: `references/migration-guide.md`

## Gaps to watch for (ask for these if you need them)

- Repo-level “golden” examples (beyond the quickstart) for common agent apps (PR reviewer, codebase migrator, CI fixer).
- A ready-to-copy **permission policy** template (hooks + settings rules) for safe production deployments.
- A “recommended tool sets by task” matrix (debugging vs refactor vs docs vs CI vs security review).
- Local mirrors for non-Agent-SDK docs that are still essential in practice (Claude Code settings/permission rules, tool reference, sandboxing).

## Using Claude Agent SDK via OpenRouter

If you would like to use the Agent SDK with other non-Anthropic models, you can do so by pointing the SDK at the OpenRouter API. See [OpenRouter support](references/openrouter-support.md) for more details.

For full OpenRouter documentation, see [OpenRouter documentation](https://openrouter.ai/docs/llms.txt).