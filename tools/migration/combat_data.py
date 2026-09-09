"""Compile v1.17 simulation inputs without altering v1.16 canonical data."""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools/migration"))
from canonical_data import read, digest, require, encode, build as canonical_build
from jsonschema import Draft202012Validator


def validate(root, name, document):
    schema=read(root/"game/data/schemas/combat.schema.json")
    schema["$ref"]="#/$defs/"+name
    Draft202012Validator.check_schema(schema)
    errors=sorted(Draft202012Validator(schema).iter_errors(document),key=lambda e:str(e.path))
    require(not errors, f"combat schema {name}: "+"; ".join(e.message for e in errors[:5]))


def integer(value, scale=1000):
    scaled=Decimal(str(value))*scale
    rounded=int(scaled.quantize(Decimal(1),rounding=ROUND_HALF_UP))
    require(abs(scaled-rounded)<Decimal("0.000001"),f"unrepresentable legacy value {value} at scale {scale}")
    return rounded


def build(root=ROOT):
    # No mutation and no escape from the previous phase's preserved-source guards.
    for path,value in canonical_build(root).items():
        require((root/path).read_bytes()==value.encode("utf-8"),f"v1.16 generated drift: {path}")
    paths=[f"game/data/canonical/{name}.json" for name in ("heroes","cards","effects")]
    paths += ["game/data/combat/ruleset.json", "game/data/combat/single_level_contracts.json", "legacy/web-prototype/data/cards.json"]
    docs={Path(p).stem:read(root/p) for p in paths[:3]}
    ruleset=read(root/paths[3])
    contracts=read(root/paths[4])
    validate(root,"ruleset",ruleset)
    validate(root,"contracts",contracts)
    oracle={c["legacyId"]:c for c in read(root/paths[5])}
    source_info=[dict(path=p,sha256=digest(root/p),normalization="utf8_lf") for p in paths]
    header=dict(schemaVersion=1,rulesetVersion=ruleset["rulesetVersion"],canonicalDataVersion=ruleset["canonicalDataVersion"],generator="tools/migration/combat_data.py",sources=source_info)
    heroes=[]
    stat_map={"hp":"max_hp_milli","atk":"attack_milli","arm":"armor_milli","focus":"focus_milli","spd":"attack_speed_milli","crit":"crit_bp","critD":"crit_multiplier_bp","regen":"energy_regen_milli","dodge":"dodge_bp"}
    for h in docs["heroes"]["records"]:
        s=h["legacy"]["skill"]
        stats={target:integer(h["stats"][source],10000 if target.endswith("_bp") else 1000) for source,target in stat_map.items()}
        skill=dict(name=s["name"],cooldown_ms=integer(s["cd"]),cost_milli=integer(s["energy"]),power_bp=integer(s["pow"],10000),damage_type="physical" if s["type"]=="phys" else "magic",status=s["status"] or "",duration_ms=integer(s["dur"]),dot_milli_per_second=integer(s["dot"]))
        heroes.append(dict(id=h["id"],stats=stats,skill=skill,provenance=h["provenance"]))
    cards={c["id"]:c for c in docs["cards"]["records"]}
    special={c["cardId"]:c for c in contracts["records"]}
    require(len(special)==len(contracts["records"]),"duplicate single-level contract")
    for key,c in special.items():
        require(key in cards and cards[key]["maxLevel"]==1,"single-level contract requires one preserved level")
        require(hashlib.sha256(cards[key]["originalText"].encode()).hexdigest()==c["originalTextSha256"],"single-level original text guard")
        require(bool(c["lethalRules"])==(key=="legacy_120"),"only LIGHTBRINGER has a specified rebirth")
    effects=[]
    for effect in docs["effects"]["records"]:
        extra=special.get(effect["id"])
        effects.append(dict(id=effect["id"],rules=effect["rules"],base_text_allowed=effect["lifecycle"]=="implemented",numbered_levels=[1] if extra else [],lethal_rules=extra["lethalRules"] if extra else [],unresolved="" if extra or effect["lifecycle"]=="implemented" else effect["reason"],source_text_hash=effect["originalTextSha256"]))
    levels=[]
    for card in cards.values():
        for raw in card["legacy"]["levels"]:
            # Exact row lookup. Oracle values are explicitly noncanonical evidence.
            values={key:float(Decimal(str(value))*raw["level"]) for key,value in oracle[card["legacyId"]]["effects"].items()}
            levels.append(dict(cardId=card["id"],level=raw["level"],maxLevel=card["maxLevel"],sourceLevel=raw,legacyOracleValues=values,canonicalNumberedExecutable=card["id"] in special,provenance=card["provenance"]))
    require(len(levels)==582,"all582 level records required")
    catalog={**header,"ruleset":ruleset,"heroes":heroes,"effects":effects}
    level_document={**header,"records":levels}
    validate(root,"catalog",catalog)
    validate(root,"levels",level_document)
    return {"game/data/generated/v1_17/combat_catalog.json":encode(catalog),"game/data/generated/v1_17/card_levels.json":encode(level_document)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    outputs=build()
    changed=[p for p,s in outputs.items() if not (ROOT/p).exists() or (ROOT/p).read_bytes()!=s.encode("utf-8")]
    if args.check: require(not changed,"generated combat drift: "+str(changed))
    else:
        for p in changed:
            (ROOT/p).parent.mkdir(parents=True,exist_ok=True)
            (ROOT/p).write_bytes(outputs[p].encode("utf-8"))
    print(json.dumps(dict(status="pass",outputs=len(outputs),changed=changed,level_records=582)))


if __name__=="__main__": main()
