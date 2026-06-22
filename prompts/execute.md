# Execute Current Spec

Read `.kiro/specs/currentspec.md` to resolve the active spec slug.
Read the spec at `.kiro/specs/<slug>/spec.md` and the task list at `.kiro/specs/<slug>/tasks.md`.

**Step 0 — UI Design (run once before any implementation group):**
If `.kiro/specs/<slug>/ui/index.html` does not exist yet, dispatch the `ui-ux` subagent first:
```
subagent(
  agent_name="ui-ux",
  query="Read the spec at .kiro/specs/<slug>/spec.md. Design HTML mockups for every screen described in the spec. Output to .kiro/specs/<slug>/ui/ — screens/NN-name.html per screen, transitions/flow.html for the animated flow, index.html as the hub, design-system.md for design choices. Mark the ui-design task [x] in tasks.md when done.",
  relevant_context="<full spec.md content>"
)
```
Wait for ui-ux to complete before executing implementation groups. Skip if the spec has no user-facing screens.

**Step 1+ — Implementation groups:**
Execute all incomplete task groups in order. For each group:

1. **Classify each task by owner** before executing:
   - Research / API verification → execute yourself (Architect) using your tools
   - Implementation → delegate to `coder` subagent
   - Infrastructure / deploy → delegate to `ops` subagent
   - UI/UX mockups & screen designs → delegate to `ui-ux` subagent
   - Review gate → delegate to `reviewer` subagent (then `security-reviewer`)
   - Documentation → delegate to `docs` subagent
2. Execute your tasks first — subagent tasks may depend on research output (e.g., `docs/tech.md`)
3. Use the `subagent` tool to delegate implementation tasks in parallel (where no dependencies exist) — set `agent_name` to `coder`, `ops`, `reviewer`, `security-reviewer`, or `docs`; pass full spec content and task definition in `relevant_context` (subagents have no access to this conversation)
4. Verify all tasks are marked `[x]` before proceeding to the next group
5. Run review and security review gates sequentially — do not skip or parallelize them
6. If review fails, create fix tasks and re-run

Continue until all groups are complete and all reviews pass.
