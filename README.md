# Kiro Multi-Agent System

A production-ready multi-agent configuration for [Kiro CLI](https://kiro.dev) that automates the full software development lifecycle — from business problem discovery to deployed, reviewed, and documented code — using a team of specialized AI agents that collaborate autonomously under human oversight.

---

## What This Is

Most AI coding assistants answer one question at a time. This system operates differently: it runs a structured **product → architecture → implementation → review → documentation** pipeline, where each stage is handled by a dedicated agent with a narrow scope and clear handoff protocol.

You describe what you want. The PM agent asks the right questions, proposes solution options, and gets your explicit sign-off before a single line of code is written. Once confirmed, the architect plans the work and orchestrates all remaining agents autonomously — no further input needed until the feature is complete, reviewed, and documented.

---

## Agent Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
              ┌─────────────────────────────────┐
              │          PM AGENT               │
              │                                 │
              │  Turn 1: Discovery questions    │◄── User answers
              │  Turn 2: 2 solution options     │◄── User chooses
              │  Turn 3: PRD + summary          │◄── User confirms
              │  Turn 4: Dispatch               │
              └─────────────────┬───────────────┘
                                │ confirmed PRD
                                ▼
              ┌─────────────────────────────────┐
              │        ARCHITECT AGENT          │
              │                                 │
              │  Reads PRD → writes spec.md     │
              │  Writes tasks.md (groups)       │
              │  Runs execution loop            │
              └──┬──────────────────────────────┘
                 │
       ┌─────────┼─────────────────────────────────┐
       │         │                                 │
       ▼         ▼                                 ▼
  ┌─────────┐ ┌─────────┐                   ┌───────────┐
  │  UI/UX  │ │  CODER  │ ··· (per group)   │    OPS    │
  │ mockups │ │  impl.  │                   │  infra    │
  └─────────┘ └─────────┘                   └───────────┘
                 │ all groups complete
                 ▼
       ┌──────────────────┐     ┌──────────────────┐
       │    REVIEWER      │────►│ SECURITY REVIEWER │
       │  code quality    │     │  OWASP / secrets  │
       └──────────────────┘     └──────────────────┘
                                        │ PASS
                                        ▼
                              ┌──────────────────┐
                              │   DOCS AGENT     │
                              │ arc42 + C4 + README│
                              └──────────────────┘
```

---

## Agents

### PM — Product Manager

**Entry point for every request. The only agent that talks to the user.**

The PM follows a structured four-turn conversation before any code is written:

| Turn | PM Action | User Action |
|------|-----------|-------------|
| 1 | Asks 8-category discovery questions covering business context, users, features, flows, NFRs, integrations, UI, and launch criteria | Answers what they know |
| 2 | Proposes **2 solution options** with trade-off comparison (time, cost, scalability, maintenance) and a recommendation | Chooses Option A, B, or a hybrid |
| 3 | Writes a full PRD based on the chosen approach and shows a requirements summary | Confirms or requests changes |
| 4 | Dispatches the architect with the confirmed PRD | — |

**Discovery questions are business-first**, not technical. Instead of "list all NFRs", the PM asks things like:
- *"What's the cost of NOT having this? Time lost, mistakes made, revenue not captured?"*
- *"How do people cope today — spreadsheet, manual process, another tool, or nothing at all?"*
- *"How fast does it need to feel? Is a 2-second load acceptable, or does it need to be instant?"*

**Solution options contrast on dimensions that matter** — build vs buy, API-first vs UI-first, fully automated vs tool-assisted — each with an honest trade-off statement so the user can make an informed decision.

Supports five request types:

| Type | Trigger signals | Flow |
|------|----------------|------|
| **New Feature** | New capability, new product, new screen | Full 4-turn flow with PRD |
| **Bug Fix** | "bug", "broken", "error", "crash", stack trace | 5-question diagnostic → bug report |
| **Refactor** | "refactor", "clean up", "restructure", "technical debt" | 5-question scope flow → scope doc |
| **Hotfix** | "urgent", "production down", "critical", "ASAP" | Immediate dispatch to Coder — no questions |
| **Docs Update** | "update docs", "fix README", "update CHANGELOG" | Immediate dispatch to Docs agent |

Model: `claude-opus-4.7` | MCPs: context7, deepwiki

---

### Architect — Technical Lead & Orchestrator

**Never starts on its own — always triggered by PM with a confirmed PRD.**

1. Reads the PRD and writes `spec.md` (architecture decisions, constraints, risks)
2. Writes `tasks.md` with ordered, parallelizable task groups — each group has an assigned agent, acceptance criteria, and a verification command
3. Dispatches UI/UX for screen mockups (if the spec has screens)
4. Enters the **execution loop**: reads `tasks.md` → finds first incomplete group → dispatches the right agent → verifies completion → repeats until all tasks are `[x]`
5. On session resume, reads `currentspec.md` and continues from the first incomplete group — no work repeated

Task group order: UI Design → Research → Implementation → Review Gate → Security Review Gate → Documentation

Mode-aware: handles `NEW_FEATURE`, `BUG_FIX`, and `REFACTOR` with appropriately scoped task structures.

Model: `claude-opus-4.7` | MCPs: context7, deepwiki

---

### UI/UX — Interface Designer

Triggered by Architect immediately after planning, before any implementation.

- Optionally installs the [UI/UX Pro Max skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (67 UI styles, 161 palettes) via `npx uipro-cli init --ai kiro`
- Produces HTML mockups for every screen defined in the spec
- Output: `ui/screens/NN-name.html` per screen, `ui/transitions/flow.html` (animated flow), `ui/index.html` (navigation hub), `ui/design-system.md`

Model: `claude-sonnet-4.6` | MCPs: context7

---

### Coder — Software Engineer

Implements features, conducts SDK research, and writes tests.

- Works from spec + task definitions — never invents requirements
- Runs tests with enforced timeouts (`timeout 120 python -m pytest --timeout=60 --tb=short -q`)
- Marks tasks `[x]` in `tasks.md` on completion, `[!]` if blocked
- All commands are timeout-enforced at the hook layer — hanging commands are blocked automatically

Model: `claude-sonnet-4.6`

---

### Ops — Infrastructure & DevOps Engineer

Handles infrastructure, deployment pipelines, and cloud configuration.

- Terraform, CDK, CloudFormation, Docker, CI/CD
- AWS-focused but framework-agnostic
- Same timeout enforcement as Coder
- Deploys are out-of-band by default — only included in the spec when the spec itself requires provisioning new infrastructure

Model: `claude-sonnet-4.6`

---

### Reviewer — Code Quality Reviewer

Triggered after all implementation groups complete. Sequential gate — nothing proceeds until this passes.

- Reviews implementation against spec and acceptance criteria
- Writes structured findings to `review.md` with Critical / Warning / Suggestion severity levels
- Returns `PASS` or `FAIL` with specific file and line references
- On `FAIL`: Architect appends a fix group to `tasks.md` and the loop continues
- Maximum 3 review cycles; escalates to user if unresolved

Model: `claude-sonnet-4.6`

---

### Security Reviewer — Security Auditor

Runs after the Reviewer issues `PASS`. Sequential gate.

- Checks for OWASP Top 10, hardcoded secrets, IAM over-permission, insecure dependencies
- Writes findings to `security-review.md`
- Same pass/fail/fix loop as the Reviewer

Model: `claude-sonnet-4.6`

---

### Docs — Technical Writer

Final step, triggered after all reviews pass.

- Reads arc42 and C4 skills from `.kiro/skills/`
- Writes `docs/architecture.md` — full arc42 document (all 12 sections, populated from spec and code)
- Writes `docs/c4.md` — C4 diagrams at Level 1 (Context), Level 2 (Container), Level 3 (Component) using Mermaid syntax
- Updates `README.md` to reflect user-facing changes from this spec

Model: `claude-sonnet-4.6`

---

## Workflows

### New Feature

```
User: "I want to build an internal expense approval system"
 │
 └─► PM: 8-category discovery questions (business problem, users, features,
 │        flows, NFRs, integrations, UI, launch criteria)
      │
      └─► User: answers
           │
           └─► PM: Option A — "Lightweight form + email approval"
           │        Option B — "Full workflow platform with audit trail"
                │
                └─► User: "Option B, but start with 2 approval levels only"
                     │
                     └─► PM: Writes PRD, shows requirements summary
                          │
                          └─► User: YES
                               │
                               └─► Architect: spec.md + tasks.md
                                    ├─► UI/UX: screen mockups
                                    ├─► Coder: implementation groups (sequential)
                                    ├─► Reviewer: PASS/FAIL gate
                                    ├─► Security Reviewer: PASS/FAIL gate
                                    └─► Docs: arc42 + C4 + README update
```

### Bug Fix

```
User: "Login fails with 500 error when SSO token expires"
 │
 └─► PM: 5 diagnostic questions
 │        (reproduce steps, expected vs actual, affected area, severity, environment)
      │
      └─► User: answers + stack trace
           │
           └─► PM: Bug report written, shows summary
                │
                └─► User: YES
                     │
                     └─► Architect (BUG_FIX mode): 4-group tasks.md
                          ├─► Coder: Diagnose → writes diagnosis.md
                          ├─► Coder: Fix
                          ├─► Coder: Test + regression test added
                          └─► Reviewer: validates fix
```

### Hotfix (Production Emergency)

```
User: "CRITICAL: checkout is down, customers can't pay"
 │
 └─► PM: Immediate dispatch — no questions, no PRD, no confirmation
      │
      └─► Coder: root cause → minimal fix → tests → done
```

### Refactor

```
User: "The auth module is 3,000 lines, need to split it"
 │
 └─► PM: 5 scope questions
 │        (target files, goal, must-not-change, risk level, verification tests)
      │
      └─► User: answers
           │
           └─► PM: Option A vs Option B refactor approach
                │
                └─► User: confirms approach
                     │
                     └─► Architect (REFACTOR mode):
                          ├─► Coder: Analyse → writes refactor-plan.md
                          ├─► Coder: Refactor (within scope only)
                          ├─► Coder: Test (behavior unchanged)
                          └─► Reviewer: validates no behavior change
```

### Docs Update

```
User: "Update the README to document the new API endpoints"
 │
 └─► PM: Immediate dispatch — no questions needed
      │
      └─► Docs agent: applies the changes → done
```

### Session Resume

The Architect reads `.kiro/specs/currentspec.md` at the start of every session. If a spec is in progress, it resumes from the first incomplete task group automatically — no user input required, no work repeated.

### Task States

| Marker | Meaning |
|--------|---------|
| `[ ]` | Not yet started |
| `[x]` | Completed and verified |
| `[!]` | Blocked — needs manual review |

---

## Project Structure

```
.kiro/
├── agents/                          # Agent definitions
│   ├── pm.json / pm.md              # PM: 4-turn conversation-driven workflow
│   ├── architect.json / architect.md
│   ├── ui-ux.json / ui-ux.md
│   ├── coder.json / coder.md
│   ├── ops.json / ops.md
│   ├── reviewer.json / reviewer.md
│   ├── security-reviewer.json / security-reviewer.md
│   └── docs.json / docs.md
│
├── skills/                          # Reusable knowledge packs
│   ├── arc42/                       # arc42 architecture documentation template
│   ├── c4/                          # C4 model diagram templates (Mermaid)
│   ├── agentcore-patterns/
│   ├── aws-cli/
│   ├── cloudwatch-dashboards/
│   ├── docker-build/
│   ├── documentation/
│   ├── git-workflow/
│   └── shell-scripting/
│
├── steering/                        # Rules loaded into every agent (inclusion: always)
│   │                                # Each file carries a PM AGENT EXCEPTION header —
│   │                                # the PM ignores all steering and follows pm.md only
│   ├── spec-workflow.md             # Spec-driven execution loop
│   ├── non-interactive.md           # Shell command rules (not PM conversations)
│   ├── testing.md                   # Test-first requirements
│   ├── documentation.md             # Documentation standards
│   ├── issue-tracking.md            # Bug and incident tracking
│   ├── sdk-verification.md          # API verification before implementation
│   ├── doc-research.md              # Documentation research protocol
│   ├── dependency-versions.md       # Pinned dependency rules
│   ├── deploy-validation.md         # Post-deploy validation
│   └── virtual-environments.md      # Dependency isolation
│
├── hooks/                           # Python scripts that intercept tool calls
│   ├── enforce-timeouts.py          # Blocks shell commands without timeout wrappers
│   ├── check-secrets.py             # Blocks file writes containing secrets or API keys
│   ├── config-drift-guard.py        # Guards .kiro/steering and .kiro/agents from edits
│   ├── validate-environment.py      # Checks required tools on agent spawn
│   ├── guard-destructive-commands.py
│   └── flywheel-log.py              # Logs turn summaries for review and improvement
│
├── specs/                           # Created at runtime per project
│   ├── currentspec.md               # Active spec slug — source of truth for resume
│   │
│   ├── YYYY-MM-DD-<slug>/           # New feature
│   │   ├── prd/
│   │   │   └── requirements.md      # PM-written, user-confirmed PRD
│   │   ├── spec.md                  # Architect's technical decisions
│   │   ├── tasks.md                 # Task groups with [ ] [x] [!] markers
│   │   ├── ui/                      # UI/UX agent output
│   │   ├── docs/                    # arc42 + C4 documentation
│   │   ├── review.md                # Reviewer findings per cycle
│   │   └── security-review.md       # Security reviewer findings per cycle
│   │
│   ├── YYYY-MM-DD-bug-<slug>/       # Bug fix
│   │   ├── bug-report.md
│   │   ├── diagnosis.md
│   │   ├── tasks.md
│   │   └── review.md
│   │
│   └── YYYY-MM-DD-refactor-<slug>/  # Refactor
│       ├── refactor-scope.md
│       ├── refactor-plan.md
│       ├── tasks.md
│       └── review.md
│
└── settings/
    └── cli.json                     # defaultAgent: pm, enableSubagent: true
```

---

## Getting Started

### Prerequisites

- [Kiro CLI](https://kiro.dev) installed
- Python 3.9+ (for hooks)
- Node.js 18+ (for UI/UX Pro Max skill — optional)

### Setup

```bash
# Copy the .kiro folder into your project root
cp -r /path/to/this-repo/.kiro /path/to/your-project/

# Open Kiro CLI in your project directory
cd /path/to/your-project
kiro
```

The `pm` agent is the default agent and starts automatically.

### Your First Request

Describe what you want in plain language — no technical spec required:

```
> I want to build an internal expense approval system.
  Finance team submits expenses, managers approve, accounting exports to ERP.
```

The PM will guide you through 4 turns:
1. Ask 8 categories of questions to understand the business problem fully
2. Propose two solution approaches with trade-offs for you to choose from
3. Write a complete PRD and show you a summary for confirmation
4. Hand off to the architect only after you say YES

No code is written until you confirm the requirements.

### Resuming After a Restart

Close and reopen Kiro CLI at any point. The Architect reads `.kiro/specs/currentspec.md` and continues from the first incomplete task group automatically. No manual steps required.

---

## Design Principles

### Requirements gate every spec

The PM runs first, always. No agent creates `spec.md` or `tasks.md` until the user has confirmed the PRD. This prevents the most common failure mode in AI-assisted development: building the wrong thing confidently and completely.

### Solution options before commitment

After gathering requirements, the PM proposes two meaningfully different approaches — not just "simple vs complex", but trade-offs that reflect the user's real constraints (team size, timeline, budget, expected scale). The user chooses the direction before any architecture work begins.

### Conversation-history turn detection

The PM determines which turn it is on by reading its own previous messages in the conversation — not from state files or disk checks. This is reliable across session restarts and immune to stale file state. Each turn is anchored to a unique sentinel phrase:

| Sentinel phrase in PM's previous message | Next turn |
|------------------------------------------|-----------|
| `"Please answer as many as you can"` | Turn 2: propose 2 solutions |
| `"Which approach fits best?"` | Turn 3: write PRD |
| `"Does this look right?"` | Turn 4: dispatch or update |

### Steering files are scoped away from PM

All 10 steering files carry an explicit `PM AGENT EXCEPTION` header. The PM ignores all of them and follows only `pm.md`. This prevents rules like `"execute autonomously without waiting for the user"` and `"no interactive prompts"` from suppressing the PM's question-asking behaviour — the most common cause of the PM skipping clarification.

### Loop-driven execution

The Architect does not follow a static numbered list. It reads `tasks.md` on every iteration and dispatches whatever is incomplete. This makes the workflow resilient to agent failures, partial completions, and session restarts — the loop always picks up from the right place without repeating completed work.

### Hooks enforce what prompts cannot

Prompts telling agents "always use timeouts" are overridden under pressure. The `enforce-timeouts.py` hook blocks test and build commands at the tool-call level if they lack a timeout wrapper. The agent receives the blocked message and must add the wrapper — no exceptions, no workarounds.

### Tasks as the source of truth

Kiro CLI subagents sometimes return empty output even when work succeeded. Agents write `[x]` to `tasks.md` on completion; the Architect reads `tasks.md` directly rather than trusting subagent return values. Tasks are the ground truth.

### File paths to reviewers, not file contents

Passing full file contents in `relevant_context` to reviewer agents causes silent context overflow. Reviewers receive file paths only and read the files themselves, keeping context small and results reliable.

---

## PM Discovery Questions

The PM asks across eight categories, phrased for business stakeholders — not developers:

| # | Category | What it uncovers |
|---|----------|-----------------|
| 1 | **Business Problem** | Pain, cost of inaction, success definition, v1 boundaries |
| 2 | **Users & Personas** | Who uses it, how many, what they do today without it |
| 3 | **Functional Core** | Actions users take, permissions, data model, business rules |
| 4 | **Flows & Edge Cases** | Main journey, secondary paths, error states, empty states |
| 5 | **Quality & Reliability** | Performance targets, uptime SLA, auth method, compliance |
| 6 | **Integrations** | Existing systems, third-party APIs, stack, hard constraints |
| 7 | **UI & Screens** | Screen list, platform, design system, UX patterns |
| 8 | **Launch & Sign-off** | Acceptance criteria, test data, approver, rollout plan |

Sample questions in business language:
- *"What's the cost of NOT having this? Time lost, mistakes made, revenue not captured?"*
- *"How do people cope today — spreadsheet, manual process, another tool, or nothing?"*
- *"How fast does it need to feel? Is a 2-second load acceptable, or does it need to be instant?"*
- *"Who signs off before this ships?"*

---

## AWS AI Development Lifecycle (AI-DLC)

The PM structures requirements using the six-phase AWS AI-DLC framework:

| Phase | What the PM produces |
|-------|---------------------|
| 1. Business Problem Definition | Problem statement, business impact, explicit out-of-scope boundaries |
| 2. User & Stakeholder Analysis | Persona table with goals, pain points, volume, and current workarounds |
| 3. Requirements Definition | User actions, roles and permissions, business rules, data model |
| 4. User Story Mapping | Epics → User Stories with measurable acceptance criteria, MoSCoW prioritisation |
| 5. Risk & Assumption Register | Assumptions flagged `[ASSUMED: reason]`, technical and business risks |
| 6. Success Metrics & Definition of Done | Measurable targets, NFR verification criteria, sign-off checklist |

The resulting PRD (`prd/requirements.md`) drives everything downstream: `spec.md`, `tasks.md`, UI mockups, test coverage, and architecture documentation.

---

## Architecture Documentation

Every completed project generates two architecture documents automatically via the Docs agent:

**arc42** (`docs/architecture.md`) — all 12 sections populated from spec and code:
- System goals, quality requirements, constraints
- Context and scope (Level 1 C4)
- Building block view, runtime scenarios, deployment view
- Cross-cutting concepts, architecture decisions, risk register, glossary

**C4 Model** (`docs/c4.md`) — three levels of Mermaid diagrams:
- Level 1: System Context — who uses it and what it integrates with
- Level 2: Container — services, databases, frontends
- Level 3: Component — internal structure of each container

Both documents use real names from the implementation code. No placeholders, no generic labels.
