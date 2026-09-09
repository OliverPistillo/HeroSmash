"""Rebuild v1.18 reference metadata. Never writes source images or the archive."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/references/visual/v1.18"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".tga", ".bmp"}
RIGHTS = {"owned-original", "generated-for-project", "licensed", "third-party-reference-only", "unknown-rights", "prohibited-for-production"}


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)


def production_references() -> dict[str, dict]:
    """Validate the separate owner-approved packet without promoting historical IDs."""
    items = read("docs/references/visual/reference_manifest.json").get("production_items", [])
    if not items:
        return {}
    folder = "references/visual/characters/solkael_lionheart/production/"
    packet = read(folder + "SOLKAEL_ART_LOCK_v1_MANIFEST.json")
    supplied = {folder + f["file"]: f for f in packet["files"]}
    result = {}
    ids = set()
    for item in items:
        path = item["file"]
        assert path in supplied and path not in result
        assert item["id"] == Path(path).stem.lower() and item["id"] not in ids
        ids.add(item["id"])
        assert item["source_type"] == item["rights_status"] == "generated-for-project"
        assert item["approval_status"] == "production-approved" and item["art_lock"] == "v1"
        assert item["rights_evidence"] == "docs/art/SOLKAEL_ART_LOCK.md"
        assert (ROOT / item["rights_evidence"]).is_file()
        data = (ROOT / path).read_bytes()
        assert len(data) == item["bytes"] == supplied[path]["bytes"], path
        assert digest(data) == item["sha256"] == supplied[path]["sha256"], path
        result[path] = item
    assert set(result) == set(supplied) and len(result) == 8
    assert {p.name for p in (ROOT / folder).iterdir() if p.is_file()} == {Path(p).name for p in supplied} | {"SOLKAEL_ART_LOCK_v1_MANIFEST.json"}
    return result


def build() -> dict[str, bytes]:
    historical = read("docs/references/visual/reference_manifest.json")
    production = production_references()
    reviews = read("docs/references/visual/v1.18/review_decisions.json")
    groups: dict[str, dict] = {}
    origins: set[str] = set()
    for old in historical["items"]:
        for origin in old["origins"]:
            sha = origin["git_sha256"] or origin["sha256"]
            group = groups.setdefault(sha, dict(id="ref_" + sha[:16], sha256=sha, category=old["category"], historical_ids=[], origins=[]))
            if old["id"] not in group["historical_ids"]:
                group["historical_ids"].append(old["id"])
            group["origins"].append(dict(path=origin["file"], source=origin["source"], hash_basis="git-blob" if origin["source"] == "repo" else "file-bytes", sha256=sha, historical_working_sha256=origin["sha256"]))
            origins.add(origin["file"])
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    excluded = []
    for path in sorted(p for p in tracked if Path(p).suffix.lower() in EXTENSIONS):
        if path in production:
            continue  # Separately hash-validated owner-approved v1.19 catalog.
        if path in origins:
            continue
        if path.startswith("docs/qa/"):
            excluded.append(dict(path=path, reason="QA evidence / temporary planning artifact; not a design reference"))
            continue
        sha = digest(git_bytes(path))
        group = groups.setdefault(sha, dict(id="ref_" + sha[:16], sha256=sha, category="unclassified", historical_ids=[], origins=[]))
        group["origins"].append(dict(path=path, source="repo", hash_basis="git-blob", sha256=sha))
    items = []
    for sha, item in sorted(groups.items()):
        item.update(source=item["origins"][0]["path"], author_owner="unknown; supplied in project legacy", rights_status="unknown-rights", rights_evidence=[], project_usage="internal reference review only", approval_status="reference-only", production_usable=False, associations=[], tags=["v1.18-audited", "rights-unresolved"], notes="Inventory classification; no inferred production license.")
        if sha in reviews["by_sha256"]:
            item.update(reviews["by_sha256"][sha])
        items.append(item)
    duplicates = [dict(id=i["id"], sha256=i["sha256"], paths=[o["path"] for o in i["origins"]], historical_ids=i["historical_ids"]) for i in items if len(i["origins"]) > 1]
    catalog = dict(schema_version=2, authority="metadata and reference direction only; no production admission without rights evidence", source_manifest="docs/references/visual/reference_manifest.json", hash_policy="Git blob bytes for tracked text/binaries; original file bytes for archive. Historical working hashes retained. SVG LF/CRLF equivalence is explicitly separate from byte duplicates.", rights_classes=sorted(RIGHTS), items=items)
    report = dict(schema_version=1, groups=len(items), origins=sum(len(i["origins"]) for i in items), duplicate_groups=len(duplicates), duplicate_extra_origins=sum(len(i["origins"])-1 for i in items), duplicates=duplicates, excluded_evidence=excluded, copied_images=0, deleted_images=0)
    return {"reference_inventory.json": encoded(catalog), "reference_duplicates.json": encoded(report)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in build().items():
        (OUT / name).write_bytes(data)
    print("Rebuilt reference inventory and duplicate report; zero image mutations.")


if __name__ == "__main__":
    main()
