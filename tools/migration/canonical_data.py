"""Reproduce v1.16 canonical data. No legacy input is ever written."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
DATA = "legacy/web-prototype/data/"
CONTRACTS = "game/data/effect_contracts.json"
NAMES = "Assault Guardian Essence Rage Ice Toxin Shield Healing Power Precision Wound Dodge".split()
BRANCHES = [name.lower() for name in NAMES]
DATASETS = ("branches", "cards", "heroes", "economy", "effects")
TRIGGERS = set("combat_start basic_attack basic_hit skill_cast skill_hit damage_taken status_applied dodge heal interval combat_end".split())
ACTIONS = set("deal_damage modify_stat apply_status heal add_shield gain_energy special_handler".split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def encode(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def memberships(raw: list[str], legacy_id: int) -> list[str]:
    result = []
    for item in raw:
        for token in re.split("[,;]", item):
            name = token.strip().lower()
            if not name:
                continue
            if name == "guadian" and legacy_id == 70:
                name = "guardian"
            require(name in BRANCHES, f"card {legacy_id}: unknown branch {token!r}")
            require(name not in result, f"card {legacy_id}: repeated branch {name}")
            result.append(name)
    return result


def schema_validate(root: Path, name: str, value):
    schema = read(root / f"game/data/schemas/{name}.schema.json")
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: str(list(e.path)))
    require(not errors, f"{name}: " + "; ".join(f"/{'/'.join(map(str,e.path))}: {e.message}" for e in errors[:8]))


def validate_rule(rule: dict):
    require(rule["trigger"] in TRIGGERS, f"unsupported_trigger: {rule['trigger']}")
    interval = rule["interval_ms"]
    require((rule["trigger"] == "interval") == (interval > 0), "interval requires positive interval_ms only")
    require(rule["loss_threshold_milli"] == 0 or rule["trigger"] == "damage_taken", "loss threshold requires damage_taken")
    kinds = {"always":TRIGGERS, "critical":{"basic_hit","skill_hit"}, "regen":{"heal"},
             "status":{"status_applied"}, "reflectable":{"dodge"}}
    condition = rule["condition"]
    require(rule["trigger"] in kinds[condition["kind"]], "condition incompatible with trigger")
    require(condition["value"] in BRANCHES if condition["kind"] == "status" else condition["value"] == "", "invalid condition value")
    for action in rule["actions"]:
        kind = action["type"]
        require(kind in ACTIONS, f"unsupported_action: {kind}")
        require(action["formula"] == "flat" or kind == "heal", "formula only supported for heal")
        require(action["formula"] != "flat" or (action["factor_bp"] == action["minimum"] == 0), "unused formula fields")
        require(action["cap"] == 0 or kind == "modify_stat", "cap only supported for modify_stat")
        require(action["handler"] == ("reflect_incoming_once" if kind == "special_handler" else ""), "unsupported_handler")
        require(action["damage_kind"] in {"magic","phys","health_loss"} if kind == "deal_damage" else action["damage_kind"] == ("magic" if kind == "special_handler" else "none"), "invalid damage kind")
        if kind == "modify_stat":
            require((action["field"],action["unit"]) in {("base_damage_milli","milli"),("basic_damage_bonus_bp","basis_points")}, "unsupported stat/unit")
        elif kind in {"apply_status", "add_shield"}:
            require(action["unit"] == "stacks" and action["field"] in BRANCHES, "invalid status stacks")
            require(kind != "add_shield" or action["field"] == "shield", "add_shield requires shield")
        else:
            require(action["unit"] == "milli" and action["field"] == "", "unexpected unit/field")
        if kind == "special_handler":
            require(rule["trigger"] == "dodge" and condition["kind"] == "reflectable" and action["target"] == "opponent", "reflect handler requires eligible dodge/opponent")
            require(action["amount"] == 0, "reflection amount must come from event")


def validate_catalog(datasets: dict):
    records = {name: document["records"] for name, document in datasets.items()}
    for name, rows in records.items():
        require(len({r["id"] for r in rows}) == len(rows), f"{name}: duplicate id")
    require([r["id"] for r in records["branches"]] == BRANCHES, "canonical branch order/set")
    for branch, expected in zip(records["branches"], NAMES):
        require(branch["name"] == expected and branch["legacy"]["id"] == branch["id"] and branch["legacy"]["name"] == expected, "branch metadata mismatch")
    cards = records["cards"]
    require([c["legacyId"] for c in cards] == list(range(1,151)), "IDs must be ordered unique 1..150")
    for card in cards:
        raw = card["legacy"]
        require(card["id"] == f"legacy_{raw['id']:03d}" and card["legacyId"] == raw["id"], "legacy ID mismatch")
        for normalized, original in {"name":"name", "originalText":"effect", "rarity":"rarity", "cost":"cost"}.items():
            require(card[normalized] == raw[original], f"{card['id']}: {normalized} changed")
        require(card["branches"] == memberships(raw["branch"], raw["id"]), "branch normalization mismatch")
        require(card["maxLevel"] == len(raw["levels"]), "maxLevel mismatch")
        require([l["level"] for l in raw["levels"]] == list(range(1,card["maxLevel"]+1)), "invalid level sequence")
        require(card["maxLevel"] == {"Normal":5,"Epic":3,"Legendary":1}[card["rarity"]], "v1.15 rarity/levels mismatch")
    require(Counter(c["rarity"] for c in cards) == {"Normal":90,"Epic":36,"Legendary":24}, "rarity distribution")
    require(Counter(len(c["branches"]) for c in cards) == {1:84,2:66}, "branch membership distribution")
    for hero in records["heroes"]:
        raw = hero["legacy"]
        require(all(hero[k] == raw[k] for k in ("id","name","stats")), "hero metadata mismatch")
        require(hero["branches"] == raw["favoredBranches"] and raw["favoredBranch"] in hero["branches"], "hero branch mismatch")
    require([e["cardId"] for e in records["effects"]] == [c["id"] for c in cards], "effect coverage/order")
    for effect, card in zip(records["effects"], cards):
        require(effect["id"] == effect["cardId"], "effect identity mismatch")
        require(effect["originalTextSha256"] == text_hash(card["originalText"]), "effect text guard mismatch")
        require(bool(effect["rules"]) == (effect["lifecycle"] == "implemented"), "lifecycle/rules mismatch")
        for rule in effect["rules"]:
            validate_rule(rule)
    for name, document in datasets.items():
        sources = {s["path"]:s["sha256"] for s in document["sources"]}
        require(len(sources) == len(document["sources"]), "duplicate provenance source")
        for record in document["records"]:
            p = record["provenance"]
            require(sources.get(p["source"]) == p["sourceSha256"], f"{name}: invalid provenance reference")


def build(root: Path = ROOT) -> dict[str,str]:
    lock = read(root / "tools/migration/source_lock.json")
    for path, expected in lock["files"].items():
        require(digest(root/path) == expected, f"v1.15 source changed: {path}")
    sources = {name:read(root/DATA/(name+".json")) for name in ("legacy_deck_source","branches","heroes","economy","cards")}
    contracts = read(root/CONTRACTS)
    schema_validate(root,"effect_contracts",contracts)
    pilots = {p["legacyId"]:p for p in contracts["pilots"]}
    require(len(pilots) == 15, "duplicate pilot ID")
    for pilot in pilots.values():
        require(pilot["originalTextSha256"] == text_hash(sources["legacy_deck_source"][pilot["legacyId"]-1]["effect"]), "authored pilot text guard")

    def provenance(path, pointer):
        return dict(source=path, pointer=pointer, sourceSha256=digest(root/path))

    rows = {name:[] for name in DATASETS}
    branch_rows = {b["id"]:(i,b) for i,b in enumerate(sources["branches"])}
    for branch in BRANCHES:
        i, raw = branch_rows[branch]
        rows["branches"].append(dict(id=branch,name=raw["name"],legacy=raw,provenance=provenance(DATA+"branches.json",f"/{i}")))
    for i, raw in enumerate(sources["legacy_deck_source"]):
        cid = f"legacy_{raw['id']:03d}"
        rows["cards"].append(dict(id=cid,legacyId=raw["id"],name=raw["name"],originalText=raw["effect"],branches=memberships(raw["branch"],raw["id"]),rarity=raw["rarity"],cost=raw["cost"],maxLevel=len(raw["levels"]),legacy=raw,provenance=provenance(DATA+"legacy_deck_source.json",f"/{i}")))
        pilot = pilots.get(raw["id"])
        rows["effects"].append(dict(id=cid,cardId=cid,profile="base_text_v1",lifecycle=pilot["lifecycle"] if pilot else "unreviewed",parity=pilot["parity"] if pilot else "unresolved",reason=pilot["proposal"] if pilot else "Exact semantics not reviewed; JS branch/keyword effects are not canonical.",originalTextSha256=text_hash(raw["effect"]),rules=pilot["rules"] if pilot else [],provenance=provenance(CONTRACTS,f"/pilots/{contracts['pilots'].index(pilot)}") if pilot else provenance(DATA+"legacy_deck_source.json",f"/{i}/effect")))
    for i, raw in enumerate(sources["heroes"]):
        rows["heroes"].append(dict(id=raw["id"],name=raw["name"],role="legacy_oracle",branches=raw["favoredBranches"],stats=raw["stats"],legacy=raw,provenance=provenance(DATA+"heroes.json",f"/{i}")))
    rows["economy"].append(dict(id="legacy_economy",role="constants_only",values=sources["economy"],provenance=provenance(DATA+"economy.json","/")))
    documents = {}
    for name in DATASETS:
        paths = sorted({r["provenance"]["source"] for r in rows[name]})
        documents[name] = dict(schemaVersion=1,logicalVersion="v1.16.1",dataset=name,generator="tools/migration/canonical_data.py",sources=[dict(path=p,sha256=digest(root/p),normalization="utf8_lf") for p in paths],records=rows[name])
        schema_validate(root,name,documents[name])
    validate_catalog(documents)
    outputs = {f"game/data/canonical/{name}.json":encode(documents[name]) for name in DATASETS}
    outputs.update(reports(sources,documents,contracts,lock))
    return outputs


def reports(sources, documents, contracts, lock):
    lines = ["# v1.16 — Data comparison", "", "Generated by `tools/migration/canonical_data.py`; logical version `v1.16.1`.", "",
             f"Baseline: `{lock['baseline']}` (`v1.15-foundation`). Source hashes: `tools/migration/source_lock.json`.", "",
             "150 cards; IDs 1–150; 12 branches; 90 Normal / 36 Epic / 24 Legendary; 84 single / 66 dual branch.",
             "16 heroes remain legacy_oracle. 20 candidate concepts remain archive references pending roster approval.",
             "Economy: all 14 source fields preserved, including four branch thresholds. No shop/loss formula port.", "",
             "## Lossless mapping", "",
             "Every card source field is preserved as `legacy.<original-key>`. Added fields: stable id, legacyId, name, originalText, normalized branches, original rarity, cost, maxLevel and provenance.",
             "Only casing, delimiter/empty-token cleanup and Guadian→guardian on card 070 are normalized. Original strings remain in legacy.branch.",
             "Branch/hero raw records remain in legacy; hero normalized stats equal legacy.stats. Economy source object equals values.",
             "Provenance records source, JSON pointer and LF-normalized source SHA-256. No original wording, level parameter, path or numeric value is repaired.", "",
             "Cost exception preserved: ID 071 HEAVY BASH is Epic/cost 300; the other 35 Epic cards cost 200. Rarity is not a universal cost formula.", "",
             "## Known alternate sources (v1.15 comparison)", "",
             "vecchio/deck.json: 150 image_card differences. vecchio/cards.json and cards_updated.json: the same 150 path differences plus 24 levels differences. Nested imported source: zero differences. No alternate fields merged. Full foundation archive parity rechecks these findings.", "",
             "## Semantics coverage", "",
             "150 registry records: 135 unreviewed, 3 unresolved pilots, 12 implemented base-text contracts. Zero claims of fully resolved card progression or full-combat parity.",
             "Unresolved pilots: 097, 111, 132. Shield/Toxin/Wound physics and all numbered levels remain unresolved even for implemented contracts.", "",
             "Economy/shop lexical audit (all 150 original effects): " + str([c["id"] for c in sources["legacy_deck_source"] if re.search(r"\b(shop|gold|coin[s]?|purchase|buy|reroll|interest)\b",c["effect"],re.I)]) + ". No explicit shop/currency card was found; economy actions are reserved capabilities.", "",
             "## Per-record preservation", "", "| ID | Rarity | Cost | Max level | Branches | Raw fields |", "|---|---|---:|---:|---|---|"]
    for card in documents["cards"]["records"]:
        lines.append(f"| {card['id']} | {card['rarity']} | {card['cost']} | {card['maxLevel']} | {', '.join(card['branches'])} | equal |")
    matrix = ["# v1.16 — Pilot parity matrix", "", "Generated from guarded original texts, unchanged JS data and authored base_text_v1 proposals.", "",
              "Read ADR 0003 before execution. `implemented` refers only to this opt-in base-text profile; original levels and global status/combat physics are not defined here. No pilot is classified exact/equivalent to the entire legacy card.", "",
              "JS numeric fields below are card-level input at one copy; BranchSystem additionally combines levels and branch synergies. CombatSystem applies start stats to both units but most periodic/on-hit/heal modifiers only to the player. Treat the JS values as approximations, not target balance.", "",
              "| Card / why | Original text | Current JS | Proposed contract | Parity / lifecycle |", "|---|---|---|---|---|"]
    old = {c["legacyId"]:c for c in sources["cards"]}
    raw = {c["id"]:c for c in sources["legacy_deck_source"]}
    escape = lambda s: s.replace("|","\\|").replace("\n"," ")
    for p in contracts["pilots"]:
        n=p["legacyId"]
        cells=[f"{n:03d} {raw[n]['name']}. {p['why']}",raw[n]["effect"],p["jsNotes"]+" Input: `"+json.dumps(old[n]["effects"],sort_keys=True)+"`",p["proposal"],p["parity"]+" / "+p["lifecycle"]]
        matrix.append("| "+" | ".join(map(escape,cells))+" |")
    matrix += ["", "## Shared unresolved differences", "", "- UI shop=3; helper/probability=4. No-selling UI; latent sell API remains. Economy constants alone do not resolve these contracts.", "- preGold=0 falls through to current gold in JS. Player loss HP uses its own pre-loss streak/enemy level; bot loss uses winner streak/round.", "- Player/bot periodic effects, on-hit procs, critical opening charges and healBoost differ. New isolated operators are actor-symmetric, with explicit deterministic input ordering.", "- JS Toxin ticks are continuous dt-scaled, stacks cap at 20 and durations refresh; canonical stack application does not adopt these values without a status specification.", "- All numbered levels are rejected by the pilot runtime. Generic legacy level parameters are preserved without interpreting them as exact effect scaling."]
    return {"docs/migration/V1_16_DATA_COMPARISON.md":"\n".join(lines)+"\n", "docs/migration/V1_16_PILOT_PARITY.md":"\n".join(matrix)+"\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="dry run; reject any generated diff")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    outputs = build(args.root)
    changed = [p for p,s in outputs.items() if not (args.root/p).exists() or (args.root/p).read_bytes() != s.encode("utf-8")]
    if args.check:
        require(not changed, "generated drift: " + ", ".join(changed))
    else:
        for path in changed:
            target = args.root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(outputs[path].encode("utf-8"))
    print(json.dumps(dict(status="pass",mode="check" if args.check else "generate",outputs=len(outputs),changed=changed,cards=150,pilot_contracts=12)))


if __name__ == "__main__":
    main()
