# Claude Agent SDK Skill

This Claude Agent SDK skill provides an on-ramp and offline reference for building autonomous agents with the Claude Agent SDK.

# Agent SDK overview

The Claude Agent SDK lets you use Claude Code as a library, to build AI agents that autonomously read files, run commands, search the web, edit code, and more. The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.


```python Python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"])
    ):
        print(message)  # Claude reads the file, finds the bug, edits it

asyncio.run(main())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix the bug in auth.py",
  options: { allowedTools: ["Read", "Edit", "Bash"] }
})) {
  console.log(message);  // Claude reads the file, finds the bug, edits it
}
```

The Agent SDK includes built-in tools for reading files, running commands, and editing code, so your agent can start working immediately without you implementing tool execution. Dive into the quickstart or explore real agents built with the SDK:

## Capabilities

Everything that makes Claude Code powerful is available in the SDK:

Your agent can read files, run commands, and search codebases out of the box. Key tools include:

| Tool | What it does |
|------|--------------|
| **Read** | Read any file in the working directory |
| **Write** | Create new files |
| **Edit** | Make precise edits to existing files |
| **Bash** | Run terminal commands, scripts, git operations |
| **Glob** | Find files by pattern (`**/*.ts`, `src/**/*.py`) |
| **Grep** | Search file contents with regex |
| **WebSearch** | Search the web for current information |
| **WebFetch** | Fetch and parse web page content |
| **[AskUserQuestion](/docs/en/agent-sdk/user-input#handle-clarifying-questions)** | Ask the user clarifying questions with multiple choice options |


### Claude Code features

The SDK also supports Claude Code's filesystem-based configuration. To use these features, set `setting_sources=["project"]` (Python) or `settingSources: ['project']` (TypeScript)  in your options.

| Feature | Description | Location |
|---------|-------------|----------|
| [Skills](/docs/en/agent-sdk/skills) | Specialized capabilities defined in Markdown | `.claude/skills/SKILL.md` |
| [Slash commands](/docs/en/agent-sdk/slash-commands) | Custom commands for common tasks | `.claude/commands/*.md` |
| [Memory](/docs/en/agent-sdk/modifying-system-prompts) | Project context and instructions | `CLAUDE.md` or `.claude/CLAUDE.md` |
| [Plugins](/docs/en/agent-sdk/plugins) | Extend with custom commands, agents, and MCP servers | Programmatic via `plugins` option |


## What This Is

This skill gives Claude Code (and agents running on it) quick access to:

- **Curated defaults** for coding agents (tools, permissions, sessions)
- **Offline documentation** mirrored from official sources in `references/`
- **Quickstart patterns** showing idiomatic SDK usage in Python and TypeScript

## Installation

Copy or symlink this folder into your Claude Code skills directory, or include it in a project's `.claude/skills/` folder.

## Usage

Once installed, Claude Code can invoke this skill when building SDK-based agents. The skill provides guidance on:

- SDK setup (Python: `pip install claude-agent-sdk`, TS: `npm install @anthropic-ai/claude-agent-sdk`)
- Permission modes and safe tool configuration
- Session management for multi-step workflows
- MCP integrations and custom tools
- Structured outputs with JSON schemas
- Deployment patterns

## Documentation Index

See [SKILL.md](SKILL.md) for the full navigation guide. Key references:

| Topic | File |
|-------|------|
| Overview & concepts | `references/overview.md` |
| Quickstart | `references/quickstart.md` |
| Python API | `references/python.md` |
| TypeScript API | `references/typescript.md` |
| Permissions | `references/permissions.md` |
| Sessions | `references/sessions.md` |
| MCP | `references/mcp.md` |
| Hosting | `references/hosting.md` |

## License

Reference documentation is mirrored from Anthropic's official Claude Agent SDK docs.

## Changelog

View the full changelog for SDK updates, bug fixes, and new features:

- **TypeScript SDK**: [view CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
- **Python SDK**: [view CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)
