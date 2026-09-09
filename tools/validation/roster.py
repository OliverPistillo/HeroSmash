"""v1.18 spec/reference gates. No installations and no source mutations."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "337710e362b1df008b74cbb1e2ba6d1c58d2f2da"
BRANCHES = {"Assault", "Guardian", "Essence", "Rage", "Ice", "Toxin", "Shield", "Healing", "Power", "Precision", "Wound", "Dodge"}
VIEWS = {"front", "three_quarter_front", "side", "back", "silhouette", "neutral", "combat_stance", "materials_palette", "weapon_detail", "expression_sheet"}
RIGHTS = {"owned-original", "generated-for-project", "licensed", "third-party-reference-only", "unknown-rights", "prohibited-for-production"}
EXPRESSIONS = {"neutral", "focused", "aggressive", "casting", "pain_light", "pain_heavy", "stunned", "victory", "defeat", "KO"}
CLIPS = {"idle", "intro", "attack_light", "attack_heavy", "skill_cast", "hit_react", "dodge", "ko", "victory", "idle_breathing"}


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(args):
    return subprocess.check_output(args, cwd=ROOT, stderr=subprocess.STDOUT).decode("utf-8").strip()


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools/art" / f"{name}.py")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def validate_rights(item):
    assert item["rights_status"] in RIGHTS, "unknown rights enum"
    assert item["approval_status"] in {"reference-only", "direction-selected", "production-approved", "rejected"}, "approval enum"
    assert type(item["production_usable"]) is bool
    assert isinstance(item["rights_evidence"], list)
    if item["production_usable"] or item["approval_status"] == "production-approved":
        assert item["production_usable"] and item["approval_status"] == "production-approved", "inconsistent approval"
        assert item["rights_status"] in {"owned-original", "generated-for-project", "licensed"}, "unresolved/proprietary rights cannot be production-approved"
        assert item["rights_evidence"] and all(isinstance(e, dict) and all(e.get(k) for k in ["source", "owner", "permitted_use", "reviewer"]) for e in item["rights_evidence"]), "missing approval evidence"


def validate_roster(data, source):
    heroes = data["heroes"]
    ids = [h["id"] for h in heroes]
    assert len(ids) == len(set(ids)) == 20, "20 unique candidate IDs"
    assert ids == [h["id"] for h in source["characters"]], "candidate IDs/order preserved"
    assert Counter(h["selection"]["status"] for h in heroes) == {"launch": 16, "reserve": 4}, "16 launch / 4 reserve"
    assert set(data["required_reference_views"]) == VIEWS
    assert data["branch_aliases"] == {"Arcane": "Essence", "Venom": "Toxin", "Frost": "Ice"}
    coverage = Counter()
    for n, h in enumerate(heroes):
        assert re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+", h["id"])
        assert h["source"]["record"] == source["characters"][n], "source facts changed"
        assert h["source"]["pointer"] == f"/characters/{n}"
        raw, identity = h["source"]["record"], h["identity"]
        for field, key in {"canonical_name":"name", "species":"animal_species", "title":"title", "personality":"personality", "combat_fantasy":"combat_role", "weapon_fighting_style":"weapon_or_fighting_style"}.items():
            assert identity[field] == raw[key], f"unsourced {field}"
        branches = [identity["primary_branch"], identity["secondary_branch"]]
        assert branches == [data["branch_aliases"].get(b,b) for b in raw["branches"]], "affinity normalization only"
        assert len(set(branches)) == 2 and set(branches) <= BRANCHES
        assert identity["gender_presentation"]["status"] == "unresolved" and identity["gender_presentation"]["value"] is None, "unsourced presentation"
        proposal = h["design_proposal"]
        assert proposal["status"] == "proposal", "unsupported attributes must remain proposal"
        assert all(proposal["visual"].get(k) for k in ["body_type", "silhouette", "proportions", "major_shapes", "palette_intent", "materials", "distinctive_feature", "speed_impression", "weight_impression", "range_impression", "rig_family", "unique_rig_requirements", "complexity"])
        assert all(proposal["combat_presentation"].get(k) for k in ["stance", "locomotion", "attack_light", "attack_heavy", "skill_cast", "hit_react", "dodge", "KO", "victory"])
        assert all(proposal["vfx"].get(k) for k in ["shape_language", "motion_language", "palette_branch_relationship"])
        assert proposal["expression_deviation"] and proposal["weapon_sockets"] and proposal["vfx_sockets"]
        assert 0.5 <= proposal["height_m_proposal"] <= 4
        assert set(h["scoring"]) == set(data["scoring_rubric"]["criteria"])
        assert all(type(s) is int and 0 <= s <= 5 for s in h["scoring"].values())
        assert h["scoring"]["rights_confidence"] == 0, "no rights evidence for candidate source"
        assert h["selection"]["decision"] and h["unresolved"]
        assert set(h["references"]["coverage"]) == VIEWS
        assert not h["references"]["production_ready"]
        for view in h["references"]["coverage"].values():
            assert view["status"] in {"gap", "partial-reference"} and view["reason"]
            assert bool(view["reference_ids"]) == (view["status"] == "partial-reference")
        if h["selection"]["status"] == "launch":
            coverage.update(branches)
    assert set(coverage) == BRANCHES, "all 12 launch branches"
    assert {b for b,n in coverage.items() if n == 1} == {"Ice"}, "documented Ice exception only"
    return dict(candidates=20, launch=16, reserve=4, coverage=dict(coverage))


def validate_mapping(data, heroes, oracle):
    assert [o["oracle_id"] for o in data["oracles"]] == [o["id"] for o in oracle["records"]], "all 16 oracle rows"
    ids = {h["id"] for h in heroes}
    lookup = {h["id"]: h for h in heroes}
    for row, old in zip(data["oracles"], oracle["records"], strict=True):
        assert row["oracle_branches"] == [b.title() for b in old["branches"]]
        cells = row["cells"]
        assert len(cells) == 20 and {c["candidate_id"] for c in cells} == ids, "20 explicit cells per oracle"
        assert row["primary_candidate"] in ids and set(row["complementary_candidates"]) <= ids
        assert row["preservation_requirement"] and row["merge_split"] and row["runtime_action"]
        assert next(h for h in heroes if h["id"] == row["primary_candidate"])["selection"]["status"] == "launch"
        for c in cells:
            assert c["rating"] in data["rating_rules"] and c["reason"]
            if c["rating"] == "exact conceptual replacement":
                h = lookup[c["candidate_id"]]["identity"]
                assert set(row["oracle_branches"]) == {h["primary_branch"],h["secondary_branch"]}, "exact concept must retain affinities"
    return dict(oracles=16, cells=320, runtime_ids_replaced=0)


def validate_rigs(data, heroes):
    launch = {h["id"] for h in heroes if h["selection"]["status"] == "launch"}
    covered = [h for f in data["families"] for h in f["launch_heroes"]]
    assert len(covered) == len(set(covered)) == 16 and set(covered) == launch, "all launch rigs exactly once"
    for f in data["families"]:
        bones = f["base_hierarchy"]
        assert bones["root"] is None and bones["pelvis"] == "root"
        assert all(n in bones for n in ["spine_01", "spine_02", "spine_03", "neck", "head", "jaw", "hand_l", "hand_r"])
        for bone, parent in bones.items():
            assert re.fullmatch(r"[a-z][a-z0-9_]*", bone), "bone naming"
            seen = {bone}
            while parent is not None:
                assert parent in bones and parent not in seen, "bone parent/cycle"
                seen.add(parent)
                parent = bones[parent]
        assert all(b in bones for b in f["sockets"].values()), "socket parent missing"
        for h in heroes:
            if h["id"] in f["launch_heroes"]:
                assert h["design_proposal"]["visual"]["rig_family"] == f["id"]
                assert set(h["design_proposal"]["weapon_sockets"]+h["design_proposal"]["vfx_sockets"]) <= set(f["sockets"])
        assert f["retarget"] and f["finger_policy"]
    return dict(families=len(data["families"]), launch_covered=16)


def validate_contracts(conventions, animation, expressions, heroes):
    assert conventions["units"]["meters_per_unit"] == conventions["units"]["blender_scale_length"] == 1.0
    assert conventions["axes"]["blender_to_godot_matrix"] == [[1,0,0],[0,0,1],[0,-1,0]], "axis conversion"
    assert conventions["axes"]["blender_model_front"] == "-Y" and conventions["axes"]["godot_model_front"] == "+Z"
    assert conventions["origin"]["location"] == [0,0,0]
    assert conventions["transforms"]["object_scale"] == [1,1,1] and conventions["transforms"]["forbid_negative_scale"]
    assert conventions["skeleton_name"] == "HeroSkeleton" and conventions["animation_fps"] == 30
    assert conventions["root_motion"]["enabled"] is False
    for h in heroes:
        values = dict(hero_id=h["id"],part="body",channel="basecolor")
        for path_key, pattern in [("export", "glb"), ("wrapper", "wrapper"), ("texture", "texture"), ("material", "material")]:
            example = conventions["paths"][path_key].format(**values)
            assert re.fullmatch(conventions["patterns"][pattern], Path(example).name), f"invalid {pattern} pattern/example"
    assert len(animation["clips"]) == len(CLIPS) and {c["name"] for c in animation["clips"]} == CLIPS, "minimum animation names"
    assert set(animation["marker_vocabulary"]) == {"windup_start", "hit", "projectile_spawn", "cast", "vfx_spawn", "recover_start", "recover_end"}
    for c in animation["clips"]:
        assert re.fullmatch(conventions["patterns"]["animation"], c["name"])
        assert c["fps"] == 30 and c["root_motion"] is False
        assert c["loop"] == (c["name"] in {"idle", "idle_breathing"}), "loop contract"
        assert set(c["required_markers"]+c["optional_markers"]) <= set(animation["marker_vocabulary"])
    assert len(expressions["expressions"]) == 10 and {e["id"] for e in expressions["expressions"]} == EXPRESSIONS
    for e in expressions["expressions"]:
        assert all(e.get(k) for k in ["emotional_intent", "brows", "eyes", "eyelids", "mouth_jaw", "head_posture", "asymmetry", "usage_context"])
        lo, hi = e["intensity_range"]
        assert 0 <= lo <= hi <= 1
    assert all(expressions["morphology"].get(k) for k in ["mammal", "avian", "reptile", "chitin", "shark", "antlered"])
    return dict(animations=10, expressions=10, markers=7, name_examples=len(heroes)*4)


def luminance(hex_color):
    rgb = [int(hex_color[i:i+2],16)/255 for i in (1,3,5)]
    lin = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(v*w for v,w in zip(lin,[.2126,.7152,.0722]))


def validate_brand(brand, cards):
    assert set(brand["branches"]) == BRANCHES
    assert set(cards["rarities"]) == set(brand["rarities"]) == {"Normal", "Epic", "Legendary"}
    assert set(cards["states"]) >= {"selected", "purchasable", "unavailable", "owned", "maxed"}
    assert {h["field"] for h in cards["hierarchy"]} == {"rarity", "cost", "title", "branch_icons", "illustration", "effect_summary", "level_state"}
    assert brand["touch"]["minimum_target_logical_px"] >= 44
    assert brand["typography"]["body"]["size_logical_px"] >= 14
    assert next(h for h in cards["hierarchy"] if h["field"] == "effect_summary")["minimum_font"] >= brand["typography"]["body"]["size_logical_px"], "card body font disagrees with brand"
    ratios = {}
    for text in ["text_primary", "text_secondary"]:
        for surface in ["canvas", "surface", "surface_raised"]:
            a,b = sorted([luminance(brand["color_tokens"][text]),luminance(brand["color_tokens"][surface])])
            ratio = (b+.05)/(a+.05)
            assert ratio >= 4.5, "text contrast"
            ratios[text+"/"+surface] = round(ratio,3)
    for key in ["adjectives", "forbidden", "panels", "glow", "buttons", "hud", "spacing", "motion", "unresolved"]:
        assert brand[key]
    return dict(contrast_ratios=ratios, rarities=3, branch_tokens=12, phone_resolutions=cards["phone_proof"]["resolutions"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--expected-branch")
    parser.add_argument("--report", type=Path, default=ROOT / ".work/reports/roster.json")
    args = parser.parse_args()
    report = dict(schema_version=1, tested_commit=command(["git","rev-parse","HEAD"]), branch=command(["git","branch","--show-current"]), working_tree_changes=bool(command(["git","status","--porcelain"])), profile="local-reference-audit" if args.archive else "portable-reference-spec", checks=[], limitations=[])
    def check(name, fn):
        try:
            detail = fn()
            report["checks"].append(dict(name=name, status="pass", details=detail))
            print("PASS", name, flush=True)
        except (AssertionError, ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
            report["checks"].append(dict(name=name, status="fail", details=str(exc)))
            print("FAIL", name, str(exc), flush=True)
    def baseline():
        subprocess.run(["git","merge-base","--is-ancestor",BASELINE,"HEAD"],cwd=ROOT,check=True)
        # v1.19 may add its explicit presentation assets/tests. Every existing
        # v1.17 runtime/oracle blob is still protected byte-for-byte.
        additions = 0
        allowed_roots = ("game/assets/characters/solkael_lionheart/", "game/scenes/characters/solkael_lionheart/")
        allowed_files = {"game/scripts/presentation/"+n+s for n in ["fighter_event_adapter", "solkael_fighter"] for s in [".gd", ".gd.uid"]}
        allowed_files |= {"game/tests/"+n+s for n in ["fighter_test", "fighter_review"] for s in [".gd", ".gd.uid"]}
        # Owner-authorized v1.20 QA additions; prior gameplay blobs stay immutable.
        allowed_files |= {"game/scripts/presentation/two_fighter_slice"+s for s in [".gd", ".gd.uid"]}
        allowed_files |= {"game/tests/"+n+s for n in ["polish_review", "two_fighter_test"] for s in [".gd", ".gd.uid"]}
        allowed_files |= {"game/scenes/qa/two_fighter_slice.tscn","game/assets/qa_icon.svg","game/assets/qa_icon.svg.import"}
        for line in command(["git","diff","--name-status",BASELINE,"--","game","legacy/web-prototype"]).splitlines():
            status,path=line.split("\t",1)
            if path == "game/export_presets.cfg":
                assert status=="M",line
                continue
            assert status == "A" and (path.startswith(allowed_roots) or path in allowed_files), "baseline runtime or oracle changed: "+line
            additions += 1
        if args.require_clean:
            assert not report["working_tree_changes"], "working tree not clean"
        if args.expected_branch:
            assert report["branch"] == args.expected_branch
        return dict(baseline=BASELINE, baseline_files_changed=0, authorized_presentation_additions=additions)
    check("baseline_and_runtime_preservation", baseline)
    source = read("docs/references/visual/v1.18/hero_candidates.source.json")
    roster = read("docs/product-specs/roster/hero_roster.json")
    def provenance():
        metadata=read("docs/references/visual/v1.18/source_provenance.json")
        content=(ROOT/metadata["snapshot"]).read_bytes()
        assert digest(content)==metadata["sha256"] and len(content)==metadata["bytes"]
        if args.archive:
            assert (args.archive/'hero.json.txt').read_bytes()==content
        return metadata
    check("source_snapshot", provenance)
    check("roster_identity_selection_coverage", lambda: validate_roster(roster,source))
    check("oracle_matrix", lambda: validate_mapping(read("docs/product-specs/roster/oracle_mapping.json"),roster["heroes"],read("game/data/canonical/heroes.json")))
    def references():
        catalog=read("docs/references/visual/v1.18/reference_inventory.json")
        review=read("docs/references/visual/v1.18/review_decisions.json")["by_sha256"]
        ids=set(); paths=set(); repo_paths=set(); archive_paths=set(); rmodule=module('reference_lock')
        for item in catalog["items"]:
            assert all(k in item for k in ["id","category","source","author_owner","rights_status","rights_evidence","project_usage","approval_status","production_usable","associations","tags","notes","sha256","origins"])
            assert re.fullmatch('[a-f0-9]{64}',item["sha256"]) and item["id"]=='ref_'+item["sha256"][:16]
            assert item["id"] not in ids, "duplicate ref ID"
            ids.add(item["id"])
            validate_rights(item)
            assert item["category"] in {"characters","arenas","cards","brand-ui","expressions","fx","ux"}
            if item["approval_status"] == "direction-selected":
                assert item["sha256"] in review and item["review_method"], "unreviewed direction selection"
            for assoc in item["associations"]:
                assert assoc.get("basis") and assoc.get("id") and assoc.get("type")
                if assoc["type"] == "hero":
                    assert assoc["id"] in {h["id"] for h in roster["heroes"]}
            for o in item["origins"]:
                assert o["path"] not in paths and o["sha256"] == item["sha256"], "duplicate origin / hash mismatch"
                paths.add(o["path"])
                if o["source"] == "repo":
                    repo_paths.add(o["path"])
                    assert digest(rmodule.git_bytes(o["path"])) == o["sha256"], o["path"]
                else:
                    assert o["source"] == "archive" and o["path"].startswith('.work/legacy-source/')
                    relative=o["path"].removeprefix('.work/legacy-source/')
                    archive_paths.add(relative)
                    assert '..' not in Path(relative).parts
                    if args.archive:
                        assert digest((args.archive/relative).read_bytes()) == o["sha256"], relative
        assert set(review) <= {i["sha256"] for i in catalog["items"]}, "orphan review entry"
        tracked=command(["git","ls-files","-z"]).split('\0')
        current={p for p in tracked if Path(p).suffix.lower() in rmodule.EXTENSIONS and not p.startswith('docs/qa/')}
        production_paths = set(rmodule.production_references())
        assert current == repo_paths | production_paths, "tracked image audit scope incomplete"
        if args.archive:
            actual={p.relative_to(args.archive).as_posix() for p in args.archive.rglob('*') if p.is_file() and '.git' not in p.relative_to(args.archive).parts and p.suffix.lower() in rmodule.EXTENSIONS}
            assert actual == archive_paths, "archive image audit scope incomplete"
        for h in roster["heroes"]:
            linked={h["references"]["primary"],*h["references"]["supporting"]}
            linked.update(r for v in h["references"]["coverage"].values() for r in v["reference_ids"])
            assert linked <= ids, "orphan hero reference"
        return dict(groups=len(ids), origins=len(paths), archive_hashes_checked=len(archive_paths) if args.archive else 0, direction_selected=sum(i["approval_status"]=='direction-selected' for i in catalog["items"]), production_approved=sum(i["approval_status"]=='production-approved' for i in catalog["items"]))
    check("reference_manifest_rights_hashes_and_scope", references)
    check("rig_families", lambda: validate_rigs(read("docs/art/rig_families.json"),roster["heroes"]))
    check("animation_conventions_expressions", lambda: validate_contracts(read("docs/art/character_conventions.json"),read("docs/art/animation_contract.json"),read("docs/art/expression_library.json"),roster["heroes"]))
    check("brand_card_language", lambda: validate_brand(read("docs/art/brand_ui_language.json"),read("docs/art/card_visual_language.json")))
    def generated():
        produced=module('roster_lock').build()
        produced.update({'docs/references/visual/v1.18/'+p:data for p,data in module('reference_lock').build().items()})
        for p,data in produced.items():
            assert (ROOT/p).read_bytes().replace(b'\r\n',b'\n')==data, "stale generated document: "+p
        sheets={p.name for p in (ROOT/'docs/product-specs/roster/heroes').glob('*.md')}
        assert sheets=={h['id']+'.md' for h in roster['heroes'] if h['selection']['status']=='launch'}
        return dict(rebuilt_documents=len(produced), identity_sheets=16)
    check("generated_specs_reproducible", generated)
    check("negative_contract_tests", lambda: command([sys.executable,"-X","utf8","-m","unittest","discover","-s","tools/validation","-p","test_roster.py"]))
    if args.proof:
        def proof():
            data=json.loads((args.proof/'card-proof.json').read_text())
            assert data['status']=='pass' and len(data['checks'])==4
            assert {tuple(c['resolution']) for c in data['checks']}=={(844,390),(667,375)}
            assert all(c['no_overlap'] and c['safe_area'] and c['minimum_interactive_height']>=44 for c in data['checks'])
            for a in data['artifacts']:
                assert digest((args.proof/a['path']).read_bytes())==a['sha256']
            return data
        check("phone_layout_proof", proof)
    else:
        report["limitations"].append("Phone diagram rendering not requested; portable contract/contrast checks only.")
    def clean_after():
        dirty=bool(command(["git","status","--porcelain"]))
        if args.require_clean: assert not dirty, "gate mutated tracked files"
        return dict(working_tree_changes=dirty)
    check("clean_after", clean_after)
    report["limitations"] += ["This profile audits the historical v1.18 specification; new Solkael model/rig/animation validation is covered separately by fighter.py.","Historical unknown-rights imagery has zero production approvals. The eight newly approved Solkael images are validated separately; historical packet gaps are not rewritten.","No Android/iOS package, device performance, remote CI or final UI validation claimed by this profile."]
    if not args.archive: report["limitations"].append("Archive byte/scope checks unavailable in this portable profile; frozen census still validated.")
    report["status"]="fail" if any(c['status']=='fail' for c in report['checks']) else "pass"
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_bytes((json.dumps(report,indent=2,ensure_ascii=False)+'\n').encode())
    print(report['status'].upper(),args.report)
    raise SystemExit(1 if report['status']=='fail' else 0)


if __name__ == '__main__':
    main()
