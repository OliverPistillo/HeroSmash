# Read-only archive index

Authoritative snapshot: `docs/migration/archive_inventory.csv` and `inventory_summary.json`.

Local source `.work/legacy-source/`: 1,152 files, including 299 original asset/data files, 405 nested web-checkout files and 448 nested Git metadata files. SHA-256 records cover every file, including nested metadata. The original external OneDrive folder is untouched.

Run full archive validation using `python tools/validation/foundation.py --archive .work/legacy-source` (other Godot/Blender flags are needed for the complete foundation gate). No command mutates this archive. Do not run cleanup or Git maintenance inside it.
