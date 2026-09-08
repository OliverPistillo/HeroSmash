"""Read-only foundation census. Snapshot first; never move/delete source files."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "4ef9eeb"
REPORTS = ROOT / "docs/migration"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def target(path: str) -> str:
    p = Path(path)
    move = (p.parts[0] in {"src", "data", "assets", "previews"}
            or path in {"README.md", "index.html", "manifest.webmanifest"}
            or path.startswith("PATCH_NOTES_")
            or (p.parts[0] == "docs" and len(p.parts) == 2 and path != "docs/index.md")
            or (p.parts[0] == "tools" and p.suffix == ".py" and len(p.parts) == 2))
    return "legacy/web-prototype/" + path if move else path


def classify(path: str, archive: bool = False) -> tuple[str, str]:
    p = Path(path)
    if ".git" in p.parts:
        return "obsolete", "nested Git metadata; retained locally, never imported"
    if archive and path.startswith("HeroSmash/"):
        return classify(path.removeprefix("HeroSmash/"))
    if path in {"data/legacy_deck_source.json", "data/branches.json", "data/economy.json"}:
        return "canonical-data", "identity/metadata or verified baseline constants; see data_source_map.md"
    if path == "hero.json.txt":
        return "reference", "20 candidate heroes; approval deferred to v1.18"
    if path in {"vecchio/deck.json", "vecchio/cards.json", "vecchio/cards_updated.json"}:
        return "reference", "alternate card source; compare before admission"
    if p.suffix == ".import":
        return "generated-asset", "old Godot import metadata; no production admission"
    if path.startswith("assets/sprites/") and p.suffix == ".json":
        return "generated-asset", "prototype animation metadata paired with placeholder sprite"
    if path == "docs/references/visual/reference_manifest.json":
        return "reference", "foundation reference registry; example entry to replace with inventory"
    if p.suffix in {".png", ".webp", ".jpeg", ".jpg", ".svg"}:
        if p.suffix == ".svg" or path.startswith("assets/sprites/"):
            return "generated-asset", "prototype placeholder; retain for behavior oracle"
        return "reference", "production candidate only after rights and visual review"
    if path.startswith("src/") or path.startswith("data/") or path.startswith("tools/") and p.suffix == ".py" or path in {"index.html", "manifest.webmanifest"}:
        return "current-js-behavior-prototype", "preserve byte-for-byte in isolated web root"
    if p.suffix == ".md" or p.name in {".gitignore", ".gitkeep"}:
        return "reference", "project governance or historical documentation; target identifies retention"
    return "unknown", "retain; explicit review required before production use"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--archive", type=Path, default=ROOT / ".work/legacy-source")
    parser.add_argument("--output", type=Path, default=REPORTS)
    args = parser.parse_args()
    sha = git("rev-parse", args.baseline).decode().strip()
    paths = git("ls-tree", "-r", "--name-only", "-z", sha).decode().strip("\0").split("\0")
    repo = []
    for path in sorted(paths):
        blob = git("show", f"{sha}:{path}")
        current = ROOT / path
        if not current.exists() or target(path) != path and (ROOT / target(path)).exists():
            current = ROOT / target(path)
        # Baseline blobs remain reproducible even when governance files evolve.
        working = current.read_bytes() if current.is_file() else blob
        category, note = classify(path)
        repo.append(dict(path=path, target_path=target(path), bytes=len(blob),
                         sha256=digest(blob), working_sha256=digest(working),
                         classification=category, disposition="git-mv" if target(path) != path else "keep", notes=note))
    archive = []
    if not args.archive.is_dir():
        raise SystemExit(f"Archive is missing: {args.archive}")
    for f in sorted(args.archive.rglob("*")):
        if f.is_symlink():
            raise SystemExit(f"Symlink requires review: {f}")
        if not f.is_file():
            continue
        path = f.relative_to(args.archive).as_posix()
        category, note = classify(path, True)
        payload = f.read_bytes()
        archive.append(dict(path=path, bytes=len(payload), sha256=digest(payload),
                            classification=category, disposition="retain-read-only", notes=note))
    groups = defaultdict(list)
    for scope, rows in (("repo", repo), ("archive", archive)):
        for row in rows:
            # Exact disk-byte comparison. Git canonical bytes recorded independently.
            groups[row.get("working_sha256", row["sha256"])].append((scope, row))
    duplicates = []
    for hash_value, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        scopes = {scope for scope, _ in members}
        kind = "cross-source" if len(scopes) == 2 else "within-" + next(iter(scopes))
        preferred = next(("repo:" + r["path"] for s, r in members if s == "repo"), "archive:" + members[0][1]["path"])
        for scope, row in members:
            duplicates.append(dict(sha256=hash_value, group_size=len(members), kind=kind,
                                   source=scope, path=row["path"], preferred_reference=preferred,
                                   disposition="retain-all; no deletion authorized"))
    write_csv(args.output / "repo_inventory.csv", repo, list(repo[0]))
    write_csv(args.output / "archive_inventory.csv", archive, list(archive[0]))
    write_csv(args.output / "duplicate_report.csv", duplicates,
              ["sha256", "group_size", "kind", "source", "path", "preferred_reference", "disposition"])
    candidates = [dict(source=s, path=r["path"], sha256=r["sha256"],
                       rights_status="unknown", decision="reference-only; review before runtime admission")
                  for s, rows in (("repo", repo), ("archive", archive)) for r in rows
                  if Path(r["path"]).suffix in {".png", ".webp", ".jpg", ".jpeg", ".svg"}]
    write_csv(args.output / "asset_candidates.csv", candidates, list(candidates[0]))
    summary = dict(baseline=sha, main=git("rev-parse", "main").decode().strip(),
                   archive_root=".work/legacy-source", external_original="not accessed or modified",
                   repo_files=len(repo), repo_bytes=sum(r["bytes"] for r in repo),
                   archive_files=len(archive), archive_bytes=sum(r["bytes"] for r in archive),
                   archive_original_material=sum(not r["path"].startswith("HeroSmash/") for r in archive),
                   archive_git_metadata=sum(".git" in Path(r["path"]).parts for r in archive),
                   repo_relocations=sum(r["disposition"] == "git-mv" for r in repo),
                   duplicate_groups=len({r["sha256"] for r in duplicates}), duplicate_members=len(duplicates),
                   cross_source_duplicate_groups=len({r["sha256"] for r in duplicates if r["kind"] == "cross-source"}),
                   classification_repo=dict(Counter(r["classification"] for r in repo)),
                   classification_archive=dict(Counter(r["classification"] for r in archive)))
    (args.output / "inventory_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
