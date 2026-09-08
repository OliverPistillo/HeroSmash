# Legacy Material

This directory will contain retained historical/runtime material after v1.15 inventory.

Do not manually dump the owner's entire old OneDrive folder into Git.

The migration process should:
- inventory external legacy files;
- hash them;
- copy only approved project assets/data;
- keep a manifest pointing back to external source paths where useful.

The current JS/Canvas runtime should eventually move to:
`legacy/web-prototype/`
while preserving Git history via `git mv` where practical.
