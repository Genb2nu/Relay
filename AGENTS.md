# Relay — Agent Development Guidelines

This document describes the conventions for contributing to or extending the
Relay plugin.

## Agent Persona Format

All agent personas live in `agents/<name>.md` and follow this structure:

```yaml
---
name: <agent_codename>         # lowercase, matches filename
description: |                 # multi-line description
  What this agent does and when to invoke it.
model: opus | sonnet           # default model tier
tools:                         # allowed tool list
  - Read
  - Write
  - Bash
  - WebSearch
  - Edit
---
```

Below the frontmatter is the agent's system prompt in Markdown.

## Rules for Agent Personas

1. **Single responsibility.** Each agent does one job. If you're writing an
   agent that does two things, it should be two agents.
2. **Explicit tool restrictions.** List only the tools the agent needs. The
   `PreToolUse` hook enforces this at runtime.
3. **Structured handoff.** Every agent must end with a "Handoff" section that
   defines the exact format of the return value to Conductor.
4. **File write restrictions.** Specify which files the agent may write to.
   The hook enforces this.
5. **No cross-invocation.** Agents never invoke other agents. Only Conductor
   dispatches subagents.

## Skill Format

Skills live in `skills/<name>/SKILL.md` and follow the standard YAML frontmatter
format used by both Superpowers and Microsoft's power-platform-skills:

```yaml
---
name: <skill-name>
description: |
  What knowledge this skill provides and when to reference it.
trigger_keywords:
  - keyword1
  - keyword2
allowed_tools:
  - Read
  - WebSearch
---
```

## Command Format

Commands live in `commands/<name>.md` with:

```yaml
---
description: Short description shown in /help
trigger_keywords:
  - keyword1
  - keyword2
---
```

## Hook Scripts

Hooks live in `hooks/scripts/` and are registered in `hooks/hooks.json`.
Exit codes: 0 = allow, 2 = block. Scripts receive tool input on stdin as JSON.

## Testing Changes

After modifying any agent, skill, command, or hook:

1. Load Relay locally: `claude --plugin-dir /path/to/relay`
2. Run `/relay:start` with the Training Request pilot brief
3. Verify the modified component works in the full workflow
4. Check that hooks correctly enforce restrictions
