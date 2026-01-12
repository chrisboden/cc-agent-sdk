# Claude Agent SDK Skill

A Claude Code skill providing an on-ramp and offline reference for building autonomous agents with the Claude Agent SDK.

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
