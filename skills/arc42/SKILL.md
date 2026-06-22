---
name: arc42
description: arc42 architecture documentation template. Use when creating or updating architecture documentation for any software system. Produces a complete arc42 document covering all 12 sections: goals, constraints, context, strategy, building blocks, runtime, deployment, concepts, decisions, quality, risks, and glossary.
---

# arc42 Architecture Documentation Skill

arc42 is the standard template for software architecture documentation. When writing architecture docs, always produce a complete arc42 document at `docs/architecture.md` (or update it if it exists).

## How to Fill Each Section

Read the spec (`spec.md`), the implementation files, and any ADRs or decisions logs before writing. Every section must be populated from what was actually built — do not leave sections empty or copy placeholder text.

---

## Full arc42 Template

```markdown
# Architecture Documentation: <System Name>

> arc42 — Version <N> — <YYYY-MM-DD>

---

## 1. Introduction and Goals

### 1.1 Requirements Overview
<!-- What does the system do? Who uses it? What problem does it solve? -->
<!-- Source: spec.md Context and Decision sections -->

| Goal | Description |
|------|-------------|
| G1   | |
| G2   | |

### 1.2 Quality Goals
<!-- Top 3–5 quality attributes that drive architectural decisions. -->
<!-- Examples: performance, security, scalability, maintainability, reliability -->

| Priority | Quality Goal | Scenario |
|----------|-------------|----------|
| 1 | | |
| 2 | | |
| 3 | | |

### 1.3 Stakeholders

| Role | Expectations |
|------|-------------|
| End User | |
| Developer | |
| Operator | |

---

## 2. Architecture Constraints

### 2.1 Technical Constraints

| Constraint | Background / Motivation |
|-----------|------------------------|
| | |

### 2.2 Organisational Constraints

| Constraint | Background / Motivation |
|-----------|------------------------|
| | |

### 2.3 Conventions

| Convention | Background / Motivation |
|-----------|------------------------|
| | |

---

## 3. System Scope and Context

### 3.1 Business Context
<!-- Show external actors (users, systems, services) that communicate with the system. -->
<!-- Use a simple text diagram or ASCII art if no diagramming tool is available. -->

```
[Actor / External System] --> [This System] --> [Actor / External System]
```

| Communication Partner | Input | Output |
|----------------------|-------|--------|
| | | |

### 3.2 Technical Context
<!-- Show technical interfaces: protocols, message formats, transport mechanisms. -->

| Interface | Technology / Protocol | Direction |
|----------|----------------------|-----------|
| | | |

---

## 4. Solution Strategy

<!-- 2–5 bullet points explaining the core architectural decisions and why they were made. -->
<!-- Reference ADRs where they exist. -->

| Decision | Rationale |
|----------|-----------|
| Technology choice | |
| Top-level decomposition | |
| Key architectural patterns used | |
| Approach to quality goals | |

---

## 5. Building Block View

### 5.1 Level 1 — White-box Overall System

<!-- Show the major components/modules and their responsibilities. -->

```
┌─────────────────────────────────────────────────────┐
│                    <System Name>                    │
│                                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────┐  │
│  │ Component A │   │ Component B │   │ Component│  │
│  └─────────────┘   └─────────────┘   └──────────┘  │
└─────────────────────────────────────────────────────┘
```

| Component | Responsibility | Key Files |
|-----------|---------------|-----------|
| | | |

### 5.2 Level 2 — Black-box Descriptions
<!-- For each major component, describe its interface and behaviour. -->

#### Component A
- **Purpose**: 
- **Interface**: 
- **Key dependencies**: 

#### Component B
- **Purpose**: 
- **Interface**: 
- **Key dependencies**: 

---

## 6. Runtime View

<!-- Describe the most important runtime scenarios. -->
<!-- For each scenario: what triggers it, which components are involved, what data flows. -->

### Scenario 1: <Name of Key User Flow>

```
User → [Component A] → [Component B] → [Data Store]
                              ↓
                       [External Service]
