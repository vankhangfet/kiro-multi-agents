---
inclusion: always
---

# Spec-Driven Workflow

## 🔁 SESSION START — Check for In-Progress Work First

**Before doing anything else — before reading the user's message, before creating a new spec — run this check:**

```bash
cat .kiro/specs/currentspec.md 2>/dev/null || echo "NO_ACTIVE_SPEC"
cat .kiro/specs/pm-state.md 2>/dev/null || echo "NO_PM_STATE"
```

If `pm-state.md` contains `WAITING_*`, the PM agent is mid-conversation with the user. Do NOT proceed — the PM is handling this request. Stop and wait.

### If output is a slug (e.g. `2026-06-15-todo-app`) → RESUME MODE

An active spec exists. Do NOT create a new spec. Resume from where it left off:

1. Detect the mode:
   - `ls .kiro/specs/<slug>/prd/requirements.md 2>/dev/null` → NEW_FEATURE mode
   - `ls .kiro/specs/<slug>/bug-report.md 2>/dev/null` → BUG_FIX mode
   - `ls .kiro/specs/<slug>/refactor-scope.md 2>/dev/null` → REFACTOR mode
2. Read `.kiro/specs/<slug>/tasks.md`
3. Find the **first group** that has any task still marked `[ ]`
4. If **no `[ ]` tasks remain** → spec is complete; run `rm .kiro/specs/currentspec.md` and tell the user it's done
5. If `[ ]` tasks exist → enter the **Execution Loop** for the detected mode — start at the first incomplete group
6. Skip every group where all tasks are `[x]` — do not re-run completed work

**Resume is silent** — do not ask the user "should I continue?" — just continue.

**Hang prevention**: If a task has been `[ ]` for more than one session restart without progress, mark it `[!]` with a note "stale — needs manual review" and report it to the user instead of dispatching again.

### If output is `NO_ACTIVE_SPEC` → NEW REQUEST MODE

No active spec. The architect reads its dispatch context (`Mode:` field) and follows the FIRST ACTION section in `architect.md`.

---

## ⚡ EXECUTION LOOP — Run Until All Tasks Are `[x]`

Once spec.md and tasks.md exist, enter this loop and **do not exit until every task in tasks.md is `[x]`**:

### Step 6 — Enter the execution loop (run this loop until ALL tasks are `[x]`)

After ui-ux completes (or if there are no UI screens), enter this loop and **do not exit until every task in tasks.md is `[x]`**:

```
LOOP — repeat until no [ ] tasks remain:

  1. Read .kiro/specs/<slug>/tasks.md
  2. Find the FIRST group that has any task still marked [ ]
  3. If NO such group → ALL DONE. Delete currentspec.md and report done to user. EXIT.
  4. Pick the agent for that group:
       UI Design group     → agent_name="ui-ux"
       Research group      → agent_name="coder"
       Implementation      → agent_name="coder" or "ops"
       Review gate         → agent_name="reviewer"  ← then WAIT for PASS before next call
                             then agent_name="security-reviewer"
       Documentation       → agent_name="docs"
  5. Call subagent() ONCE. Wait for it to return before doing anything else.
       subagent(
         agent_name="<agent>",
         query="<task text + file paths + instruction to mark [x] in tasks.md when done>",
         relevant_context="<spec path only — pass paths, not file contents>"
       )
  6. Read tasks.md again (do NOT trust the return value — subagent may return "No result" even on success).
  7. If all tasks in that group are [x] → go to step 1.
     If any task is [!] → STOP. Report the blocked task to the user.
     If tasks still [ ] → retry ONCE with a shorter, more direct query.
                          If still [ ] after retry → mark [!] with note and STOP.
```

**⚠️ BANNED — these do not exist in Kiro CLI and will cause the workflow to hang:**
- DAG pipelines ("stage 1 → stage 2 pipeline")
- Multi-stage or chained subagent calls
- "Optimizing" by combining two groups into one subagent call
- Dispatching review and implementation simultaneously

**One subagent call = one group = one agent. Always sequential between groups.**

**This sequence is not optional.** Every user request for implementation must produce: a spec folder, spec.md, tasks.md, currentspec.md, ui design, implementation, review, and documentation — all executed autonomously without waiting for the user.

---

## When to Create a Spec

Create a spec before any non-trivial work — if it touches multiple files, involves architectural choices, or will be delegated to subagents.

## Directory Structure

