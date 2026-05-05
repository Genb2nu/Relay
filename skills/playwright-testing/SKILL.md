---
name: playwright-testing
description: |
  End-to-end UI testing for Power Platform apps using Microsoft's official
  power-platform-playwright-toolkit. Covers Canvas App iframe scoping,
  Model-Driven App grid/form components, authentication setup, Playwright MCP
  for AI-assisted test generation, and Page Object Model patterns. Used by
  Sentinel during Phase 6 verification.
trigger_keywords:
  - playwright
  - e2e test
  - ui test
  - canvas test
  - model driven test
  - browser test
  - end to end
  - automated testing
allowed_tools:
  - Read
  - Write
  - Bash
---

# Power Platform Playwright Testing

Sentinel uses this skill to generate, run, and report on end-to-end UI tests
for Canvas Apps and Model-Driven Apps built by Relay.

## Framework

Microsoft official: `power-platform-playwright-toolkit` — TypeScript, Playwright
test runner, Page Object Model, dual-domain auth, CI/CD ready.

## Prerequisites

```bash
npm init -y
npm install --save-dev @playwright/test power-platform-playwright-toolkit dotenv
npx playwright install msedge
```

## Project Structure (Sentinel generates this)

```
tests/
  e2e/
    canvas/<app-name>.test.ts
    mda/<app-name>.test.ts
    pages/CanvasAppPage.ts
    pages/MDAPage.ts
playwright.config.ts
.env
.playwright-ms-auth/    (gitignored — auth storage state)
```

---

## Authentication (human bootstrap — one-time)

```
ACTION REQUIRED — Playwright Auth (~3 min, one-time)

1. Terminal: npm run auth:headful
   Sign in with test user when browser opens
2. Verify the active account separately in each maker surface you will use (Power Apps, Power Pages, Power Automate)
3. Dismiss startup blockers such as coachmarks, onboarding panes, flyouts, account menus, stale side panels, and modal overlays
4. For MDA tests: npm run auth:mda:headful
5. Reply "Auth complete"
```

## Maker surface preflight (before browser-driven verification)

For Power Pages or cloud-flow-dependent scenarios, verify these before deeper automation:

1. Power Pages maker `/portals` loads for the intended owner/admin account
2. Power Automate trigger search exposes the documented Power Pages trigger when the scenario depends on it
3. The active account is correct in each relevant surface independently

If any of those fail, stop as `environment-blocked` instead of repeatedly retrying browser interactions.

## clearTransientBlockers helper pattern

Use a reusable helper before interacting with maker controls:

```typescript
async function clearTransientBlockers(page: Page): Promise<void> {
  const dismissTargets = [
    page.getByRole('button', { name: /got it|close|dismiss|skip/i }),
    page.getByRole('button', { name: /not now|maybe later/i }),
    page.getByLabel(/close/i),
  ];

  for (const target of dismissTargets) {
    const count = await target.count().catch(() => 0);
    if (count > 0) {
      await target.first().click().catch(() => {});
    }
  }
}
```

Call this after sign-in, after navigation to a maker surface, and again before concluding that a control is missing.

## .env Template (generated from state.json)

```env
POWER_APPS_BASE_URL=https://make.powerapps.com
POWER_APPS_ENVIRONMENT_ID=<from state.json>
CANVAS_APP_URL=https://apps.powerapps.com/play/e/<env-id>/a/<app-id>
CANVAS_APP_ID=<from plan-index.json>
MODEL_DRIVEN_APP_URL=https://<org>.crm.dynamics.com/main.aspx?appid=<app-guid>
MS_AUTH_EMAIL=<test-user@domain.com>
MS_AUTH_CREDENTIAL_TYPE=password
MS_USER_PASSWORD=<password>
```

## playwright.config.ts Template

```typescript
import { defineConfig } from '@playwright/test';
import { getStorageStatePath } from 'power-platform-playwright-toolkit';
import * as dotenv from 'dotenv';
dotenv.config();

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 120_000,
  retries: 1,
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    channel: 'msedge',
    storageState: getStorageStatePath(process.env.MS_AUTH_EMAIL!),
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    actionTimeout: 30_000,
    navigationTimeout: 60_000,
  },
  projects: [
    { name: 'setup', testMatch: '**/auth.setup.ts', use: { storageState: undefined } },
    { name: 'mda-setup', testMatch: '**/auth-mda.setup.ts', use: { storageState: undefined } },
    { name: 'default', testMatch: '**/canvas/**', dependencies: ['setup'] },
    { name: 'model-driven-app', testMatch: '**/mda/**', dependencies: ['setup', 'mda-setup'] },
  ],
});
```

