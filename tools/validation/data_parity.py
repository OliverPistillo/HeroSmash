"""Validate canonical metadata against the preserved imported source, without regeneration."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BRANCHES = "Assault Guardian Essence Rage Ice Toxin Shield Healing Power Precision Wound Dodge".split()


def validate(web: Path, archive: Path | None = None) -> dict:
    read = lambda p: json.loads(p.read_text(encoding="utf-8-sig"))
    source, cards, branches = [read(web / "data" / p) for p in ("legacy_deck_source.json", "cards.json", "branches.json")]
    assert len(source) == len(cards) == 150
    assert sorted(c["id"] for c in source) == list(range(1, 151))
    assert sorted(c["legacyId"] for c in cards) == list(range(1, 151))
    assert {b["name"] for b in branches} == set(BRANCHES)
    assert {b["id"] for b in branches} == {b.lower() for b in BRANCHES}
    by_id = {c["legacyId"]: c for c in cards}
    rarity = {"Normal":"Normale", "Epic":"Epica", "Legendary":"Leggendaria"}
    for original in source:
        c = by_id[original["id"]]
        assert c["id"] == f"legacy_{original['id']:03d}"
        assert c["name"] == original["name"]
        assert c["legacyEffect"] == c["desc"] == original["effect"]
        assert c["cost"] == original["cost"]
        assert c["rarity"] == rarity[original["rarity"]]
        assert c["legacyLevels"] == original["levels"]
        assert c["max"] == len(original["levels"])
        assert c["legacyImageCard"] == original["image_card"]
        assert c["legacyImageBackground"] == original["image_background"]
        raw = original["branch"] if isinstance(original["branch"], list) else [original["branch"]]
        normalized = [p.strip().lower().replace("guadian", "guardian") for part in raw for p in re.split("[,;]", part) if p.strip()]
        assert all(b in {x.lower() for x in BRANCHES} for b in normalized)
        assert c["branches"] == list(dict.fromkeys(normalized))
    rarity_counts = Counter(c["rarity"] for c in cards)
    combinations = Counter(len(c["branches"]) for c in cards)
    assert rarity_counts == {"Normale":90,"Epica":36,"Leggendaria":24}
    assert combinations == {1:84,2:66}
    differences = {}
    if archive is not None:
        for name in ["vecchio/deck.json", "vecchio/cards.json", "vecchio/cards_updated.json", "HeroSmash/data/legacy_deck_source.json"]:
            alternative = read(archive / name)
            assert len(alternative) == 150
            alternate_ids = {c["id"]:c for c in alternative}
            assert set(alternate_ids) == set(range(1,151))
            differences[name] = dict(Counter(k for c in source for k in c.keys() | alternate_ids[c["id"]].keys() if c.get(k) != alternate_ids[c["id"]].get(k)))
        assert differences["vecchio/deck.json"] == {"image_card":150}
        assert differences["vecchio/cards.json"] == {"image_card":150,"levels":24}
        assert differences["vecchio/cards_updated.json"] == {"image_card":150,"levels":24}
        assert differences["HeroSmash/data/legacy_deck_source.json"] == {}
        roster = read(archive / "hero.json.txt")["characters"]
        assert len(roster) == len({h["id"] for h in roster}) == 20
        aliases = {"Arcane":"Essence", "Venom":"Toxin", "Frost":"Ice"}
        assert all(aliases.get(b,b) in BRANCHES for h in roster for b in h["branches"])
    return dict(status="pass", cards=150, branches=12, rarity_counts=dict(rarity_counts),
                membership_counts=dict(combinations), alternate_source_differences=differences,
                semantics="metadata parity only; numeric effects remain legacy approximations")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web", type=Path, default=ROOT / "legacy/web-prototype")
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.web, args.archive), indent=2))