```
.kiro/specs/currentspec.md  # Tracks current spec slug in use
.kiro/specs/YYYY-MM-DD-<slug>/
  spec.md        # Design decisions, requirements, constraints
  tasks.md       # Parallelized task list for execution
  review.md      # Reviewer findings per cycle
  security-review.md  # Security reviewer findings per cycle
  decisions.md   # Mid-flight decision log
  prd/           # Product requirements documents (when work involves product roadmap decisions)
    <descriptive-title>.md

issues/YYYY-MM-DD-<slug>/
  report.md      # Problem description, reproduction steps, impact, investigation
  summary.md     # Root cause, fix applied, prevention, status
```

Use a date-prefixed kebab-case slug for spec and issue folders. The date is the creation date in `YYYY-MM-DD` format, followed by a short descriptive slug (e.g., `2026-03-04-auth-api`, `2026-02-27-vpc-redesign`). This ensures chronological ordering when listing directories.

## Current Spec Tracking (`currentspec.md`)

`currentspec.md` contains a single line: the slug of the active spec. This is the source of truth for which spec is in progress.

```markdown
2026-03-04-auth-api
```

**Rules:**
- **Write** when creating a new spec (Phase 1, step 2) — set to the new slug
- **Read** at the start of any workflow phase to resolve the active spec path (`specs/<slug>/`)
- **Clear** (delete the file) when the spec is complete (all groups pass review)
- Only one spec is active at a time. Starting a new spec overwrites the previous slug.

## Spec Format (`spec.md`)

```markdown
# <Title>

## Context
Why this work exists. Link to issues, conversations, or prior decisions.

## Decision
What we're doing and why. Include alternatives considered and why they were rejected.

## Constraints
- Budget, timeline, team, technical limitations
- Non-functional requirements (performance, security, compliance)

## Design
Technical approach — interfaces, data models, flows, diagrams as needed.

## Risks
Known unknowns and mitigation strategies.
```

## Task Format (`tasks.md`)

Tasks are organized into parallel groups. All tasks within a group can be executed simultaneously by independent subagents. Groups execute sequentially — group 2 starts only after group 1 is complete.

```markdown
# Tasks: <Title>

Spec: `specs/<slug>/spec.md`

## Group 0: UI Design
- [ ] Design HTML mockups and screen transition flow | `.kiro/specs/<slug>/ui/`
  - **Agent**: `ui-ux`
  - **Accept**: `.kiro/specs/<slug>/ui/index.html` exists and links to all screen mockups and `transitions/flow.html`
  - **Verify**: `ls .kiro/specs/<slug>/ui/index.html .kiro/specs/<slug>/ui/transitions/flow.html`
  - **Constraints**: Output HTML only — no frameworks, no build tools. Skip this group only if the spec has zero user-facing screens.

## Group 1: <description>
- [ ] Task description | `path/to/relevant/files`
  - **Packages**: exact package names and versions (e.g., `strands-agents==0.1.x`, not `strands`)
  - **Accept**: measurable completion criteria
  - **Verify**: command(s) the subagent must run before marking complete
  - **Constraints**: explicit "do not" rules or known gotchas

## Group 2: <description>
- [ ] Task description | `path/to/relevant/files`
  - **Accept**: measurable completion criteria
  - **Verify**: command(s) the subagent must run before marking complete
```

### Task Rules

- Each task MUST be self-contained — a subagent should be able to complete it with no knowledge of sibling tasks in the same group
- Each task specifies relevant file paths and clear acceptance criteria
- Every task MUST include an **Accept** field with measurable criteria and a **Verify** field with at least one command to run
- Include **Packages** with exact PyPI/npm names and version constraints when the task involves dependencies
- Include **Constraints** to call out known naming gotchas, common mistakes, or explicit "do not" rules
- Subagents mark tasks `[x]` when complete — only after verification passes
- If a task is blocked or fails, mark it `[!]` and add a note below it
- Keep tasks small enough that one subagent can finish in a single session

### Group Ordering

The default task group ordering is:

1. **UI Design group** (Group 0 — mandatory when spec has user-facing screens; dispatched to `ui-ux` agent)
2. Research group (mandatory Group 1)
3. Implementation groups (one or more)
4. **Review gate** — all implementation groups must pass review before proceeding
5. Documentation group (mandatory final group)

**Deploys are out-of-band by default.** Most projects deploy via a CI/CD pipeline that runs after the spec is merged — the pipeline is not part of the spec's task list, and the spec finishes at the documentation group.

