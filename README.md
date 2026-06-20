# Kiro Multi-Agent System

A production-ready multi-agent configuration for [Kiro CLI](https://kiro.dev) that automates the full software development lifecycle — from requirements gathering to deployed, documented code — using a team of specialized AI agents that collaborate autonomously.

## Overview

Instead of a single AI assistant that does everything, this system uses **eight specialized agents**, each with a focused role, a scoped toolset, and strict handoff protocols. A user describes what they want to build; the agents handle requirements, UI design, implementation, testing, review, and documentation — in order, without manual intervention between steps.

```
User
 │
 ▼
PM Agent  ──── clarifies requirements, writes PRD, waits for user approval
 │
 ▼
Architect ──── reads confirmed PRD, creates spec + tasks, orchestrates all agents below
 │
 ├──► UI/UX Agent          ── designs HTML mockups for every screen
 │
 ├──► Coder Agent          ── implements features, runs tests
 │
 ├──► Ops Agent            ── infrastructure, CI/CD, deployment
 │
 ├──► Reviewer Agent       ── code quality review
 │
 ├──► Security Reviewer    ── security audit
 │
 └──► Docs Agent           ── arc42 architecture doc + C4 diagrams + README
```

## Agents

### PM — Product Manager
**Entry point for every new request.**

Runs the AWS AI Development Lifecycle (AI-DLC) to gather requirements before any code is written:

1. **Asks focused discovery questions** — problem, users, features, screens, constraints
2. **Writes a full PRD** (`prd/requirements.md`) with epics, user stories, acceptance criteria, NFRs, risks, and success metrics
3. **Shows a requirements summary** and waits for user confirmation
4. **Dispatches the Architect** only after the user explicitly approves

Model: `claude-opus-4.7` | MCPs: context7, deepwiki

---

### Architect — Technical Lead & Orchestrator
**Never starts on its own — always triggered by PM with a confirmed PRD.**

1. Reads the confirmed PRD and converts it into `spec.md` (architecture decisions) and `tasks.md` (ordered task groups)
2. Dispatches the UI/UX agent for screen mockups
3. Enters a **continuous execution loop**: reads `tasks.md`, finds the first incomplete group, dispatches the right agent, verifies completion, repeats — until all tasks are `[x]`

Task groups are executed in order: UI Design → Research → Implementation → Review Gate → Documentation.

Model: `claude-opus-4.7` | MCPs: context7, deepwiki

---

### UI/UX — Interface Designer
Triggered by Architect after planning is complete.

- Optionally installs the [UI/UX Pro Max skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (67 UI styles, 161 palettes) via `npx uipro-cli init --ai kiro`
- Reads the spec and creates HTML mockups for every screen
- Output: `ui/screens/NN-name.html` per screen, `ui/transitions/flow.html` (animated transitions), `ui/index.html` (navigation hub), `ui/design-system.md`

Model: `claude-sonnet-4.6` | MCPs: context7

---

### Coder — Software Engineer
Implements features and conducts research.

- Writes production code from spec and task definitions
- Runs tests with enforced timeouts (`timeout 120 python -m pytest --timeout=60 --tb=short -q`)
- Marks tasks `[x]` on completion, `[!]` if blocked
- All test/build commands are timeout-enforced at the hook layer — hanging tests are blocked automatically

Model: `claude-sonnet-4.6`

---

### Ops — Infrastructure & DevOps Engineer
Handles infrastructure, deployment, and operations tasks.

- Terraform / CDK / CloudFormation
- Docker builds, CI/CD pipelines
- Cloud deployments (AWS-focused)
- Same timeout enforcement as Coder

Model: `claude-sonnet-4.6`

---

### Reviewer — Code Quality Reviewer
Triggered after all implementation groups complete.

- Reviews code against the spec and acceptance criteria
- Writes findings to `review.md`
- Returns `PASS` or `FAIL` with specific issues
- On `FAIL`: Architect appends a fix group to `tasks.md` and the loop re-runs
- Maximum 3 review cycles before escalating to the user

Model: `claude-sonnet-4.6`

---

### Security Reviewer — Security Auditor
Runs after the Reviewer passes.

- Checks for OWASP Top 10, secrets in code, IAM over-permission, insecure dependencies
- Writes findings to `security-review.md`
- Same pass/fail/fix loop as the Reviewer

Model: `claude-sonnet-4.6`

---

### Docs — Technical Writer
Final step, triggered after all implementation and reviews pass.

- Reads arc42 and C4 skills from `.kiro/skills/`
- Writes `docs/architecture.md` — full arc42 document (all 12 sections)
- Writes `docs/c4.md` — C4 diagrams at Level 1 (Context), Level 2 (Container), Level 3 (Component) using Mermaid
- Updates `README.md`

Model: `claude-sonnet-4.6`

---

## Workflows

### New Feature / New Project

```
User describes request
 └─► PM classifies → "New Feature" path
      └─► PM asks 5–8 discovery questions
           └─► User answers
                └─► PM writes PRD draft → shows summary
                     └─► User says YES
                          └─► PM dispatches Architect (Mode: NEW_FEATURE)
                               └─► Architect reads PRD → writes spec.md + tasks.md
                                    └─► UI/UX → screens
                                         └─► Coder/Ops → implementation groups
                                              └─► Reviewer → security-reviewer
                                                   └─► Docs (arc42 + C4)
                                                        └─► Done
```

### Bug Fix

```
User describes bug / error
 └─► PM classifies → "Bug Fix" path
      └─► PM asks 3 targeted questions (reproduce, expected vs actual, affected area)
           └─► User answers
                └─► PM writes bug-report.md → shows summary
                     └─► User says YES
                          └─► PM dispatches Architect (Mode: BUG_FIX)
                               └─► Architect writes minimal tasks.md (4 groups)
                                    └─► Coder: Diagnose → writes diagnosis.md
                                         └─► Coder: Fix → bug no longer reproduces
                                              └─► Coder: Test + regression test
                                                   └─► Reviewer validates
                                                        └─► Done
```

### Hotfix (Urgent / Production Down)

```
User signals urgency ("production down", "critical", "ASAP")
 └─► PM classifies → "Hotfix" path
      └─► No questions, no confirmation (emergency)
           └─► PM writes bug-report.md, dispatches Coder DIRECTLY
                └─► Coder: find root cause → apply minimal fix → run tests
                     └─► Done (add review manually if needed)
```

### Refactor

```
User describes refactor goal
 └─► PM classifies → "Refactor" path
      └─► PM asks 3 scope questions (target, goal, must-not-change boundary)
           └─► User answers
                └─► PM writes refactor-scope.md → shows summary
                     └─► User says YES
                          └─► PM dispatches Architect (Mode: REFACTOR)
                               └─► Architect writes minimal tasks.md (4 groups)
                                    └─► Coder: Analyse → writes refactor-plan.md
                                         └─► Coder: Refactor (within scope only)
                                              └─► Coder: Test (behavior unchanged)
                                                   └─► Reviewer validates
                                                        └─► Done
```

### Docs Update

```
User asks to update README / docs
 └─► PM classifies → "Docs" path
      └─► No questions needed
           └─► PM dispatches Docs agent directly
                └─► Done
```

### Session Resume

If Kiro CLI is restarted mid-workflow, the Architect reads `.kiro/specs/currentspec.md` at session start and resumes from the first incomplete task group. No work is repeated.

### Task States in tasks.md

| Marker | Meaning |
|--------|---------|
| `[ ]` | Not yet started |
| `[x]` | Completed |
| `[!]` | Blocked — needs manual review |

---

## Project Structure

```
.kiro/
├── agents/               # Agent configs (.json) and prompts (.md)
│   ├── pm.json / pm.md
│   ├── architect.json / architect.md
│   ├── ui-ux.json / ui-ux.md
│   ├── coder.json / coder.md
│   ├── ops.json / ops.md
│   ├── reviewer.json / reviewer.md
│   ├── security-reviewer.json / security-reviewer.md
│   └── docs.json / docs.md
│
├── skills/               # Reusable knowledge loaded by agents
│   ├── arc42/            # arc42 architecture documentation template
│   ├── c4/               # C4 model diagram templates (Mermaid)
│   ├── agentcore-patterns/
│   ├── aws-cli/
│   ├── cloudwatch-dashboards/
│   ├── docker-build/
│   ├── documentation/
│   ├── git-workflow/
│   └── shell-scripting/
│
├── steering/             # Global rules loaded into every agent
│   ├── spec-workflow.md  # Spec-driven workflow (inclusion: always)
│   ├── non-interactive.md # Timeout and non-blocking rules
│   └── ...
│
├── hooks/                # Python scripts that intercept tool calls
│   ├── enforce-timeouts.py      # Blocks test commands without timeouts
│   ├── check-secrets.py         # Blocks writes containing secrets
│   ├── config-drift-guard.py    # Guards steering/agent config changes
│   ├── validate-environment.py  # Checks required tools on agent spawn
│   ├── guard-destructive-commands.py
│   ├── flywheel-log.py          # Logs turn summaries for analysis
│   └── ...
│
├── specs/                # Created at runtime per project
│   ├── currentspec.md    # Active spec slug (single line)
│   │
│   ├── YYYY-MM-DD-<slug>/           # New feature
│   │   ├── prd/requirements.md      # PM-written, user-confirmed PRD
│   │   ├── spec.md                  # Architect's technical spec
│   │   ├── tasks.md                 # Task tracker ([ ] [x] [!])
│   │   ├── ui/                      # UI/UX agent output
│   │   ├── docs/                    # arc42 + C4 documentation
│   │   ├── review.md                # Reviewer findings
│   │   └── security-review.md       # Security reviewer findings
│   │
│   ├── YYYY-MM-DD-bug-<slug>/       # Bug fix
│   │   ├── bug-report.md            # PM-written bug report
│   │   ├── diagnosis.md             # Coder's root cause analysis
│   │   ├── tasks.md                 # 4-group minimal task tracker
│   │   └── review.md
│   │
│   └── YYYY-MM-DD-refactor-<slug>/  # Refactor
│       ├── refactor-scope.md        # PM-written scope doc
│       ├── refactor-plan.md         # Coder's analysis and plan
│       ├── tasks.md                 # 4-group minimal task tracker
│       └── review.md
│
└── settings/
    └── cli.json          # Entry point: defaultAgent=pm, enableSubagent=true
```

---

## Getting Started

### Prerequisites

- [Kiro CLI](https://kiro.dev) installed
- Node.js (for UI/UX Pro Max skill installation)
- Python 3 (for hooks)

### Setup

1. Copy this `.kiro/` folder into your project root
2. Open Kiro CLI in your project directory
3. The `pm` agent starts automatically as the default agent

### Starting a New Project

Just describe what you want to build:

```
> I want to build a task management app with user authentication, 
  project boards, and real-time updates
```

The PM agent will ask you a few questions, show you a requirements summary, and wait for your approval before any code is written.

### Resuming an Interrupted Session

If you close and reopen Kiro CLI, the Architect detects the active spec and resumes automatically from where it stopped. No manual restart needed.

---

## Key Design Decisions

**Requirements before code.** The PM agent always runs first. No agent writes spec.md or tasks.md until the user has confirmed requirements. This prevents agents from building the wrong thing.

**Loop-driven execution.** The Architect does not follow a numbered list — it reads `tasks.md` on every iteration and dispatches whatever is incomplete. This makes the workflow resilient to failures, restarts, and partial completions.

**Timeout enforcement at the hook layer.** Prompts telling agents "use timeouts" are ignored under pressure. The `enforce-timeouts.py` hook blocks test and build commands at the tool level if they lack a timeout wrapper — the agent receives the safe command back and must use it.

**"No result" is not failure.** Kiro CLI subagents sometimes return empty output even when work succeeded. All agents mark tasks `[x]` in `tasks.md` on completion; the Architect reads `tasks.md` directly rather than trusting the subagent return value.

**File paths, not file contents, to reviewers.** Passing full file contents in `relevant_context` to reviewer agents causes silent context overflow failures. Reviewers receive paths only and read files themselves.

---

## AWS AI Development Lifecycle (AI-DLC)

The PM agent structures requirements using the six-phase AWS AI-DLC framework:

| Phase | Output |
|-------|--------|
| 1. Business Problem Definition | Problem statement, out of scope |
| 2. User & Stakeholder Analysis | Personas with goals and pain points |
| 3. Requirements Definition | Functional + non-functional requirements |
| 4. User Story Mapping | Epics → Features → User Stories → Acceptance Criteria |
| 5. Risk & Assumption Register | Technical and business risks, documented assumptions |
| 6. Success Metrics & Definition of Done | Measurable targets, release criteria |

The resulting PRD drives everything downstream — spec.md, tasks.md, UI screens, test coverage, and documentation.

---

## Architecture Documentation

Every completed project generates two architecture documents automatically via the Docs agent:

- **arc42** (`docs/architecture.md`) — 12-section architecture documentation covering goals, constraints, context, building blocks, runtime behavior, deployment, concepts, design decisions, quality requirements, risks, and glossary
- **C4 Model** (`docs/c4.md`) — Context, Container, and Component diagrams as Mermaid charts

Both are generated from the project's spec, code, and decisions — not from templates filled by hand.
