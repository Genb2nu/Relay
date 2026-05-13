# Deployment Checklist — {Project Name}

**Solution:** {solution_name}
**Version:** {version}
**Target Environment:** {target_env}
**Target URL:** {target_url}
**Deploying:** {name}
**Date:** {date}

---

## Pre-Deployment — Development Environment

### Quality Gates
- [ ] QA gate passed (`sentinel_approved = true` in `.sn/state.json`)
- [ ] All flows are active in development environment
- [ ] Canvas App passes App Checker at 0 errors (all 5 categories)
- [ ] MDA is published (`PublishAllXml` called after last change)
- [ ] No components exist outside the project solution

### Solution Preparation
- [ ] Solution version incremented: previous → **{version}**
  - Run: `pac solution version --solutionName {solution_name} --patchVersion {build}`
- [ ] Unmanaged solution exported to `dist/{solution_name}_unmanaged_{version}.zip`
- [ ] Managed solution exported to `dist/{solution_name}_managed_{version}.zip`
- [ ] Exported zip files are not corrupt (open in Power Platform admin to verify)

### Source Control
- [ ] All changes committed to source control
- [ ] Branch merged or PR approved
- [ ] Exported zip files committed to `dist/` folder

---

## Pre-Deployment — Target Environment

### Environment Access
- [ ] System Administrator or System Customiser role confirmed in target environment
- [ ] PAC CLI auth configured for target: `pac auth select`
- [ ] `pac solution list --environment {target_url}` runs without errors

### Publisher
- [ ] Publisher with prefix `{publisher_prefix}` exists in target environment
  - If not: create publisher in PPAC before importing
  - Publisher prefix MUST match exactly — mismatch causes import failure

### Connections (for flows)
- [ ] All required connections exist in target environment:
  - [ ] Dataverse connection (for `{prefix}_DataverseConnection`)
  - [ ] {Other connector} connection (for `{prefix}_{Connector}Connection`)
  - [ ] Note: connections must be created by a service account, not a personal account

### Environment Variables
- [ ] Current values noted for all environment variables:
  - `{prefix}_{VarName}`: current value = `{value}`
  - Target value for {target_env}: `{target_value}`
  - _(Update these in PPAC after import, before activating flows)_

### Backup (for upgrades)
- [ ] Current managed solution version backed up:
  - Run: `pac solution export --name {solution_name} --path dist/backup_{date}.zip --managed true --environment {target_url}`
- [ ] Backup tested (can be re-imported if needed)

---

## Import

- [ ] Managed solution imported:
  ```
  pac solution import \
    --path dist/{solution_name}_managed_{version}.zip \
    --environment {target_url} \
    --async \
    --force-overwrite
  ```
- [ ] Import completed without errors (monitor async status)
- [ ] Import completed with warnings only (document any warnings below)

**Import warnings (if any):**
```
{paste warnings here}
```

---

## Post-Import Configuration

### Connection References
Wire each connection reference to a live connection in {target_env}:

- [ ] `{prefix}_DataverseConnection` → connected to: {connection display name}
- [ ] `{prefix}_{Connector}Connection` → connected to: {connection display name}

Steps: PPAC → Solutions → {solution_name} → Connection References → wire each one

### Environment Variables
Set values for {target_env}:

- [ ] `{prefix}_{VarName}` set to: `{target_value}`

Steps: PPAC → Solutions → {solution_name} → Environment Variables → Current Value

### Flow Activation
Flows import as inactive. Activate each after wiring connections:

- [ ] {Prefix}ApprovalFlow → activated
- [ ] {Prefix}ReminderFlow → activated

Steps (API):
```
PATCH /api/data/v9.2/workflows({flowId})
{ "statecode": 1, "statuscode": 2 }
```

Or via portal: Power Automate → Solutions → {solution_name} → Flows → Turn On

---

## Post-Deployment Verification

### Smoke Tests
- [ ] Log in as a {Persona 1} user → can access the Canvas App / MDA
- [ ] Create a test record → record saves successfully
- [ ] Trigger the approval flow → approval email received
- [ ] Log in as a {Viewer Persona} → cannot create or delete records
- [ ] Check FLS: sensitive column hidden from viewer user

### Monitoring
- [ ] Flow run history checked — no immediate failures
- [ ] Canvas App opened on mobile browser (if applicable)
- [ ] MDA sitemap all areas accessible

---

## Rollback Plan

If the deployment fails or causes issues:

1. **Re-import backup:**
   ```
   pac solution import \
     --path dist/backup_{date}.zip \
     --environment {target_url} \
     --managed true \
     --force-overwrite
   ```

2. **If data was created under the new version:**
   - Do NOT delete the managed solution (this deletes all data)
   - Contact data admin to assess impact before any further action

3. **Escalate to:** {Technical Lead Name} at {contact}

---

## Sign-off

- [ ] Deployment completed successfully
- [ ] Smoke tests passed
- [ ] Client/stakeholder notified

**Deployed by:** {name}
**Completed at:** {timestamp}
**Notes:** {any notes}
