"""Generate reference metadata from frozen inventories without copying images."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = ["characters","arenas","cards","brand-ui","expressions","fx","ux"]


def category(path: str) -> str:
    path = path.lower()
    if "arena" in path or "combat_bg" in path:
        return "arenas"
    if any(p in path for p in ("/cards/", "carte/", "immaggg", "levels/", "background_blue")):
        return "cards"
    if any(p in path for p in ("heroes/", "sprites/", "sheet sprite", "spritesheet")):
        return "characters"
    if "home_keyart" in path or "hero_select_bg" in path or "market_bg" in path:
        return "ux"
    return "brand-ui"


def main() -> None:
    rows = list(csv.DictReader((ROOT / "docs/migration/asset_candidates.csv").open(encoding="utf-8")))
    repo_rows = {r["path"]: r for r in csv.DictReader((ROOT / "docs/migration/repo_inventory.csv").open(encoding="utf-8"))}
    grouped = {}
    for row in rows:
        file = repo_rows[row["path"]]["target_path"] if row["source"] == "repo" else ".work/legacy-source/" + row["path"]
        # Exact source bytes; SVG checkout CRLF can differ from the canonical Git blob.
        sha = repo_rows[row["path"]]["working_sha256"] if row["source"] == "repo" else row["sha256"]
        item = grouped.setdefault(sha, dict(id="ref_"+sha[:16], category=category(row["path"]),
            file=file, sha256=sha, source_type="project-legacy", source_url_or_path=file,
            author_or_owner="unknown; supplied in Hero Smash legacy material",
            rights_status="unknown", status="reference-only", intended_use="Reference and migration review only; no runtime admission",
            tags=["v1.15-inventory", "requires-rights-review"],
            notes="Category inferred from source group; unnamed imagery requires visual subject review. Duplicate origins retained.", origins=[]))
        item["origins"].append(dict(source=row["source"], file=file, original_path=row["path"],
                                    sha256=sha, git_sha256=row["sha256"] if row["source"] == "repo" else None))
    manifest = dict(schema_version=1, generated_by="tools/migration/reference_index.py",
                    inventory_baseline="4ef9eeb503c3c1c69efa36b7b1a3ae5d23cc4816", items=list(grouped.values()))
    existing_path = ROOT / "docs/references/visual/reference_manifest.json"
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        if "production_items" in existing:
            manifest["production_items"] = existing["production_items"]
    (ROOT / "docs/references/visual/reference_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    for name in CATEGORIES:
        out = ROOT / "references/visual" / name / "README.md"
        count = sum(i["category"] == name for i in grouped.values())
        out.write_text(f"# {name} reference catalog\n\n{count} indexed image groups in `docs/references/visual/reference_manifest.json` (filter category `{name}`).\n\nBinaries remain at indexed legacy paths to avoid duplication. Archive-origin entries need the read-only `.work/legacy-source/` copy. Rights remain unknown; these are reference-only. {'No samples admitted yet.' if not count else 'Review unnamed imagery before assigning a hero or approved visual direction.'}\n", encoding="utf-8")
    print(f"Indexed {len(rows)} image paths in {len(grouped)} reference groups; copied zero binaries.")


if __name__ == "__main__":
    main()
