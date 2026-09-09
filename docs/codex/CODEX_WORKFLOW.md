# Codex Workflow for Hero Smash

## Operating model

ChatGPT project discussions define intent and decisions.
Codex executes implementation work inside the local repository.

The repository must therefore carry enough durable context that a new Codex task does not require reconstructing project history from chat.

## Before assigning a macro task

Ensure the prompt includes:
- desired outcome;
- constraints;
- relevant paths;
- acceptance criteria;
- whether it may modify architecture/data;
- expected validations.

## Recommended prompt form

Write tasks like a strong GitHub issue:

1. Goal.
2. Context.
3. Scope.
4. Out of scope.
5. Files/systems to inspect.
6. Acceptance criteria.
7. Required tests.
8. Required artifacts/screenshots.
9. State update requirements.

See `PROMPT_TEMPLATE.md`.

## Agent behavior expectations

Codex should:
- inspect before editing;
- preserve history;
- prefer small reversible commits;
- validate changes;
- report evidence;
- update generated inventories when source data changes.

Codex should not:
- rewrite whole systems merely because a rewrite is easier;
- silently change game rules;
- invent missing canonical data;
- move/delete legacy assets before inventory;
- approve its own visual direction without reference criteria.

## Macro phase closeout

At phase completion:
1. all quality gates run;
2. migration/inventory reports refreshed;
3. architecture decisions recorded;
4. active plan moved to completed;
5. `PROJECT_STATE.md` updated;
6. commit SHA recorded;
7. next phase has an active execution plan.