**In-spec deploy groups are the exception, not the rule.** Only include a deploy group when the spec itself must perform a deploy to be considered done — e.g., bootstrapping new infrastructure before a pipeline exists, or one-off migrations that don't fit the pipeline. A deploy group is any group whose tasks include `deploy.sh`, `cdk deploy`, infrastructure provisioning, or production-affecting operations.

When a spec does include an in-spec deploy group, the ordering is:

1. Research group
2. Implementation groups
3. **Review gate** — must issue PASS before deploy runs
4. Deploy/verification group
5. Documentation group (still the final group)

Documentation is always the final group regardless of whether a deploy group is present.

### Verification Requirements by Technology

**Verify** commands must actually validate the output, not just check that files parse or import:

| Technology | Weak (don't use) | Strong (use this) |
|-----------|-------------------|-------------------|
| CDK | `python3 -c "from stack import MyStack"` | `cdk synth StackName 2>&1` |
| CloudFormation | `cat template.yaml` | `aws cloudformation validate-template --template-body file://template.yaml` |
| Terraform | `terraform fmt` | `terraform validate` |
| Docker | `cat Dockerfile` | `docker build --check .` |
| Python | `python3 -c "import module"` | `python3 -m pytest tests/ -v` |
| TypeScript | `cat src/index.ts` | `npx tsc --noEmit` |

Import checks only prove a file parses — they do NOT validate that constructs, resources, or configurations are correct. Always use the tool's own validation command.

### Dependency Research

Every spec that introduces or relies on SDK/framework APIs MUST include a research step before implementation tasks.

**Group 1 must include a documentation research task** that:
1. Looks up current API docs for each key dependency (AWS docs, Context7, official docs)
2. Verifies constructor signatures, handler conventions, and import paths
3. Writes findings to the project's `docs/tech.md`
4. Implementation tasks in later groups reference `docs/tech.md` — not assumed APIs

**Mandatory Group 1 task template:**

```markdown
- [ ] Research and document SDK/framework APIs | `docs/tech.md`
  - **Accept**: `docs/tech.md` contains verified import paths, constructor signatures, and usage patterns for all key dependencies in this spec
  - **Verify**: Each documented pattern has a source citation (doc URL or `inspect.signature()` output)
  - **Constraints**: Implementation tasks MUST reference `docs/tech.md` — do not write code against unverified APIs
```

**Additional requirements for alpha/preview packages:**
- Pin exact versions in the spec (no ranges)
- Run `inspect.signature()` or equivalent to verify actual API surface
- Flag in spec Constraints section which deps are alpha vs stable

### Mandatory Review Gate

Every spec MUST include a review gate after all implementation groups complete. The orchestrator delegates to the `reviewer` subagent to inspect all implementation work.

- **Default (no in-spec deploy group):** the review gate is the second-to-last group, immediately before documentation.
- **Spec includes an in-spec deploy group (rare — see Group Ordering):** the review gate runs before deploy (research → implementation → review gate → deploy → documentation).

**Mandatory review gate task template:**

```markdown
## Group N: Review gate
- [ ] Code review of all implementation groups | `.kiro/specs/<slug>/review.md`
  - **Accept**: Reviewer has written findings to `review.md` with verdict PASS. Zero critical findings, zero warnings.
  - **Verify**: `grep -i 'verdict.*pass' .kiro/specs/<slug>/review.md`
  - **Constraints**: Do NOT proceed to the next group until this passes. Maximum 3 review cycles — escalate to user if still failing.
```

### Mandatory Final Group: Documentation Update

The last group in every `tasks.md` MUST include a documentation update task. Documentation written against finished, reviewed code is accurate documentation. Delegate this task to the `docs` subagent.

**Mandatory final group task template:**

```markdown
## Group N: Documentation
- [ ] Write arc42 architecture document, C4 diagrams, and update README | `docs/architecture.md`, `docs/c4.md`, `README.md`
  - **Agent**: `docs`
  - **Accept**:
    - `docs/architecture.md` exists with all 12 arc42 sections filled from the spec and code
    - `docs/c4.md` exists with Level 1 (Context), Level 2 (Container), and Level 3 (Component) diagrams using real names from the codebase
    - `README.md` reflects all user-facing changes from this spec
    - No TODO/FIXME/PLACEHOLDER text in any of the above files
  - **Verify**:
    - `ls docs/architecture.md docs/c4.md`
    - `grep -r 'TODO\|FIXME\|PLACEHOLDER' docs/architecture.md docs/c4.md README.md || true`
  - **Constraints**:
    - Read `.kiro/skills/arc42/SKILL.md` for the arc42 template before writing
    - Read `.kiro/skills/c4/SKILL.md` for the C4 diagram templates before writing
    - All 12 arc42 sections must be populated — "N/A — <reason>" is acceptable, blank is not
    - All C4 diagrams must use real names from the implementation code — no generic placeholders
    - Do not document features that were descoped or marked `[!]`
    - If files already exist, update only sections affected by this spec
```

What to update (check each):
- **README.md** — if user-facing behavior, CLI commands, config, dependencies, or folder structure changed
- **Architecture docs** — if services, data flows, or integration patterns changed
- **Inline docstrings** — if public function/class signatures changed
- **Runbooks** — if operational procedures or deployment steps changed

### Parallelization Guidelines

When structuring groups, maximize parallelism:
- **Test skeletons go in early groups** — define expected behavior before implementation
- Implementation tasks reference the tests they must make pass
- Tasks with no shared file writes go in the same group
- Tasks that produce outputs consumed by later tasks go in earlier groups
- Infrastructure before application code
- Shared libraries/interfaces before consumers
- Tests can often parallel with implementation if interfaces are defined first

## Review Format (`review.md`)

The reviewer writes findings here. Each review cycle gets its own section.

```markdown
# Review: <Title>

## Cycle 1 — <date>
Reviewing: Group 1 tasks

### Critical
- [file:line] Description of issue and recommended fix

### Warning
- [file:line] Description of issue and recommended fix

### Suggestion
- [file:line] Description of improvement

### Tests
- [ ] All tests passing
- [ ] Test coverage adequate for changes

### Verdict: PASS | FAIL
```

Verdict is **FAIL** if any Critical or Warning findings exist, or tests are not passing. Otherwise **PASS**.

## Security Review Format (`security-review.md`)

The security reviewer writes findings here. The security review happens after the general review passes. Each cycle gets its own section.

```markdown
# Security Review: <Title>

## Cycle 1 — <date>
Reviewing: Groups 1-N

### Critical
- [file:line] Description of vulnerability and remediation

### Warning
- [file:line] Description of risk and recommended mitigation

### Suggestion
- [file:line] Description of hardening opportunity

### Verdict: PASS | FAIL
```

Verdict is **FAIL** if any Critical or Warning security findings exist. Otherwise **PASS**.

## Decisions Log (`decisions.md`)

Records decisions made during implementation that aren't significant enough for the spec but need to be tracked. Prevents the same question from being re-asked across cycles.

```markdown
# Decisions: <Title>

## <date> — <short description>
**Context**: What prompted the decision
**Decision**: What was decided
**Rationale**: Why
```

## Product Requirements Document (`prd.md`)

Create a PRD when the work involves a product roadmap decision — new features, feature changes, deprecations, or anything that affects what the product does for users. Not needed for purely technical/infrastructure work with no user-facing impact.

- **Location**: `prd/<descriptive-title>.md` within the spec folder
- **File naming**: Use a descriptive kebab-case title (e.g., `prd/user-auth-sso-support.md`)

```markdown
# PRD: <Title>

## Problem Statement
What user problem or opportunity this addresses.

## Goals
- Measurable outcomes this work should achieve

## Non-Goals
- What this work explicitly does NOT cover

## User Stories
- As a [persona], I want [action] so that [outcome]

## Requirements
### Must Have
- [requirement]

### Should Have
- [requirement]

### Won't Have (this iteration)
- [requirement]

## Success Metrics
How we measure whether this achieved its goals.

## Open Questions
Unresolved product decisions that need stakeholder input.
```

## Issues (`issues/`)

Issues track bugs, problems, and investigations. They live at the project root in `issues/YYYY-MM-DD-<slug>/`.

### Issue Report (`report.md`)

```markdown
# Issue: <Title>

## Summary
One-line description of the problem.

## Impact
Who/what is affected and severity.

## Reproduction
Steps to reproduce, environment details, relevant logs.

## Investigation
What was checked, what was ruled out, root cause analysis.
```

### Issue Summary (`summary.md`)

Written after the issue is resolved.

```markdown
# Resolution: <Title>

## Root Cause
What caused the issue.

## Fix Applied
What was changed and where.

## Prevention
What prevents recurrence (tests, monitoring, guardrails).

## Status
RESOLVED | MITIGATED | WONT_FIX
```

## Development Loop

### Phase 1: Plan
1. **Research** — gather context, explore codebase, check docs
2. **SDK/Framework research** — for each dependency, look up current API docs using AWS documentation search and Context7. Write verified patterns, import paths, and constructor signatures to the project's `docs/tech.md`
3. **Spec** — create the spec folder `mkdir .kiro/specs/<YYYY-MM-DD-slug>/`, write `spec.md` with decisions and design, then write the slug to `.kiro/specs/currentspec.md`
4. **Plan** — create `tasks.md` with parallelized groups (include a `ui-design` task in Group 0 if the spec has user-facing screens)

### Phase 1.5: UI Design (mandatory for any spec with user-facing screens)

After writing `spec.md` and `tasks.md`, **immediately** dispatch the `ui-ux` subagent before any implementation work. Do not skip this step for any spec that involves screens, forms, dashboards, or any visual UI.

Use the `subagent` tool:
```
subagent(
  agent_name="ui-ux",
  query="Read the spec and design HTML mockups for every screen described. Output to .kiro/specs/<slug>/ui/: screens/NN-name.html per screen, transitions/flow.html for the animated flow, index.html as the navigation hub, design-system.md documenting design choices. Mark the ui-design task [x] in tasks.md when done.",
  relevant_context="<paste the full content of spec.md here>"
)
```

Wait for the `ui-ux` agent to complete before starting Phase 2. Verify `.kiro/specs/<slug>/ui/index.html` exists.

**Only skip Phase 1.5** if the spec is purely backend, CLI, or infrastructure with zero user-facing screens.

### Phase 2: Build (per group)
1. **Read `.kiro/specs/currentspec.md`** to resolve the active spec slug and path
2. **Delegate via `subagent` tool** — use the `subagent` tool to launch group tasks to `coder` and/or `ops` agents in parallel. Each spawned agent runs **completely independently** with no access to this conversation — pass everything it needs in `query` and `relevant_context` (spec content, task definition, file paths).
   ```
   subagent(
     agent_name="coder",
     query="<specific task instruction — what to implement, where to write output, how to mark complete>",
     relevant_context="<full spec.md content + the specific task definition from tasks.md>"
   )
   ```
3. **Verify completion** — confirm all tasks in the group are `[x]`
4. **Run tests** — execute the test suite, confirm all tests pass
5. **Review (mandatory gate)** — delegate to `reviewer` using the `subagent` tool, who writes findings to `review.md`. Do NOT proceed to the next group until the review verdict is PASS. This step is not optional — skipping review is a workflow violation.
6. **Security review (mandatory gate)** — after the general review passes, delegate to `security-reviewer` using the `subagent` tool, who writes findings to `security-review.md`. Do NOT proceed until both reviews pass.

> ⚠️ **ANTI-PATTERN — DO NOT PARALLELIZE REVIEW GATES**
>
> Review (step 5), security review (step 6), and documentation are SEQUENTIAL gates, not parallel tasks.
> The correct order is: review → wait for PASS → security review → wait for PASS → next group.
> NEVER launch review, security-review, and documentation subagents simultaneously.
> This is the most common workflow violation. Speed does not justify skipping gates.

> ⚠️ **SUBAGENT TOOL — NOT `/spawn`**
>
> Always use the `subagent` tool to delegate tasks. The `/spawn` command does not exist in Kiro CLI.
> Subagents receive ONLY what you pass in `query` and `relevant_context` — they cannot see this conversation.
> Always paste the full spec content and task definition into `relevant_context`.

### Phase 3: Fix (if needed)
1. **Read `.kiro/specs/currentspec.md`** to resolve the active spec
2. **Evaluate reviews** — read `review.md` and `security-review.md` for the current cycle
3. **If FAIL** — create fix tasks as a new group in `tasks.md` (e.g., `## Fix Group 1: Address review cycle 1`), then go to step 1 of Phase 2
4. **If PASS** — proceed to next group (back to Phase 2 step 1) or finish
5. **On completion** (all groups pass) — delete `.kiro/specs/currentspec.md`

### Completion Criteria

The loop stops when ALL of the following are true:
- **Zero critical findings** in the latest review cycle
- **Zero warnings** in the latest review cycle
- **Zero critical findings** in the latest security review cycle
- **Zero warnings** in the latest security review cycle
- **All tests passing**
- **All tasks marked `[x]`**

Suggestions do NOT block completion — log them for future improvement.

### Loop Safeguards
- Maximum 3 review cycles per group. If still failing after 3, escalate to the user with a summary of unresolved criticals.
- Log each decision made during fixes in `decisions.md` to prevent re-litigation.
