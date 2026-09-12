# Change recording

## Trigger: current conversation plus plan status

Recognize a user request to fix a bug or adjust functionality that the agent will implement by changing code or configuration. Examples include “fix this error,” “change single-select to multi-select,” and “keep the filters after returning.” Infer intent from the current message and conversation, not a keyword alone. Do not read previous intent/spec/plan files to compare requirements merely to decide whether the request qualifies.

Then route by the current requirement directory's plan status. Use an explicit status already established in the current context; otherwise inspect only the current plan's status first. Approval, partial progress, or an apparently working feature does not establish completion.

| State | Where to record |
| --- | --- |
| Writing intent/spec; plan not yet created | Revise the affected existing intent/spec sections; create plan.md when entering implementation planning. No change.md. |
| Plan drafted, approved, executing, or awaiting its required verification | Revise affected intent/spec/plan sections and progress. No change.md. |
| Full plan finished and plan.md explicitly marked completed | Create or update change.md in that same current directory. Preserve intent/spec/plan as the completed baseline. |
| A new independent requirement is starting | Create docs/<next-requirement>/ with its own intent/spec/plan as those phases occur. Freeze the previous directory. |
| Current directory or completion state is ambiguous | Resolve the missing directory/status fact; do not assume completion or scan historical specifications to classify the request. |

An old feature's fix follows the latest directory's status, not the original feature's status. Once a newer directory exists, do not append to the older change.md. Use references to identify earlier features or rules when relevant.

## Keep the record selective

Record qualifying post-completion requests once the agent is proceeding with implementation. Before editing code, capture the requested correction, expected behavior, and a concise approach. Add actual results afterwards. An urgent authorized mitigation may be recorded as soon as operationally safe, but must be recorded before the item closes.

Do not create entries for:

- Normal execution of the agreed plan or “continue implementing.”
- Routine agent corrections during implementation, such as fixing a compile error introduced in the current work.
- Exploratory questions or suggestions with no implementation decision.
- Pure formatting, mechanical renaming, or other behavior-neutral housekeeping, unless the user explicitly requests a record.

One entry represents one meaningful change, not each message, file, attempt, or commit. After deciding to record, inspect the current change.md to reuse an existing entry for the same work. Keep subsequent outcomes, including deferral, rejection, or unsuccessful verification, on that entry. Do not expand this into a log of every conversation or incidental observation.

Reading relevant specifications to implement a fix correctly is still appropriate. It is not a prerequisite for deciding to record it. When implementation needs historical behavior, check applicable later accepted changes so a baseline spec does not undo a subsequent correction; inspect only relevant context.

## Entry format and document ownership

Create change.md only for the first qualifying post-completion change. Use short sequential IDs within the file; no separate repair directory is needed.

```markdown
# Post-completion changes

## CHG-001 — <short title>
- Date / source: <date and concise request; source link if available>
- Status: in_progress / completed / deferred / rejected
- Problem and intended behavior: <what changes and why>
- Approach and scope: <affected code/configuration and planned action>
- Baseline reference: <relevant requirement/section if known; do not search merely to fill this field>
- Result and verification: <actual change, commands/outcomes or manual evidence; pending until checked>
- Remaining work: <only when applicable>
```

The entry contains the follow-up's intent, specification delta, implementation approach, and verification. Do not also rewrite the completed intent/spec/plan. State behavior changes clearly enough to amend the baseline without forcing the next agent to reconstruct chat history. Link a superseded change when a subsequent accepted decision replaces it; retain the prior record. A proposed delta is not verified implementation: preserve status and actual results separately.

Before initial plan completion, keep the same kinds of information in their owning documents: goals/scope in intent.md, behavior/rules in spec.md, and execution/progress/evidence in plan.md. Update only affected sections; no duplicate change log is required.

Update separately maintained user guides, API docs, or runbooks if the implemented change makes them inaccurate. This does not authorize edits to frozen requirement folders or require a new documentation layer.

Close a change only after the scoped modification and applicable checks/review finish and the record contains the evidence. Report the directory and change ID, outcome, and any pending work. Preserve the completed baseline plan's status; change.md tracks its own progress. Production release still requires the normal release authority.

## Boundary examples

- While writing spec.md: “Make this multi-select.” Update spec.md and intent.md if its scope changes; no change.md.
- During plan execution: “Add validation to that input.” Update the affected spec/plan and implement within authority; no change.md.
- After plan.md is completed: “Saving loses my filters; fix it.” Record CHG-001 in that directory's change.md, implement, and append verification.
- After CHG-001: “The same fix still loses filters on refresh.” Continue CHG-001 and its verification rather than logging each attempt separately.
- Requirement 002 is in progress; a requirement 001 bug is reported. Record needed behavior/steps in 002's spec/plan with a reference to 001; leave 001 frozen.
- Requirement 002's plan is completed; a requirement 001 bug is reported. Record it in 002/change.md with a reference to 001; leave 001 frozen.
