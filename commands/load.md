---
description: |
  Load project documents into Relay's context before starting. Drop BRDs,
  wireframes, task lists, data models, emails, or any project file into the
  context/ folder, then run this command. Scout will read all documents first
  and ask only about gaps the documents didn't cover — turning a 15-question
  discovery into 2-3 targeted questions.
trigger_keywords:
  - relay load
  - load context
  - load documents
  - load project docs
  - attach documents
---

# /relay:load

When the user invokes this command:

1. Check if a `context/` folder exists in the current directory.
   - If not: create it and tell the user:
     "I've created a `context/` folder. Drop your project documents in there
     (BRDs, wireframes, task lists, data models, emails, process flows — any
     format). Then run `/relay:load` again."
   - Stop here if the folder was just created.

2. If `context/` exists, list all files inside it:
   ```
   Found in context/:
   - <filename> (<type>)
   - ...
   ```

3. If no files are in the folder, tell the user to add documents and try again.

4. If files exist, read every file in `context/`. For each file:
   - Markdown / text / Word: read the full content
   - PDF: extract text content
   - Images (PNG, JPG): describe what you see — wireframes, diagrams, screenshots
   - Excel / CSV: summarise the structure and key data
   - PowerPoint: summarise slide titles and key points

5. Produce a structured context summary and write it to `.relay/context-summary.md`:

   ```markdown
   # Project Context Summary

   ## Documents loaded
   - <filename>: <one-line description of what it contains>

   ## What I understand about this project
   <3-5 bullet points synthesising the key information across all documents>

   ## Entities / Data identified
   <List any tables, entities, or data structures mentioned across the documents>

   ## Personas / Users identified
   <List any user roles or personas mentioned>

   ## Processes / Flows identified
   <List any business processes or workflow steps described>

   ## Constraints / Requirements identified
   <List any technical, business, or security constraints mentioned>

   ## Gaps — things the documents did NOT cover
   <List anything that a full requirements document would need but isn't in the provided docs>
   ```

6. Tell the user:
   "I've read all your documents and summarised the context. Here's what I
   understand so far:

   <brief 3-line summary>

   **Gaps I'll need to ask about:**
   <list the gaps from the summary>

   Run `/relay:start` when you're ready — Scout will use this context and ask
   only about the gaps above."

7. Update `.relay/state.json` to include `"context_loaded": true` so Conductor
   and Scout know to check `.relay/context-summary.md` before asking questions.

## Important notes

- This command works whether or not a project has been started yet
- It can be re-run after adding more documents — it merges with any existing summary
- Documents are NOT deleted from `context/` after loading — they stay available
  for agents to reference throughout the project
- If a wireframe image is provided, Stylist can use it as design direction input
