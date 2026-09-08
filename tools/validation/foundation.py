"""Foundation gates. Missing requested tools fail; no downloads or installations."""
from __future__ import annotations
import argparse
import csv
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from threading import Thread
from urllib.request import urlopen

from data_parity import validate as validate_data
from glb_check import validate as validate_glb

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "legacy/web-prototype"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def census(archive: Path | None) -> dict:
    read_csv = lambda name: list(csv.DictReader((ROOT / "docs/migration" / name).open(encoding="utf-8")))
    rows = read_csv("repo_inventory.csv")
    summary = json.loads((ROOT / "docs/migration/inventory_summary.json").read_text())
    tree = subprocess.check_output(["git", "ls-tree", "-r", "-z", summary["baseline"]], cwd=ROOT)
    baseline = {r.split(b"\t",1)[1].decode():r.split(b"\t",1)[0].split()[2].decode() for r in tree.split(b"\0") if r}
    assert set(baseline) == {r["path"] for r in rows}, "Every baseline path must be inventoried"
    index = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=ROOT)
    indexed = {r.split(b"\t",1)[1].decode():r.split(b"\t",1)[0].split()[1].decode() for r in index.split(b"\0") if r}
    moved = 0
    for row in rows:
        dest = ROOT / row["target_path"]
        if row["path"] == "docs/exec-plans/active/V1_15_FOUNDATION.md" and not dest.exists():
            dest = ROOT / "docs/exec-plans/completed/V1_15_FOUNDATION.md"
        assert dest.is_file(), f"Lost retained path: {dest}"
        if row["disposition"] == "git-mv":
            assert indexed[row["target_path"]] == baseline[row["path"]], f"Changed Git blob: {dest}"
            payload = dest.read_bytes()
            assert hashlib.sha256(payload).hexdigest() in {row["sha256"],row["working_sha256"]} or hashlib.sha256(payload.replace(b"\r\n",b"\n")).hexdigest() == row["sha256"], f"Changed working file: {dest}"
            moved += 1
    assert moved == summary["repo_relocations"] == 393
    for name in ["archive_inventory.csv", "duplicate_report.csv", "data_source_map.md", "asset_source_map.md", "js_to_godot_system_map.md", "MIGRATION_PROPOSAL.md"]:
        assert (ROOT / "docs/migration" / name).stat().st_size > 0
    archived = read_csv("archive_inventory.csv")
    if archive is not None:
        assert archive.is_dir(), f"Missing archive: {archive}"
        actual = {p.relative_to(archive).as_posix() for p in archive.rglob("*") if p.is_file()}
        assert actual == {r["path"] for r in archived}, "Archive path set changed"
        for row in archived:
            assert sha(archive / row["path"]) == row["sha256"], f"Archive modified: {row['path']}"
    dupes = read_csv("duplicate_report.csv")
    assert len({r["sha256"] for r in dupes}) == summary["duplicate_groups"]
    return dict(baseline_paths=len(rows), unchanged_relocations=moved, archive_files=len(archived),
                archive_integrity="pass" if archive else "not-requested; required for local macro closeout", duplicate_groups=summary["duplicate_groups"])


def references(archive: Path | None) -> dict:
    manifest = json.loads((ROOT / "docs/references/visual/reference_manifest.json").read_text(encoding="utf-8"))
    ids = set()
    checked, archive_skipped = 0, 0
    for item in manifest["items"]:
        assert item["id"] not in ids
        ids.add(item["id"])
        assert item["status"] == "reference-only" and item["rights_status"] == "unknown"
        for origin in item["origins"]:
            if origin["source"] == "archive" and archive is None:
                archive_skipped += 1
                continue
            p = ROOT / origin["file"] if origin["source"] == "repo" else archive / origin["original_path"]
            assert sha(p) in {origin["sha256"],origin["git_sha256"]}, f"Reference hash mismatch: {p}"
            checked += 1
    return dict(groups=len(ids), verified_origins=checked, archive_origins_not_requested=archive_skipped)


