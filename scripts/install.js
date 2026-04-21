#!/usr/bin/env node
/**
 * Relay — Install Script
 *
 * Detects available AI coding tools (Claude Code, GitHub Copilot CLI) and
 * installs the Relay plugin on whichever is present.
 *
 * Usage:
 *   node install.js
 *
 * Or via curl:
 *   curl -fsSL https://raw.githubusercontent.com/Genb2nu/relay/main/scripts/install.js | node
 */

const { execSync } = require("child_process");

function commandExists(cmd) {
  try {
    execSync(`which ${cmd}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function run(cmd, opts = {}) {
  try {
    return execSync(cmd, { encoding: "utf8", stdio: "pipe", ...opts }).trim();
  } catch (e) {
    if (!opts.ignoreError) {
      console.error(`  ✗ Failed: ${cmd}`);
      console.error(`    ${e.message}`);
    }
    return null;
  }
}

console.log("\n🔗 Relay — Power Platform AI Squad Installer\n");

// --- Check prerequisites ---
console.log("Checking prerequisites...\n");

const prereqs = [
  { cmd: "node", label: "Node.js" },
  { cmd: "git", label: "Git" },
  { cmd: "jq", label: "jq (JSON processor)" },
];

const optionalPrereqs = [
  { cmd: "pac", label: "Power Platform CLI (pac)" },
  { cmd: "az", label: "Azure CLI (az)" },
];

let missingRequired = false;

for (const { cmd, label } of prereqs) {
  if (commandExists(cmd)) {
    console.log(`  ✓ ${label}`);
  } else {
    console.log(`  ✗ ${label} — REQUIRED`);
    missingRequired = true;
  }
}

for (const { cmd, label } of optionalPrereqs) {
  if (commandExists(cmd)) {
    console.log(`  ✓ ${label}`);
  } else {
    console.log(`  ⚠ ${label} — optional but recommended`);
  }
}

if (missingRequired) {
  console.error("\n✗ Missing required tools. Install them and re-run.\n");
  process.exit(1);
}

// --- Detect AI coding tools ---
console.log("\nDetecting AI coding tools...\n");

const tools = [];

if (commandExists("claude")) {
  console.log("  ✓ Claude Code CLI detected");
  tools.push("claude");
}

if (commandExists("copilot")) {
  console.log("  ✓ GitHub Copilot CLI detected");
  tools.push("copilot");
}

if (tools.length === 0) {
  console.error("  ✗ Neither Claude Code nor GitHub Copilot CLI found.");
  console.error("    Install at least one:");
  console.error("    - Claude Code: https://claude.ai/code");
  console.error("    - Copilot CLI: https://docs.github.com/en/copilot");
  process.exit(1);
}

// --- Determine repo URL ---
// If run from a cloned repo, use local path. Otherwise, use GitHub.
const repoUrl = process.env.RELAY_REPO || "https://github.com/Genb2nu/relay";
const isLocal = !repoUrl.startsWith("http");

console.log(`\nPlugin source: ${isLocal ? "local (" + repoUrl + ")" : repoUrl}\n`);

// --- Install on each detected tool ---
for (const tool of tools) {
  console.log(`\nInstalling Relay on ${tool === "claude" ? "Claude Code" : "GitHub Copilot CLI"}...`);

  if (tool === "claude") {
    console.log("  Adding marketplace...");
    console.log(`  Run in Claude Code: /plugin marketplace add ${repoUrl}`);
    console.log("  Then: /plugin install relay@relay-marketplace");
  } else if (tool === "copilot") {
    console.log("  Adding marketplace...");
    console.log(`  Run in Copilot CLI: copilot plugin marketplace add ${repoUrl}`);
    console.log("  Then: copilot plugin install relay@relay-marketplace");
  }
}

// --- Check for Superpowers and Power Platform skills ---
console.log("\n--- Recommended companion plugins ---\n");
console.log("  Superpowers (workflow backbone):");
console.log("    /plugin marketplace add obra/superpowers-marketplace");
console.log("    /plugin install superpowers@superpowers-marketplace\n");
console.log("  Microsoft Power Platform skills:");
console.log("    /plugin marketplace add microsoft/power-platform-skills");
console.log("    /plugin install power-pages@power-platform-skills");
console.log("    /plugin install model-apps@power-platform-skills");
console.log("    /plugin install canvas-apps@power-platform-skills");
console.log("    /plugin install code-apps@power-platform-skills\n");
console.log("  Dataverse MCP:");
console.log("    Complete labs at https://github.com/microsoft/Dataverse-MCP\n");

console.log("✓ Relay installation guide complete.\n");
console.log("Next steps:");
console.log("  1. Run the plugin install commands above in your AI coding tool");
console.log("  2. Open a project folder and run /relay:start");
console.log("  3. Provide a project brief and watch the squad work\n");
