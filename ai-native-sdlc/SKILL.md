---
name: ai-native-sdlc
description: Use for requirement-based software delivery with intent.md, spec.md, and plan.md in per-requirement directories under docs/. Revise those documents until the plan is completed; record subsequent user-requested bug fixes and feature adjustments in the current requirement's change.md.
---

# AI-Native SDLC

Treat software delivery as a loop, not a one-way handoff:

Plan → Design → Build → Test → Deploy → Maintain → Plan

The operating rule is **artifact, evidence, approval**. Each phase leaves a versioned artifact or record, each claim is backed by observable evidence, and a human makes decisions at authority boundaries. A small change may use terse artifacts; it must still preserve the required decisions and gates.

Conceptual source: Anthropic's *The AI Native SDLC Playbook*. Apply the process using the current runtime's project instructions, skills, checks, agents, CI/CD, and access controls rather than assuming any platform-specific tool.

## Precedence and starting point

- Read the repository's governing instructions first. More-specific project rules, user scope, and safety requirements override this general process.
- Begin at the phase matching the request. Recover upstream artifacts needed for implementation, but do not read historical requirements merely to decide whether a change needs recording.
- Store each requirement's artifacts together under docs/<requirement>/. Follow the document lifecycle below; for follow-up work, read [Change recording](references/feedback-loop.md).
- Existing user authorization counts within its scope; ask again only for missing decisions or expanded authority.
- Never invent approval, test evidence, review findings, or release authority.

## Requirement directories and document lifecycle

```text
docs/
  001-requirement-one/
    intent.md
    spec.md
    plan.md
    change.md       # Created only for qualifying changes after plan completion
  002-requirement-two/
    intent.md
    spec.md
    plan.md
```

Use the project's requirement naming convention; otherwise use increasing numeric prefixes and meaningful names. The latest requirement directory is the current one. Resolve it from the current conversation or explicit project designation, then directory sequence if unambiguous; do not infer it from file modification times. If competing directories leave ownership unclear, ask which is current instead of scanning their full specifications. Do not create a separate repair directory or a standalone current-feature-spec layer.

| Document | Purpose and recording rule |
| --- | --- |
| intent.md | Problem, scope, constraints, success criteria, and open questions. Revise affected sections while the plan is not completed. |
| spec.md | Accepted behavior, rules, interfaces, and boundary cases. Revise affected sections while the plan is not completed. |
| plan.md | Implementation steps, progress, verification, and explicit status. Revise during execution; mark completed only after the full plan and its required checks/review are finished. |
| change.md | Subsequent user-requested bug fixes or feature adjustments requiring code/configuration changes. Created on the first qualifying request after plan.md is explicitly completed; append one entry per distinct change and update its outcome. |

**The boundary is full plan completion, not plan approval, a working demo, or completion of one step.** Use a visible status near the top of plan.md: `Status: draft`, `Status: in_progress`, or `Status: completed` (an unambiguous existing equivalent is acceptable). Missing or unclear status does not imply completion; establish the real state without inventing evidence.

Before completion, incorporate requests into the affected intent/spec/plan sections; do not create change.md, even if the user says “fix” or “change.” After completion, retain the three documents as the delivery baseline and record follow-up intent, behavior differences, implementation steps, and verification in change.md. Do not reopen the completed plan merely to log a follow-up. Accepted changes in change.md amend the baseline; proposals and failed attempts do not redefine it.

When a new requirement starts, create its own directory and freeze the previous directory, including change.md. Subsequent fixes belong to the latest directory, even when they affect an older feature; reference that older requirement without editing its frozen files. The latest directory's own plan status still determines whether the fix goes into its intent/spec/plan or change.md. A distinct new requirement follows the full three-document flow rather than being hidden in change.md.

## Phase gates

The phase instructions below describe initial delivery. For post-completion follow-ups, keep the same applicable decisions, authority, and verification requirements, but put the follow-up's intent, design delta, and implementation plan in change.md rather than rewriting the completed three-document baseline.

| Phase | Required artifact or evidence | Gate before proceeding |
| --- | --- | --- |
| Plan | intent.md | Requester confirms the problem, scope, and success criteria. |
| Design | spec.md | Design covers flows, interfaces, rules, and failure cases. |
| Build | plan.md, code, tests | The implementation plan is accepted before code changes. |
| Test | Actual command output and an independent review record | Relevant checks pass and review findings are resolved. |
| Deploy | PR/review record and CI/CD result | Production release has explicit named authorization. |
| Maintain | Current requirement's change.md for qualifying post-completion changes; incident evidence when applicable | Record the change and actual verification; independent new requirements begin a new directory. |

For repositories without pull requests, use the closest version-controlled review record. Put durable artifacts under version control when repository policy permits it.

## 1. Plan — establish intent before design

Ask only for missing information, but resolve these dimensions in a compact batch:

