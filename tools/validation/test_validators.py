"""Negative migration cases must fail, without altering the retained sources."""
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

from data_parity import validate as validate_data
from glb_check import validate as validate_glb

ROOT = Path(__file__).resolve().parents[2]


class ValidatorRejections(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        for name in ["cards.json", "branches.json", "legacy_deck_source.json"]:
            shutil.copyfile(ROOT / "legacy/web-prototype/data" / name, self.root / "data" / name)

    def tearDown(self):
        self.temp.cleanup()

    def mutate_card(self, edit):
        file = self.root / "data/cards.json"
        records = json.loads(file.read_text(encoding="utf-8"))
        edit(records)
        file.write_text(json.dumps(records), encoding="utf-8")
        with self.assertRaises(AssertionError):
            validate_data(self.root)

    def test_missing_card_rejected(self):
        self.mutate_card(lambda cards:cards.pop())

    def test_rewritten_effect_text_rejected(self):
        self.mutate_card(lambda cards:cards[0].update(legacyEffect="invented effect"))

    def test_unknown_branch_rejected(self):
        self.mutate_card(lambda cards:cards[0].update(branches=["thirteenth_branch"]))

    def test_changed_level_metadata_rejected(self):
        self.mutate_card(lambda cards:cards[0]["legacyLevels"][0].update(parameters={"stacks":999}))

    def test_truncated_glb_rejected(self):
        file = self.root / "sample.glb"
        file.write_bytes((ROOT / "art/exports/props/foundation_sample.glb").read_bytes()[:-4])
        with self.assertRaises(AssertionError):
            validate_glb(file)


if __name__ == "__main__":
    unittest.main()
