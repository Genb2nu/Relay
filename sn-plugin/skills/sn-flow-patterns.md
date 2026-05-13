# SimplifyNext Flow Patterns

## Purpose

Standard Power Automate flow patterns that Forge-Flow must follow for all
SimplifyNext projects. Every flow must meet these standards.

---

## Flow Architecture Standards

### Every Flow Must Have

1. **Try-Catch pattern** — use Scope actions to wrap logic in try/catch/finally
2. **Error notification** — on catch, send email or Teams message to admin
3. **Run-only users** — every triggered flow must have run-only permissions configured
4. **Connection references** — never use personal connections; always use connection references
5. **Solution-scoped** — all flows must be inside the project solution

### Flow Naming Convention

`{Prefix}{EntityName}{Trigger}Flow`

Examples:
- `OpsRequestApprovalFlow`
- `OpsRequestReminderFlow`
- `OpsNotificationOnCreateFlow`

---

## Standard Flow Templates

### Approval Flow Pattern

```json
{
  "definition": {
    "triggers": {
      "When_a_row_is_added_or_modified": {
        "type": "OpenApiConnectionWebhook",
        "inputs": {
          "host": { "connectionName": "{prefix}_DataverseConnection" },
          "parameters": {
            "table": "{prefix}_{tablename}",
            "scope": "organization",
            "filterexpression": "statuscode eq 1"
          }
        }
      }
    },
    "actions": {
      "Try_Scope": {
        "type": "Scope",
        "actions": {
          "Start_approval": {
            "type": "OpenApiConnection",
            "inputs": {
              "host": { "connectionName": "{prefix}_ApprovalConnection" },
              "method": "post",
              "path": "/approvalRequests/synchronous",
              "body": {
                "title": "Approval required: @{triggerOutputs()?['body/title']}",
                "assignedTo": "@{variables('ApproverEmail')}",
                "details": "@{triggerOutputs()?['body/{prefix}_description']}"
              }
            }
          },
          "Update_record_on_outcome": {
            "type": "Switch",
            "expression": "@body('Start_approval')?['outcome']",
            "cases": {
              "Approved": {
                "actions": {
                  "Set_approved": {
                    "type": "OpenApiConnection",
                    "inputs": {
                      "host": { "connectionName": "{prefix}_DataverseConnection" },
                      "method": "patch",
                      "path": "/{prefix}_{tablename}/@{triggerOutputs()?['body/{prefix}_{tablename}id']}",
                      "body": { "statuscode": 2, "{prefix}_approvedby": "@{variables('ApproverEmail')}" }
                    }
                  }
                }
              },
              "Rejected": {
                "actions": {
                  "Set_rejected": {
                    "type": "OpenApiConnection"
                  }
                }
              }
            }
          }
        }
      },
      "Catch_Scope": {
        "type": "Scope",
        "runAfter": { "Try_Scope": ["Failed", "TimedOut"] },
        "actions": {
          "Send_error_notification": {
            "type": "OpenApiConnection",
            "inputs": {
              "host": { "connectionName": "{prefix}_OutlookConnection" },
              "method": "post",
              "path": "/Mail",
              "body": {
                "To": "@{variables('AdminEmail')}",
                "Subject": "Flow error: OpsRequestApprovalFlow",
                "Body": "@{result('Try_Scope')}"
              }
            }
          }
        }
      }
    }
  }
}
```

### Scheduled Reminder Flow Pattern

Use for: reminders, escalations, daily summaries.

```json
{
  "triggers": {
    "Recurrence": {
      "type": "Recurrence",
      "recurrence": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2026-01-01T08:00:00Z",
        "timeZone": "UTC"
      }
    }
  }
}
```

---

## Error Handling Requirements

Every flow must implement:

```
[Scope: Try]
  ← all business logic here

[Scope: Catch] (runs after Try if Failed or TimedOut)
  → Log error to Dataverse error log table (if exists)
  → Send notification to admin email via env var {prefix}_AdminEmail

[Scope: Finally] (optional, always runs)
  → Update "last run" timestamp if needed
```

---

## Self-Approval Prevention

For any approval flow, include this check before starting the approval:

```
Condition: triggerOutputs()?['body/createdby/systemuserid'] is equal to
           body('Get_approver_user')?['systemuserid']

If true: set statuscode to "Rejected - Self Approval Blocked"
         send notification to manager
If false: proceed with normal approval
```

---

## Activation Procedure

After importing a flow via `pac solution import`:

1. Wire connection references first (flows will fail to activate without them)
2. Activate via Dataverse API:
   ```
   PATCH /api/data/v9.2/workflows({flowId})
   { "statecode": 1, "statuscode": 2 }
   ```
3. Verify activation:
   ```
   GET /api/data/v9.2/workflows({flowId})?$select=statecode,statuscode
   → statecode: 1 (active)
   ```

Never activate flows via the Power Automate portal — always use the API
to ensure automation consistency.
