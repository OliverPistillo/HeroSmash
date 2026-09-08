# MCP / Tool Plan

## Principle

Use the fewest powerful integrations necessary.
Every MCP expands the agent's authority and attack surface.

Prefer native Codex shell/filesystem capabilities and deterministic CLI tools where possible.

## Phase 1 — Foundation

### GitHub
Use for:
- branches;
- issues/PRs;
- code review;
- CI visibility.

Keep `main` protected by workflow convention even if branch protection is not yet configured.

### Browser / Playwright
Use for:
- external docs validation;
- web prototype parity checks;
- screenshot/reference capture where rights permit.

For the final Godot runtime, browser automation is secondary.

## Phase 2 — Blender automation

Candidate integration:
- Blender MCP capable of executing controlled Blender Python and observing the viewport.

Requirements before enabling:
- pin a reviewed version/commit;
- understand exposed commands;
- avoid transmitting private files unnecessarily;
- run on localhost;
- restrict the working directories;
- keep Blender source under versioned project structure;
- validate outputs independently.

Blender automation goals:
- scene inspection;
- model/material edits;
- rig checks;
- animation checks;
- render/reference screenshots;
- GLB export.

## Godot automation

Start with **Godot CLI/headless**, not a Godot MCP.

Why:
- deterministic;
- official;
- simple to audit;
- ideal for CI;
- sufficient for import validation, tests and export.

Add a Godot-specific MCP only if it demonstrably improves editor/scene manipulation after v1.15.

## Optional later tools

- Android SDK/ADB for device smoke tests.
- Image comparison tooling for visual regression.
- Local performance log parsers.
- Git LFS if the production repository starts carrying large binary source assets.

## Tool admission checklist

Before adding any new MCP:
- What task does it unlock?
- Can native shell/CLI do it more safely?
- Is the implementation maintained?
- Can it execute arbitrary code?
- What folders/network endpoints can it access?
- Is it pinned?
- How is output validated?
