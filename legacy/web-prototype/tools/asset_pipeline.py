#!/usr/bin/env python3
"""
Hero Smash Asset Pipeline

Usage:
  python3 tools/asset_pipeline.py validate
  python3 tools/asset_pipeline.py manifest
  python3 tools/asset_pipeline.py report
  python3 tools/asset_pipeline.py placeholders

This tool intentionally has zero external dependencies.
"""
from pathlib import Path
import json, hashlib, sys, time, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))

def sha12(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]

def build_manifest():
    cards = load("cards")
    heroes = load("heroes")
    out = {
        "version": "1.1.0",
        "generated_at": int(time.time()),
        "base_path": ".",
        "images": {},
        "categories": {"cards": [], "heroes": [], "ui": [], "fx": []},
        "missing": []
    }
    for c in cards:
        p = ROOT / c["image"]
        key = f"card:{c['id']}"
        out["images"][key] = {
            "id": c["id"], "type": "card", "path": c["image"],
            "exists": p.exists(), "hash": sha12(p) if p.exists() else None,
            "rarity": c.get("rarity"), "branches": c.get("branches", [])
        }
        out["categories"]["cards"].append(key)
        if not p.exists(): out["missing"].append(c["image"])
    for h in heroes:
        p = ROOT / h["image"]
        key = f"hero:{h['id']}"
        out["images"][key] = {
            "id": h["id"], "type": "hero", "path": h["image"],
            "exists": p.exists(), "hash": sha12(p) if p.exists() else None,
            "favoredBranch": h.get("favoredBranch")
        }
        out["categories"]["heroes"].append(key)
        if not p.exists(): out["missing"].append(h["image"])
    return out

def write_manifest():
    manifest = build_manifest()
    (DATA / "asset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    index = {"version":"1.1.0","cards":{},"heroes":{},"branches":{}}
    for k, rec in manifest["images"].items():
        if rec["type"] == "card":
            index["cards"][rec["id"]] = rec
        elif rec["type"] == "hero":
            index["heroes"][rec["id"]] = rec
    try:
        for b in load("branches"):
            index["branches"][b["id"]] = {"icon":b["icon"],"color":b["color"]}
    except Exception:
        pass
    (DATA / "asset_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    js = f"export const ASSET_MANIFEST_V11 = {json.dumps(manifest, indent=2, ensure_ascii=False)};\nexport const ASSET_INDEX_V11 = {json.dumps(index, indent=2, ensure_ascii=False)};\n"
    (ROOT / "src/game/AssetManifest.generated.js").write_text(js, encoding="utf-8")
    return manifest

def validate():
    errors = []
    cards = load("cards")
    heroes = load("heroes")
    ids = set()
    for c in cards:
        if c["id"] in ids: errors.append(f"Duplicate card id: {c['id']}")
        ids.add(c["id"])
        if not (ROOT / c["image"]).exists(): errors.append(f"Missing card image: {c['image']}")
        for field in ["name","rarity","branches","effects","cost","points","max"]:
            if field not in c: errors.append(f"Card {c['id']} missing {field}")
    ids = set()
    for h in heroes:
        if h["id"] in ids: errors.append(f"Duplicate hero id: {h['id']}")
        ids.add(h["id"])
        if not (ROOT / h["image"]).exists(): errors.append(f"Missing hero image: {h['image']}")
        for field in ["name","title","stats","skill"]:
            if field not in h: errors.append(f"Hero {h['id']} missing {field}")
    return errors

def placeholder_svg(label, icon="?", color="#ffb703"):
    label = html.escape(label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="620" viewBox="0 0 420 620">
<rect width="420" height="620" rx="40" fill="#08060d"/>
<rect x="18" y="18" width="384" height="584" rx="32" fill="#171c34" stroke="{color}" stroke-width="6"/>
<text x="210" y="270" text-anchor="middle" font-size="120">{icon}</text>
<text x="210" y="370" text-anchor="middle" fill="#fff" font-family="Arial" font-size="34" font-weight="900">{label}</text>
<text x="210" y="420" text-anchor="middle" fill="{color}" font-family="Arial" font-size="22" font-weight="800">PLACEHOLDER</text>
</svg>'''

def make_placeholders():
    count = 0
    for c in load("cards"):
        p = ROOT / c["image"]
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(placeholder_svg(c["name"], c.get("icon","?")), encoding="utf-8")
            count += 1
    for h in load("heroes"):
        p = ROOT / h["image"]
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(placeholder_svg(h["name"], h.get("icon","?"), h.get("color","#ffb703")), encoding="utf-8")
            count += 1
    return count

def report():
    manifest = build_manifest()
    print("Hero Smash Asset Report")
    print("=======================")
    print("Cards:", len(manifest["categories"]["cards"]))
    print("Heroes:", len(manifest["categories"]["heroes"]))
    print("Missing:", len(manifest["missing"]))
    if manifest["missing"]:
        for m in manifest["missing"]:
            print(" -", m)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "validate":
        errs = validate()
        if errs:
            print("\n".join(errs))
            raise SystemExit(1)
        print("OK: assets/data valid")
    elif cmd == "manifest":
        m = write_manifest()
        print(f"Manifest written: {len(m['images'])} images, {len(m['missing'])} missing")
    elif cmd == "placeholders":
        print(f"Placeholders created: {make_placeholders()}")
        write_manifest()
    elif cmd == "report":
        report()
    else:
        print(__doc__)
        raise SystemExit(2)

if __name__ == "__main__":
    main()
