"""Run all portable v1.16 gates; require an explicit existing Godot executable."""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "80c098b256f5855d4c5dfb9869135fd2bad6c709"


def run(command):
    result = subprocess.run(list(map(str,command)),cwd=ROOT,text=True,encoding="utf-8",errors="replace",capture_output=True,timeout=60,env={**os.environ,"PYTHONUTF8":"1"})
    output = result.stdout + result.stderr
    passed = result.returncode == 0 and "SCRIPT ERROR" not in output and "Parse Error" not in output
    return dict(command=list(map(str,command)),status="pass" if passed else "fail",exit_code=result.returncode,output=output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot",type=Path,required=True)
    parser.add_argument("--require-clean",action="store_true")
    parser.add_argument("--expected-branch",help="optional local task branch guard; CI may use a detached checkout")
    parser.add_argument("--report",type=Path,default=ROOT/".work/reports/canonical.json")
    args = parser.parse_args()
    godot = args.godot.resolve()
    checks = []

    def add(name,command):
        try:
            check=run(command)
        except (OSError,subprocess.TimeoutExpired) as error:
            check=dict(command=list(map(str,command)),status="fail",error=str(error))
        check["name"]=name
        checks.append(check)
        return check

    add("baseline_ancestor",["git","merge-base","--is-ancestor",BASELINE,"HEAD"])
    tag=add("baseline_tag",["git","rev-parse","v1.15-foundation^{commit}"])
    if tag.get("output","").strip() != BASELINE: tag["status"]="fail"
    branch=add("checkout_branch",["git","branch","--show-current"])
    if args.expected_branch and branch.get("output","").strip() != args.expected_branch: branch["status"]="fail"
    if args.require_clean:
        clean=add("clean_before",["git","status","--porcelain"])
        if clean.get("output","").strip(): clean["status"]="fail"
    version=add("godot_version",[godot,"--version"])
    if not version.get("output","").startswith("4.7.2.stable."): version["status"]="fail"
    add("reproducible_generation_and_diff",[sys.executable,"tools/migration/canonical_data.py","--check"])
    add("schema_source_parity_and_malformed_data",[sys.executable,"tools/validation/test_canonical_data.py"])
    add("godot_import",[godot,"--headless","--path","game","--editor","--import","--quit"])
    for suite in ("canonical_data", "effect"):
        check=add(suite+"_headless",[godot,"--headless","--path","game","--script",f"res://tests/{suite}_test.gd"])
        summaries=[]
        for line in check.get("output","").splitlines():
            if line.startswith("{"):
                try: summaries.append(json.loads(line))
                except json.JSONDecodeError: pass
        if len(summaries) != 1 or summaries[0].get("status") != "pass" or not summaries[0].get("assertions",0): check["status"]="fail"
        check["test_summaries"]=summaries
    if args.require_clean:
        clean=add("clean_after",["git","status","--porcelain"])
        if clean.get("output","").strip(): clean["status"]="fail"
    packages={name:importlib.metadata.version(name) for name in ("jsonschema","attrs","referencing","rpds-py","jsonschema-specifications")}
    if sys.version_info < (3,13): packages["typing-extensions"]=importlib.metadata.version("typing-extensions")
    report=dict(phase="v1.16",status="pass" if all(c["status"]=="pass" for c in checks) else "fail",commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),branch=branch.get("output","").strip(),baseline=BASELINE,python=platform.python_version(),platform=platform.platform(),packages=packages,clean_checkout=args.require_clean,checks=checks,limits=["Only base_text_v1; numbered levels and global combat/status/death rules remain unresolved.","Foundation full profile is a separate required local gate.","No Android/iOS package/device or final-art gate is claimed.","Local execution is not evidence of a remote GitHub Actions run."])
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for check in checks: print(check["name"]+": "+check["status"])
    print(json.dumps({"status":report["status"],"checks":len(checks),"report":str(args.report)}))
    return 0 if report["status"]=="pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
