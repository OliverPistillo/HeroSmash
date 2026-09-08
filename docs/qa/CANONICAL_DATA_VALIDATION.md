# v1.16 validation

Use the existing pinned Godot 4.7.2. Detect installed tooling before adding anything.
The only added dependency is isolated Python validation tooling, pinned in
`tools/requirements-canonical.txt`. Local detection found jsonschema absent in
Python 3.12/3.13/3.14. No global package, Android SDK, engine or MCP was installed.
The standard validator is [python-jsonschema](https://pypi.org/project/jsonschema/4.25.1/).

```powershell
python -m venv .work/venvs/canonical-data
.work/venvs/canonical-data/Scripts/python.exe -m pip install -r tools/requirements-canonical.txt
.work/venvs/canonical-data/Scripts/python.exe tools/migration/canonical_data.py --check
.work/venvs/canonical-data/Scripts/python.exe tools/validation/canonical.py --godot .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --expected-branch revival/v1.16-canonical-data
```

Generation without `--check` writes only fully built/validated derived outputs.
It never edits a legacy input. Before changing sources or progression rules, change
the authoritative specification and review the migration diff; the baseline lock
is not a routine escape hatch.

Required v1.16 checks:

- Five full dataset schemas, raw-field parity, IDs 1–150 and 12 branches, 90/36/24
  rarity and 84/66 membership counts, cost/max-level preservation including ID071.
- Exact generated-byte comparison and repeated in-memory generation, source-hash
  guards, provenance pointers and original-text guards.
- Shared 30-case malformed corpus in Python/Godot: type/required/unknown fields,
  duplicates, unknown branch aliases, lost metadata, invalid levels, references,
  unsupported schema version/trigger/action/handler, unit/condition/timer errors.
- Godot typed loader, copy isolation, failed-reload transactionality, malformed
  JSON errors and fail-closed schema keywords.
- Twelve pilot contracts and all 138 unavailable definitions: known amounts,
  threshold boundaries/remainders, min/max healing, chance vectors/endpoints,
  rejection-sampling vector, conditional draws, Toxin/Shield stacks, reflection
  suppression, independent action caps and command ordering.
- Eight seeds × 400 input events × two executions, exact state/RNG/log equality;
  actor-mirror comparison; timer partition independence; invalid input, work/number
  bounds and rollback; full v1.15 foundation profile separately.

For clean-checkout evidence, commit all code and generated Godot UID files, clone
the current branch into a fresh ignored `.work/` directory, and run the same command
there with `--require-clean` and absolute paths to the existing Python/Godot tools.
The report captures commit, baseline, branch, package versions, commands and output.
The clone must have no prior `.godot` cache and stay clean after import/tests.

CI uses the pinned official engine acquisition already introduced in v1.15 and
installs requirements only inside the disposable runner. Pull-request checkouts
can be detached: the optional local `--expected-branch` guard is omitted in CI;
baseline ancestry/tag and clean-file checks remain required. Remote CI execution
must be reported separately from a local run.

No UI/art changed in v1.16. Android/iOS release/device and final-art performance
gates remain later-phase checks. A full local foundation run still rechecks the
existing sample GLB/Blender pipeline, web oracle, archive integrity and screenshots.
