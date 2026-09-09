"""Rebuild the safe Blender sample; admit its GLB only after validation."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/validation"))
from glb_check import validate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True, help="Existing Blender 5.2 LTS executable; never installs")
    args = parser.parse_args()
    subprocess.run([args.blender, "--background", "--factory-startup", "--python-exit-code", "1", "--python",
                    str(ROOT / "art/pipeline/create_foundation_sample.py")], cwd=ROOT, check=True)
    source = ROOT / "art/exports/props/foundation_sample.glb"
    report = validate(source)
    runtime = ROOT / "game/assets_runtime/props/foundation_sample.glb"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, runtime)
    report["generated_by"] = "art/pipeline/create_foundation_sample.py"
    report["runtime_copy"] = runtime.relative_to(ROOT).as_posix()
    (ROOT / "art/exports/props/foundation_sample.provenance.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