```

1. User triggers …
2. Component A does …
3. Component B does …
4. Response returned …

### Scenario 2: <Name of Error / Edge Case>

<!-- Describe at least one error scenario -->

---

## 7. Deployment View

### 7.1 Infrastructure

<!-- Describe the target environment: cloud, on-prem, containerised, serverless, etc. -->

```
Cloud / Region
├── Network (VPC / Subnet)
│   ├── Compute (Lambda / ECS / EC2)
│   ├── Data Store (RDS / DynamoDB / S3)
│   └── Cache (ElastiCache / Redis)
└── CDN / Load Balancer
```

### 7.2 Deployment Mapping

| Component | Deployment Unit | Technology | Scaling |
|-----------|----------------|------------|---------|
| | | | |

### 7.3 CI/CD Pipeline

| Stage | Tool | Trigger |
|-------|------|---------|
| Build | | |
| Test | | |
| Deploy | | |

---

## 8. Cross-cutting Concepts

### 8.1 Security

| Concept | Implementation |
|---------|---------------|
| Authentication | |
| Authorisation | |
| Secrets management | |
| Data encryption (at rest) | |
| Data encryption (in transit) | |

### 8.2 Observability

| Concept | Implementation |
|---------|---------------|
| Logging | |
| Metrics | |
| Tracing | |
| Alerting | |

### 8.3 Error Handling

<!-- Describe the system-wide error handling strategy. -->

### 8.4 Testability

| Test Type | Tool / Approach | Coverage Target |
|-----------|----------------|----------------|
| Unit | | |
| Integration | | |
| End-to-end | | |

---

## 9. Architecture Decisions

<!-- List significant decisions here. Create separate ADR files in docs/decisions/ for detail. -->

| ID | Decision | Status | Date |
|----|----------|--------|------|
| ADR-001 | | Accepted | |
| ADR-002 | | Accepted | |

<!-- Link to full ADRs: [ADR-001](decisions/ADR-001.md) -->

---

## 10. Quality Requirements

### 10.1 Quality Tree

| Quality Attribute | Scenario | Priority |
|------------------|----------|----------|
| Performance | Response time < 200ms at p99 under 100 rps | High |
| Availability | 99.9% uptime, max 8.7 hours downtime/year | High |
| Security | All data encrypted in transit and at rest | High |
| Maintainability | New developer productive within 1 day | Medium |

### 10.2 Quality Scenarios

#### Scenario QS-1: <Performance>
- **Stimulus**: 100 concurrent requests
- **Response**: System handles all within 200ms p99
- **Measure**: Latency percentiles from load test

#### Scenario QS-2: <Availability>
- **Stimulus**: Single AZ failure
- **Response**: Traffic routed to healthy AZ within 30 seconds
- **Measure**: Failover time measured by health check

---

## 11. Risks and Technical Debts

### 11.1 Known Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| | | | |

### 11.2 Technical Debts

| Debt | Description | Priority | Planned Resolution |
|------|-------------|----------|--------------------|
| | | | |

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| | |
| | |

---

*Generated using arc42 template — https://arc42.org*
```

---

## Instructions for the docs agent

When your task includes writing architecture documentation:

1. **Output file**: `docs/architecture.md` (create `docs/` if it does not exist)
2. **If `docs/architecture.md` already exists**: update only the sections affected by the current spec — do not overwrite unrelated sections
3. **Source material to read before writing**:
   - `.kiro/specs/<slug>/spec.md` — for sections 1, 2, 3, 4
   - `.kiro/specs/<slug>/decisions.md` — for section 9
   - Actual implementation files — for sections 5, 6, 7, 8
   - `tasks.md` — for section 10 (quality criteria in Verify fields)
4. **Diagrams**: use ASCII/Unicode box-drawing characters — no external tools required
5. **Every section must be filled**: if a section genuinely has nothing (e.g. no external actors), write "N/A — <reason>" not just leave it blank
6. **ADR files**: for each significant decision in section 9, also write `docs/decisions/ADR-NNN.md` using the ADR template from the documentation skill