def web_links() -> dict:
    paths = {"index.html", "manifest.webmanifest", "src/main.js"}
    modules = sorted((WEB / "src").rglob("*.js"))
    for module in modules:
        for relative in re.findall(r"(?:from\s*|import\s*)['\"]([.][^'\"]+)['\"]", module.read_text(encoding="utf-8")):
            p = (module.parent / relative).resolve()
            assert p.is_relative_to(WEB) and p.is_file(), f"Broken module: {module}: {relative}"
            paths.add(p.relative_to(WEB).as_posix())
    def walk(value):
        if isinstance(value, dict):
            for v in value.values(): walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
        elif isinstance(value, str) and value.startswith(("assets/", "data/")) and Path(value).suffix:
            assert (WEB / value).is_file(), f"Missing runtime asset: {value}"
            paths.add(value)
    for p in (WEB / "data").rglob("*.json"):
        paths.add(p.relative_to(WEB).as_posix())
        walk(json.loads(p.read_text(encoding="utf-8")))
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_args): pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(WEB)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for p in sorted(paths):
            with urlopen(f"http://127.0.0.1:{server.server_port}/{p}", timeout=10) as response:
                assert response.status == 200
                assert response.read() == (WEB / p).read_bytes()
    finally:
        server.shutdown(); server.server_close(); thread.join()
    scene = (WEB / "src/scenes/CombatScene.js").read_text(encoding="utf-8")
    assert "new StatusIconBar" in scene and "c.events[0]?.text" in scene
    return dict(modules=len(modules), http_resources=len(paths), current_status_component=True, current_event_text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--godot", help="Existing Godot 4.7.2 executable")
    parser.add_argument("--blender", help="Existing Blender 5.2 LTS executable; version check only")
    parser.add_argument("--pillow-python", help="Existing Python interpreter with Pillow for legacy arena check")
    parser.add_argument("--visual", action="store_true", help="Run actual Mobile renderer at two landscape sizes; requires --godot")
    parser.add_argument("--report", type=Path, default=ROOT / ".work/reports/foundation.json")
    args = parser.parse_args()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    report = dict(schema_version=1, tested_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),
                  working_tree_changes=bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT).strip()), checks=[], limitations=[])
    def check(name, fn):
        try:
            details = fn()
            report["checks"].append(dict(name=name, status="pass", details=details))
            print("PASS " + name, flush=True)
        except Exception as exc:
            report["checks"].append(dict(name=name, status="fail", details=str(exc)))
            print("FAIL " + name + ": " + str(exc), flush=True)
    def command(argv, marker=None, expected_code=0, env=None):
        result = subprocess.run([str(a) for a in argv],cwd=ROOT,text=True,encoding="utf-8",errors="replace",capture_output=True,timeout=60,env=env)
        output = result.stdout + result.stderr
        assert result.returncode == expected_code, output
        if marker: assert marker in output, output
        if expected_code == 0: assert "SCRIPT ERROR:" not in output and not re.search(r"^ERROR:",output,re.M), output
        return dict(command=[str(a) for a in argv], exit_code=result.returncode, output=output)
    check("inventory_and_retention", lambda:census(args.archive))
    check("canonical_metadata", lambda:validate_data(WEB,args.archive))
    check("validator_negative_cases",lambda:command([sys.executable,"-X","utf8",ROOT/"tools/validation/test_validators.py"],"OK"))
    check("reference_manifest", lambda:references(args.archive))
    check("web_modules_assets_http", web_links)
    check("web_seeded_oracle", lambda:command(["node","--experimental-default-type=module",ROOT/"tools/validation/web_oracle.mjs"],"PASS:"))
    check("legacy_asset_validator", lambda:command([sys.executable,"-X","utf8",WEB/"tools/asset_pipeline.py","validate"],"OK:"))
    def stale_check():
        result = command([sys.executable,"-X","utf8",WEB/"tools/combat_readability_check.py"],expected_code=1)
        assert [line for line in result["output"].splitlines() if "MISSING" in line] == ["status_icons: MISSING", "combat_log: MISSING"]
        result["meaning"] = "Expected pre-existing stale identifier failure; not a successful legacy check. Current component/HTTP and browser evidence replace it for relocation."
        return result
    check("legacy_readability_failure_unchanged", stale_check)
    check("glb_structure", lambda:validate_glb(ROOT/"art/exports/props/foundation_sample.glb"))
    def runtime_glb():
        export, runtime = ROOT/"art/exports/props/foundation_sample.glb", ROOT/"game/assets_runtime/props/foundation_sample.glb"
        provenance = json.loads((export.with_suffix(".provenance.json")).read_text())
        assert sha(export) == sha(runtime) == provenance["sha256"]
        assert (ROOT/"art/blender/shared/foundation_sample.blend").stat().st_size < 2_000_000
        return dict(sha256=sha(runtime), bytes=runtime.stat().st_size)
    check("runtime_glb_provenance", runtime_glb)
    if args.pillow_python:
        check("legacy_arena_dimensions_alpha",lambda:command([args.pillow_python,WEB/"tools/validate_arena_assets.py"],"OK: arena assets valid"))
    else:
        report["limitations"].append("Pillow legacy arena check not requested in this profile")
    if args.blender:
        check("blender_version",lambda:command([args.blender,"--version"],"Blender 5.2."))
    else:
        report["limitations"].append("Blender authoring version check not requested in this profile")
    if args.godot:
        check("godot_version",lambda:command([args.godot,"--version"],"4.7.2.stable"))
        check("godot_import",lambda:command([args.godot,"--headless","--path",ROOT/"game","--editor","--import"]))
        check("godot_headless_boot",lambda:command([args.godot,"--headless","--path",ROOT/"game","--quit-after","10"],"FOUNDATION_BOOT_OK"))
        check("godot_determinism_and_scene",lambda:command([args.godot,"--headless","--path",ROOT/"game","--script","res://tests/foundation_test.gd"],"FOUNDATION_TEST_PASS"))
    else:
        report["limitations"].append("Godot gates not requested; this run cannot close v1.15")
    if args.visual:
        if not args.godot:
            check("godot_mobile_visual",lambda:(_ for _ in ()).throw(ValueError("--visual requires --godot")))
        else:
            for resolution in ["1366x768", "844x390"]:
                def visual(resolution=resolution):
                    out = args.report.parent / f"godot-mobile-{resolution}.png"
                    env = {**os.environ,"HERO_SMASH_CAPTURE":str(out.resolve())}
                    result = command([args.godot,"--path",ROOT/"game","--rendering-method","mobile","--resolution",resolution,"--","--capture-foundation"],"FOUNDATION_CAPTURE result=0",env=env)
                    assert "Forward Mobile" in result["output"] and "Vulkan" in result["output"], "Real Vulkan Mobile renderer required"
                    result["screenshot"] = str(out)
                    return result
                check("godot_mobile_"+resolution,visual)
    else:
        report["limitations"].append("Actual GPU/visual gate not requested in this profile")
    if args.archive is None:
        report["limitations"].append("External archive unavailable/not requested; committed census only")
    report["limitations"].extend(["Android SDK and export templates not installed; package/device QA deferred", "iOS export/signing requires Apple toolchain; not part of foundation", "No representative fighters yet; performance budgets intentionally not set"])
    report["status"] = "fail" if any(c["status"] == "fail" for c in report["checks"]) else "pass"
    report["profile"] = "local-foundation" if all([args.archive,args.godot,args.blender,args.pillow_python,args.visual]) else "partial-or-ci"
    args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"{report['status'].upper()} {report['profile']}: {args.report}",flush=True)
    raise SystemExit(1 if report["status"] == "fail" else 0)


if __name__ == "__main__":
    main()
