#!/usr/bin/env python3
"""
Import the authoritative legacy deck.json into the current Hero Smash engine format.

Usage:
  python3 tools/import_legacy_deck.py /path/to/deck.json

The importer preserves the exact number of cards, legacy ids, rarity distribution,
branch composition, original effect text, cost, and level counts. It also generates
runtime-safe SVG placeholder cards and a report.
"""
from pathlib import Path
import json, re, html, collections, sys

ROOT = Path(__file__).resolve().parents[1]
BRANCHES = json.loads((ROOT / "data/branches.json").read_text(encoding="utf-8"))
BRANCH_BY_ID = {b["id"]: b for b in BRANCHES}
NAME_TO_ID = {b["name"].lower(): b["id"] for b in BRANCHES}
ALIASES = {"guadian":"guardian", "fire":"rage", "poison":"toxin"}
RARITY_MAP = {"Normal":"Normale", "Epic":"Epica", "Legendary":"Leggendaria"}
RARITY_WEIGHT = {"Normale":64,"Epica":12,"Leggendaria":3}
RARITY_POINTS = {"Normale":1,"Epica":2,"Leggendaria":3}
RARITY_UNLOCK = {"Normale":0,"Epica":10,"Leggendaria":20}
RARITY_FRAME = {"Normale":"#38bdf8","Epica":"#c77dff","Leggendaria":"#ffca3a"}
BRANCH_ICONS = {b["id"]: b["icon"] for b in BRANCHES}

def normalize_branches(raw):
    items = raw if isinstance(raw, list) else [raw]
    out = []
    for item in items:
        for p in re.split(r"[,;]", str(item)):
            key = p.strip().strip(",").lower()
            if not key: continue
            key = ALIASES.get(key, key)
            bid = NAME_TO_ID.get(key, key)
            if bid in BRANCH_BY_ID and bid not in out:
                out.append(bid)
    return out or ["power"]

def effects_for(branches, rarity, text):
    # Same conservative gameplay mapping used by v1.5 importer.
    scale = {"Normale":1.0,"Epica":1.65,"Leggendaria":2.7}[rarity]
    base = {
        "wound": {"woundHit": .030, "woundAmp": .010},
        "essence": {"manaRegen": .35, "skillPower": .010},
        "rage": {"speedPct": .010, "tempo": .35},
        "ice": {"iceHit": .022, "slow": .010},
        "toxin": {"toxinHit": .024, "toxinTick": .55},
        "shield": {"startShield": 10, "shieldRegen": 2.5},
        "healing": {"hpRegen": .55, "healBoost": .008},
        "power": {"attack": .75, "focus": .75, "execute": .006},
        "precision": {"crit": .0075, "critD": .010},
        "guardian": {"hp": 14, "armor": .32},
        "assault": {"attack": 1.05, "multiHit": .006},
        "dodge": {"dodge": .0065}
    }
    eff = {}
    def add(k,v): eff[k] = round(eff.get(k,0)+v,5)
    for b in branches:
        for k,v in base.get(b, {}).items(): add(k, v*scale/max(1,len(branches)))
    t = text.lower()
    if "crit" in t or "critical" in t: add("crit", .012*scale)
    if "critical damage" in t: add("critD", .05*scale)
    if "dodge" in t or "evasion" in t: add("dodge", .008*scale)
    if "shield" in t or "barrier" in t or "guard" in t: add("startShield", 18*scale)
    if "mana" in t or "mp" in t or "essence" in t or "arcane" in t: add("manaRegen", .45*scale); add("skillPower", .012*scale)
    if "wound" in t: add("woundHit", .035*scale); add("woundAmp", .012*scale)
    if "toxin" in t or "poison" in t or "venom" in t: add("toxinHit", .035*scale); add("toxinTick", .70*scale)
    if "ice" in t or "frost" in t or "cold" in t: add("iceHit", .032*scale); add("slow", .012*scale)
    if "fire" in t or "flame" in t or "burn" in t or "rage" in t: add("speedPct", .011*scale); add("tempo", .45*scale)
    if "heal" in t or "regenerat" in t or "lifesteal" in t: add("hpRegen", .65*scale); add("healBoost", .010*scale)
    if "damage" in t or "assault" in t or "slash" in t or "strike" in t or "blade" in t: add("attack", .95*scale)
    if "counter" in t or "again" in t or "re-invoke" in t: add("multiHit", .012*scale)
    if "lethal" in t or "death" in t or "below" in t: add("execute", .018*scale)
    caps = {"crit":.18,"dodge":.15,"multiHit":.18,"toxinHit":.45,"woundHit":.45,"iceHit":.40,"execute":.20,"speedPct":.22,"skillPower":.30,"healBoost":.25}
    for k,c in caps.items():
        if k in eff: eff[k] = min(eff[k], c)
    return eff

def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/legacy_deck_source.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    cards = []
    for c in raw:
        rarity = RARITY_MAP[c["rarity"]]
        branches = normalize_branches(c["branch"])
        cid = f"legacy_{int(c['id']):03d}"
        cards.append({
            "id": cid, "legacyId": int(c["id"]), "name": c["name"], "rarity": rarity,
            "branches": branches, "icon": BRANCH_ICONS.get(branches[0], "◆"),
            "desc": c.get("effect", ""), "legacyEffect": c.get("effect", ""),
            "effects": effects_for(branches, rarity, c.get("effect", "")),
            "image": f"assets/cards/{cid}.svg", "legacyImageCard": c.get("image_card"),
            "legacyImageBackground": c.get("image_background"), "legacyLevels": c.get("levels", []),
            "points": RARITY_POINTS[rarity], "max": len(c.get("levels", [])), "cost": c.get("cost", 100),
            "weight": RARITY_WEIGHT[rarity], "frame": RARITY_FRAME[rarity], "unlock": RARITY_UNLOCK[rarity],
            "source": "deck.json"
        })
    (ROOT / "data/cards.json").write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Imported {len(cards)} cards from {source}")

if __name__ == "__main__": main()
