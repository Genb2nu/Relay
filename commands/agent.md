---
description: Talk directly to a specific Relay agent for a follow-up question, outside the normal workflow.
trigger_keywords:
  - relay agent
  - ask scout
  - ask warden
  - ask forge
---

# /relay:agent <agent_name>

When the user invokes this command with an agent name:

1. Validate the agent name is one of: `scout`, `drafter`, `auditor`, `warden`, `critic`, `vault`, `forge`, `forge-canvas`, `forge-mda`, `forge-flow`, `forge-pages`, `sentinel`.

2. Invoke the specified agent as a subagent with the user's follow-up question.

3. The agent runs in its normal context — it can read project files but follows its standard rules and tool restrictions.

4. Return the agent's response to the user.

Examples:
```
/relay:agent warden Can a user with the Employee role access the Approval table via Web API?
/relay:agent forge What PAC CLI command would export just the flows?
/relay:agent scout Can you re-interview me about the reporting requirements?
```

This does NOT change the project phase or state. It's a side-channel conversation that doesn't affect the workflow.