---

## Canvas App Testing

### Critical: iframe scoping

ALL Canvas controls live inside an iframe:
```typescript
const canvasFrame = page.frameLocator('iframe[name="fullscreen-app-host"]');
// ALL locators must use canvasFrame, never page directly
```

### Critical: 60-second gallery timeout

```typescript
await canvasFrame
  .locator('[data-control-name="Gallery1"] [data-control-part="gallery-item"]')
  .first()
  .waitFor({ state: 'visible', timeout: 60_000 });
```

### Control interactions

```typescript
// Click button
await canvasFrame.locator('[data-control-name="SubmitButton"]').click();

// Fill text input
await canvasFrame.locator('input[aria-label="Training Title"]').fill('Test');

// Select gallery item by text
const item = canvasFrame
  .locator('[data-control-part="gallery-item"]')
  .filter({ has: canvasFrame.locator('[data-control-name="Title1"]').getByText('Annual') });
await item.click();

// Count gallery items
const count = await canvasFrame.locator('[data-control-part="gallery-item"]').count();
expect(count).toBeGreaterThan(0);

// Check status badge
await expect(canvasFrame.locator('[data-control-name="StatusBadge"]')).toContainText('Pending');
```

---

## Model-Driven App Testing

Use toolkit built-in components — never raw selectors for MDA grids:

```typescript
import { AppProvider, AppType, AppLaunchMode } from 'power-platform-playwright-toolkit';

const app = new AppProvider(page, context);
await app.launch({
  app: '<MDAName>',
  type: AppType.ModelDriven,
  mode: AppLaunchMode.Play,
  directUrl: process.env.MODEL_DRIVEN_APP_URL!,
});
const mda = app.getModelDrivenAppPage();

// Grid
await mda.grid.filterByKeyword('TR-00001');
await mda.grid.waitForGridLoad();
await mda.grid.openRecord({ rowNumber: 0 });
const value = await mda.grid.getCellValue(0, '<prefix>_column');

// Form
const status = await mda.form.getAttribute('<prefix>_requeststatus');
await mda.form.setAttribute('<prefix>_managercomments', 'Approved');
await mda.form.save();
await mda.form.switchTab('Approval');
```

---

## Page Object Model (Sentinel generates per project)

```typescript
// tests/e2e/pages/TrainingCanvasApp.ts
import { Page, FrameLocator } from '@playwright/test';

export class TrainingCanvasApp {
  private readonly frame: FrameLocator;

  constructor(page: Page) {
    this.frame = page.frameLocator('iframe[name="fullscreen-app-host"]');
  }

  get gallery()      { return this.frame.locator('[data-control-name="galRequests"]'); }
  get submitBtn()    { return this.frame.locator('[data-control-name="btnSubmit"]'); }
  get titleInput()   { return this.frame.locator('input[aria-label="Training Title"]'); }

  async waitForLoad() {
    await this.gallery.locator('[data-control-part="gallery-item"]').first()
      .waitFor({ state: 'visible', timeout: 60_000 });
  }

  async getRequestCount(): Promise<number> {
    return this.gallery.locator('[data-control-part="gallery-item"]').count();
  }

  async submitRequest(title: string) {
    await this.frame.locator('[data-control-name="iconNewRequest"]').click();
    await this.titleInput.fill(title);
    await this.submitBtn.click();
  }
}
```

---

## Playwright MCP — AI-assisted control discovery

Add to .vscode/mcp.json:
```json
{ "playwright": { "command": "npx", "args": ["@playwright/mcp"] } }
```

Sentinel uses MCP tools to inspect the live app:
- `browser_navigate` → go to app URL
- `browser_snapshot` → capture accessibility tree with data-control-name values
- Generate Page Object from discovered control names

---

## Test Data Conventions

```typescript
// Unique per run — prevents parallel conflicts
const title = `Test Training ${Date.now()}`;
```

Clean up after tests via Dataverse API in test.afterAll().

---

## Test Report (Sentinel produces docs/e2e-test-report.md)

```markdown
# E2E Test Report
| Test ID | Description | App | Result | Duration |
|---|---|---|---|---|
| TC-001 | Employee submits request | Canvas | PASS | 12s |
| TC-002 | Gallery filters by user | Canvas | PASS | 8s |
| TC-003 | Manager approves in MDA | MDA | PASS | 15s |

Summary: N total | N passed | N failed
Playwright report: npx playwright show-report
```
