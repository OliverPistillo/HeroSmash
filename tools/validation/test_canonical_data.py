"""Source parity, shared malformed-data corpus and deterministic generation."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT / "tools/migration"))
import canonical_data as migration


def documents():
    return {name:migration.read(ROOT/f"game/data/canonical/{name}.json") for name in migration.DATASETS}


def malformed(base, case):
    result = copy.deepcopy(base)
    node = result[case["dataset"]]
    for key in case["path"][:-1]:
        node = node[key]
    key = case["path"][-1]
    if case["op"] == "remove": del node[key]
    elif case["op"] == "pop": node[key].pop()
    else: node[key] = case["value"]
    return result


def validate(docs):
    for name in migration.DATASETS:
        migration.schema_validate(ROOT,name,docs[name])
    migration.validate_catalog(docs)


class CanonicalDataTests(unittest.TestCase):
    def test_schema_and_full_source_parity(self):
        docs = documents()
        validate(docs)
        sources = {}
        for name, document in docs.items():
            for record in document["records"]:
                p = record["provenance"]
                source = sources.setdefault(p["source"], migration.read(ROOT/p["source"]))
                value = source
                for token in p["pointer"].strip("/").split("/") if p["pointer"] != "/" else []:
                    value = value[int(token)] if isinstance(value,list) else value[token]
                expected = record.get("legacy",record.get("values"))
                if name != "effects": self.assertEqual(expected,value)
        self.assertEqual(docs["cards"]["records"][70]["cost"],300)
        self.assertEqual(docs["cards"]["records"][70]["rarity"],"Epic")

    def test_shared_malformed_corpus(self):
        base = documents()
        cases = migration.read(ROOT/"game/tests/fixtures/canonical_cases.json")
        for case in cases:
            with self.subTest(case=case["name"]), self.assertRaises(ValueError):
                validate(malformed(base,case))

    def test_generation_repeatability_and_committed_bytes(self):
        first = migration.build()
        self.assertEqual(first,migration.build())
        for path, content in first.items():
            self.assertEqual((ROOT/path).read_bytes(),content.encode("utf-8"),path)

    def test_source_guard_and_no_partial_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock = migration.read(ROOT/"tools/migration/source_lock.json")
            paths = list(lock["files"]) + ["tools/migration/source_lock.json",migration.CONTRACTS]
            paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/"game/data/schemas").glob("*.json")]
            for path in paths:
                (root/path).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/path,root/path)
            self.assertEqual(migration.build(root),migration.build())
            target = root/migration.DATA/"legacy_deck_source.json"
            value = migration.read(target)
            value[0]["effect"] = "changed source"
            target.write_text(json.dumps(value),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"source changed"):
                migration.build(root)
            self.assertFalse((root/"game/data/canonical").exists())

    def test_only_documented_normalizations(self):
        self.assertEqual(migration.memberships(["Guadian;", " Healing,"],70),["guardian","healing"])
        for raw, cid in [(["Guadian"],1),(["Fire"],70),(["Arcane"],1),(["Toxin","Toxin"],1)]:
            with self.assertRaises(ValueError): migration.memberships(raw,cid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