- **Problem:** What real problem exists now, and what is the pain or impact?
- **Users:** Who is affected, including distinct roles or third parties?
- **Constraints:** What technical, security, compliance, performance, time, cost, or data limits apply?
- **Success:** What measurable acceptance criteria prove the outcome?
- **Non-goals:** What is explicitly out of scope?
- **Change surface and edges:** Which systems, interfaces, permissions, dependencies, and failure modes may be involved?
- **Validation:** Which tests, comparisons, metrics, or screenshots will establish correctness?

Write intent.md with the answers, stated assumptions, and open questions. Do not advance to Design while material uncertainty remains; urgent work gets a shorter intent, not a skipped intent.

## 2. Design — turn intent into a buildable specification

Read intent.md and applicable project rules. Write spec.md describing behavior, data/control flow, affected systems, interfaces and fields, mandatory rules, permissions, observability, and boundary behavior such as timeout, missing data, and dependency failure.

The gate is a specification a reviewer can use to distinguish a correct implementation from a merely plausible one. If it reveals a new uncertainty, return to Plan.

## 3. Build — approve the plan before implementation

First inspect the codebase read-only. Write plan.md naming the files or modules expected to change, implementation approach, test strategy, risks, and rollback or compatibility concerns. Obtain the required approval before changing implementation code.

Then implement only within that accepted plan. Apply the repository's development and testing rules; use focused subagents only when they improve coverage or separation of concerns, while the primary agent owns the final evidence. A material discovery outside plan scope returns to Design or Plan for an updated artifact and approval.

## 4. Test — evidence, then independent review

Run the relevant tests, build, lint/type checks, and targeted manual validation. Preserve the actual commands, exit status, and concise results in the work record; a statement that something is complete is not evidence.

Use a fresh, read-only reviewer context for independent review. Review in this order:

1. Logic and behavioral errors.
2. Security, permissions, data handling, and unsafe failure modes.
3. Conformance with spec.md and plan.md.

For post-completion follow-ups, verify against the accepted behavior delta in change.md and relevant baseline context. Record actual checks and review results in the same entry. Update affected user/API/operational documentation when necessary, while preserving completed requirement baselines and frozen directories.

When evaluation suites exist, rerun them after model, rule, or workflow changes. Turn material production failures into regression tests or evaluations where practical.

For the initial delivery, mark plan.md `Status: completed` with completion date and evidence references only after all planned work and required validation/review are finished. If the plan includes deployment, its required deployment work must also finish; this status never grants production release authority.

## 5. Deploy — prepare safely, authorize explicitly

Record the review outcome with the change or PR, then let normal CI/CD validate the approved artifact. Development or test deployment may proceed only within granted authority. For production, prepare the release, monitoring plan, and rollback path, then wait for explicit authorization from the named release owner. Never self-authorize a production release.

## 6. Maintain — make operations feed the next loop

For user-requested bug fixes or feature adjustments that require code/configuration changes, use [Change recording](references/feedback-loop.md). Decide the request's meaning from the current conversation, then use the current plan's explicit status to route the record. There is no historical-document comparison prerequisite. Ordinary usability feedback does not require an incident report.

For alerts or incidents, start with read-only diagnosis: inspect relevant metrics, logs, recent changes, and known-safe mitigations. Propose a fix, or use only a pre-approved, rehearsed rollback. Do not improvise a high-risk production action.

After recovery, record impact, timeline, evidence, mitigation, root cause or uncertainty, and follow-up in the applicable current work/change record or established incident record. Route required modifications by the current plan status; an independent new requirement starts a new directory and re-enters Plan. Never rewrite a frozen requirement to record an incident.

## Fast decisions and common traps

| Situation | Required response |
| --- | --- |
| Vague feature request | Clarify the missing intent dimensions before design. |
| “It is urgent; skip docs/tests/review.” | Reduce artifact length, not gates or evidence. |
| In-progress plan needs a new system or public interface | Update the affected intent/spec/plan and obtain approval for expanded scope. |
| “I tested it manually.” | Run repeatable checks and record their output. |
| A change is ready for production | Require a named human release authorization. |
| “Fix this” while the current plan is not completed | Revise the relevant current intent/spec/plan; no change.md. |
| User requests a code/configuration fix or feature adjustment after plan completion | Record and track it in the current requirement's change.md. |
| Discussion only, normal planned implementation, or an agent's routine implementation correction | Do not create a change entry. |
| A recorded change is deferred or rejected | Keep the entry and reason; do not treat it as accepted behavior. |

## Completion check

Before declaring a work item complete, confirm that the applicable phase artifacts exist, gates were met with real evidence, review findings were addressed, and the next owner can continue from the repository rather than reconstructing context from chat history.

Identify the current requirement directory, the applicable document sections or change entry, actual verification results, and unresolved follow-ups. Required recording is part of completion: a post-completion fix without its change.md entry is partial work. Do not require retroactive rewriting of completed intent/spec/plan as a closure condition.
