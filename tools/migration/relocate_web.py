"""Execute only the committed inventory move proposal; never touch the archive."""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ["repo_inventory.csv", "archive_inventory.csv", "duplicate_report.csv",
            "data_source_map.md", "asset_source_map.md", "js_to_godot_system_map.md", "MIGRATION_PROPOSAL.md"]


def main() -> None:
    for name in REQUIRED:
        path = ROOT / "docs/migration" / name
        if not path.is_file() or not path.stat().st_size:
            raise SystemExit(f"Required report missing/empty: {name}")
        subprocess.run(["git", "ls-files", "--error-unmatch", path.relative_to(ROOT).as_posix()], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        raise SystemExit("Commit and review inventory/proposal first; working tree must be clean.")
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT).decode().strip()
    if branch != "revival/v1.15-foundation":
        raise SystemExit(f"Unexpected branch: {branch}")
    rows = list(csv.DictReader((ROOT / "docs/migration/repo_inventory.csv").open(encoding="utf-8")))
    moves = [row for row in rows if row["disposition"] == "git-mv"]
    for row in moves:
        source, destination = ROOT / row["path"], ROOT / row["target_path"]
        if not source.resolve().is_relative_to(ROOT) or not destination.resolve().is_relative_to(ROOT / "legacy/web-prototype"):
            raise SystemExit("Move escapes the approved workspace")
        if destination.exists() or not source.is_file():
            raise SystemExit(f"Unexpected move input/output: {source}")
        if hashlib.sha256(source.read_bytes()).hexdigest() != row["working_sha256"]:
            raise SystemExit(f"Source changed since inventory: {source}")
    for row in moves:
        destination = ROOT / row["target_path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", "--", row["path"], row["target_path"]], cwd=ROOT, check=True)
    print(f"Moved {len(moves)} inventoried files; no archive access or deletions.")


if __name__ == "__main__":
    main()
