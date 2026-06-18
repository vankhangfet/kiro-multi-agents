---
inclusion: always
---

# Spec-Driven Workflow

## 🔁 SESSION START — Check for In-Progress Work First

**Before doing anything else — before reading the user's message, before creating a new spec — run this check:**

```bash
cat .kiro/specs/currentspec.md 2>/dev/null || echo "NO_ACTIVE_SPEC"
```

### If output is a slug (e.g. `2026-06-15-todo-app`) → RESUME MODE

An active spec exists. Do NOT create a new spec. Resume from where it left off:

1. Read `.kiro/specs/<slug>/tasks.md`
2. Find the **first group** that has any task still marked `[ ]`
3. If **no `[ ]` tasks remain** → spec is complete; run `rm .kiro/specs/currentspec.md` and tell the user it's done
4. If `[ ]` tasks exist → go directly to the **Execution Loop** (Step 6 of the MANDATORY section below) — enter the loop at the first incomplete group
5. Skip every group where all tasks are `[x]` — do not re-run completed work, do not re-dispatch completed agents

**Resume is silent** — do not ask the user "should I continue?" — just continue.

**Hang prevention**: If a task has been `[ ]` for more than one session restart without progress, mark it `[!]` with a note "stale — needs manual review" and report it to the user instead of dispatching again.

### If output is `NO_ACTIVE_SPEC` → NEW REQUEST MODE

No active spec. Read the user's message and follow the MANDATORY section below.

---

## ⚡ MANDATORY: When Dispatched by PM Agent (PRD Confirmed by User)

The architect only runs this section when dispatched by the PM agent after user confirmation. The PM agent always dispatches with `relevant_context` containing `"User confirmed requirements: YES"`.

**If you are the architect and were NOT dispatched by PM** (i.e., you received a direct user message with no PRD): respond with: "Please describe your request and I'll hand it to the PM agent for requirements gathering." Do not create spec or tasks directly.

### Step 1 — Read the confirmed PRD
```bash
cat .kiro/specs/<slug>/prd/requirements.md
```
The slug is in `relevant_context` from the PM dispatch. This PRD has been user-confirmed — use it as the single source of truth.

### Step 2 — Create spec.md from the PRD

Write `.kiro/specs/<slug>/spec.md` mapping PRD sections:
- **Context** → PRD section 1 (Problem Statement) + section 2 (Users & Personas)
- **Decision** → PRD section 3 (Functional Requirements) — list the epics and Must Have user stories
- **Constraints** → PRD section 4 (NFRs) + section 5 (Technical Constraints)
- **Design** → PRD section 6 (Screens & User Flows)
- **Risks** → PRD section 7 (Risk & Assumptions)

### Step 3 — Write currentspec.md
Write `.kiro/specs/currentspec.md` containing only the slug. (Already written by PM — overwrite to confirm.)

### Step 4 — Write tasks.md
Write `.kiro/specs/<slug>/tasks.md` with Group 0 (UI Design), Group 1 (Research), implementation groups, a Review gate group, and a Documentation group.
Scope implementation tasks to the PRD's **Must Have** user stories (US-xx) — reference their IDs in each task (e.g., `Implement US-01: user login screen`).

### Step 5 — Dispatch ui-ux agent (if spec has any user-facing screens)
Call the `subagent` tool immediately:
```
subagent(
  agent_name="ui-ux",
  query="Design HTML mockups for every screen in the spec. Output to .kiro/specs/<slug>/ui/: screens/NN-name.html per screen, transitions/flow.html for the animated flow, index.html as the hub, design-system.md for design choices. Mark the ui-design task [x] in .kiro/specs/<slug>/tasks.md when done.",
  relevant_context="<paste the full text of the spec.md you just wrote>"
)
```

### Step 6 — Enter the execution loop (run this loop until ALL tasks are `[x]`)

After ui-ux completes (or if there are no UI screens), enter this loop and **do not exit until every task in tasks.md is `[x]`**:

```
LOOP:
  1. Read .kiro/specs/<slug>/tasks.md
  2. Find the FIRST group that has any task still marked `[ ]`
  3. If NO such group exists → ALL DONE, exit loop
  4. Determine the agent for each `[ ]` task in that group:
       - "UI Design" group          → agent_name="ui-ux"
       - "Research" group           → agent_name="coder"
       - "Implementation" group     → agent_name="coder" or "ops" (per task)
       - "Review gate" group        → agent_name="reviewer", then agent_name="security-reviewer"
                                     IMPORTANT: pass only file PATHS to reviewer — do NOT paste full file contents.
                                     reviewer reads files itself. Short query = reliable execution.
       - "Documentation" group      → agent_name="docs" (query MUST say: "Write docs/architecture.md in arc42 format (all 12 sections) and docs/c4.md with C4 diagrams (Level 1, 2, 3). Read .kiro/skills/arc42/SKILL.md and .kiro/skills/c4/SKILL.md for templates. Also update README.md.")
  5. Dispatch ALL `[ ]` tasks in that group in parallel using subagent:
       subagent(agent_name="<agent>", query="<task text + file paths + how to mark complete>", relevant_context="<spec path + task definition — keep short, pass paths not file contents>")
  6. After subagent returns (even if it returned "No result" or empty output):
       Read tasks.md directly — the return value of subagent is unreliable.
       "No result" does NOT mean failure — check tasks.md, not the return value.
  7. If tasks.md shows all tasks in this group are `[x]` → group complete, go to step 1
  8. If any task is `[!]` → STOP. Report to the user:
       - Which task is blocked and the note on the `[!]` line
       - Do NOT retry automatically
  9. If tasks are STILL `[ ]` after subagent returned → the agent ran but did not complete.
       Retry the dispatch ONCE with a shorter, more direct query.
       If still `[ ]` after retry → mark `[!]` with "two attempts, no progress" and STOP
 10. Go back to step 1
```

**The loop replaces manual step-by-step thinking. You do not decide when to stop — the tasks.md file decides. Keep looping until every `[ ]` is `[x]`.**

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
