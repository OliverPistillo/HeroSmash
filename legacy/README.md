# Legacy Material

`web-prototype/` contains the historical v1.14.3 runtime, moved with Git history after the v1.15 inventory/classification/proposal commit. All 393 moved files retain their original Git blobs.

Do not manually dump the owner's entire old OneDrive folder into Git.

The migration process should:
- inventory external legacy files;
- hash them;
- copy only approved project assets/data;
- keep a manifest pointing back to external source paths where useful.

The current JS/Canvas runtime is isolated at:
`legacy/web-prototype/`
Start it from any working directory using `python legacy/web-prototype/tools/serve.py`; it serves its own root on localhost:8000. No root-level JS runtime remains.

`archive-index/README.md` points to the full CSV census of the local archive. The archive itself remains outside versioned production at `.work/legacy-source/`; it was not relocated, renamed, pruned, or imported wholesale.
