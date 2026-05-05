---
name: relay-recovery-playbook
description: |
  Recovery sequences for common Relay smoke-test and environment blockers.
  Covers Power Pages provisioning failures, missing Power Pages triggers in
  Power Automate, and Model-Driven App deployment recovery patterns so agents
  can continue from prior evidence instead of repeating blind retries.
trigger_keywords:
  - recovery
  - stateerrorconfiguration
  - operationfailed
  - power pages recovery
  - maker blocked
  - missing trigger
  - relay blocked
allowed_tools:
  - Read
---

# Relay Recovery Playbook

Use this skill when Relay is blocked by environment, maker-surface, or deployment-state problems
that are not ordinary repo drift. The goal is to preserve a proven recovery order and stop repeated
blind retries.

---

## Power Pages — StateErrorConfiguration / OperationFailed

If Power Pages maker is disconnected or the site shows `StateErrorConfiguration` / `OperationFailed`:

1. **Verify the local site identity**
   - Check `.powerpages-site/website.yml`
   - Confirm the `id` points to the live Dataverse `adx_website` record, not a stale/deleted site

2. **Redeploy the code site**
   - Use:
     ```powershell
     pac pages upload-code-site --rootPath "<project-root>"
     ```
   - Do not use `pac pages upload` for code sites

3. **Restart the site**
   - Use the supported Power Pages admin restart route or the equivalent approved admin action

4. **Check website binding**
   - Confirm an `adx_websitebinding` row exists for the live hostname/subdomain
   - Recreate it if missing

5. **Revalidate under the owner/admin account**
   - Verify the active account separately in Power Pages and Power Automate
   - Do not assume one surface switch applies to the other

6. **Stop condition**
   - If the site still reports `StateErrorConfiguration` / `OperationFailed`, maker `/portals` still disconnects,
     or the Power Pages trigger still does not appear, classify the issue as:
     - `environment-blocked`
     - not a repo drift issue
   - Preserve the attempted recovery sequence in the handoff

---

## Power Automate — Power Pages trigger missing

If cloud-flow registration is blocked because the Power Pages trigger is not visible:

1. Verify the active account in Power Automate
2. Open **Automated cloud flow**
3. Search for both:
   - `Power Pages`
   - `When a Power Pages flow step is run`
4. If the trigger is still missing under the correct owner/admin account:
   - stop as environment-blocked
   - do not keep retrying generic flow builders

---

## Model-Driven App — sitemap/forms not taking effect

If generated MDA XML exists but the live app does not reflect it:

1. Export the solution
2. Patch sitemap/forms against the exported artifacts
3. Reimport the solution
4. Publish customizations
5. Verify the live app again before marking the phase complete

Do not treat file generation alone as successful deployment.

---

## Handoff rule

When using this playbook, always preserve:
- the blocker that remained true
- the exact steps tried, in order
- what changed after each step
- the next recommended action inside or outside Relay scope

Do not return a generic blocked summary.
