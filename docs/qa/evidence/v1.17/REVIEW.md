# Executed v1.17 evidence

All three profiles ran from a fresh local clone on the same requested branch,
initial commit `5af0f0afc40dc57d97e24ae87e94842c397a9d6a` with no prior Godot cache,
then fast-forwarded cleanly to `ec34ebb` for the explicit seed-list CLI and repeated
full gates. Final exact SHA is recorded in each gate report.
`combat-gates.json`:15 checks,full repeated12,000 profile,clean before/after.
`canonical-gates.json`:11 checks,clean before/after. `foundation-gates.json`:18 full
local checks,external archive retention,Blender,GLB and two actual GPU screenshots.
Both screenshots were inspected; no new combat UI or device performance claim.

`lab-summary.json` contains aggregated metrics and cross-checkout comparison.
`lab-metrics.jsonl.gz` contains one metadata line plus12,000 first-pass records,
including per-seed state/event hashes and measured runtime. Read with standard
Python `gzip.open(...,'rt')` and `json.loads(line)`. Runtime is excluded from the
deterministic metrics hash. Repeated-pass hashes/metrics all match the first pass.
`reflection-lethal-seed0.replay.json` is a complete verified example. Twelve scenario
replays were regenerated/verified by the lab; one is curated here to limit repository
size. `profile-samples.json` records optional instrumented12-seed measurements.
`manifest.json` records artifact SHA-256 and aggregate counts;gzip metadata mtime0.
JSON artifacts normalize CRLF to LF before hashing,matching committed Git blobs.
The initial evidence export exposed that mismatch; normalization and a Git-blob /
clean-checkout hash check corrected it before PROJECT_STATE closeout.

Exact commands and subprocess output are retained in gate JSON. Environment paths
refer to existing local tools and the ignored clean clone; clone execution did not
install anything. Report: `../../V1_17_BALANCE_REPORT.md`.

Development failures were fixed before this snapshot:seed5 cross-trigger readiness;
schema adapter support/normalization. No final required test failed. The legacy
readability script's two known stale identifiers remain the documented unchanged
exception. Remote CI,Linux,phone performance,Android/iOS export/signing and final-art
gates were not executed and are not represented as passes.
