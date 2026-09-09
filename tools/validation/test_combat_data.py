"""Versioned schema, source parity and measurement aggregation checks for v1.17."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/migration'))
sys.path.insert(0,str(ROOT/'tools/balance_lab'))
import combat_data as migration
import run as lab

class CombatDataTests(unittest.TestCase):
    def test_exact_generation_and_all_source_levels(self):
        first=migration.build()
        self.assertEqual(first,migration.build())
        for path,text in first.items():self.assertEqual((ROOT/path).read_bytes(),text.encode())
        levels=json.loads(first['game/data/generated/v1_17/card_levels.json'])['records']
        cards={c['id']:c for c in migration.read(ROOT/'game/data/canonical/cards.json')['records']}
        self.assertEqual(len(levels),582)
        self.assertEqual(sum(r['canonicalNumberedExecutable'] for r in levels),3)
        for row in levels:
            card=cards[row['cardId']]
            self.assertEqual(row['sourceLevel'],card['legacy']['levels'][row['level']-1])
            self.assertEqual(row['maxLevel'],card['maxLevel'])
        self.assertEqual(cards['legacy_071']['cost'],300)

    def test_only_unit_normalization(self):
        self.assertEqual(migration.integer(.09000000000000001,10000),900)
        with self.assertRaisesRegex(ValueError,'unrepresentable'):migration.integer(.12345)
        heroes=migration.read(ROOT/'game/data/generated/v1_17/combat_catalog.json')['heroes']
        original={r['id']:r['stats'] for r in migration.read(ROOT/'game/data/canonical/heroes.json')['records']}
        for hero in heroes:
            self.assertEqual(hero['stats']['max_hp_milli'],migration.integer(original[hero['id']]['hp']))
            self.assertEqual(hero['stats']['energy_regen_milli'],migration.integer(original[hero['id']]['regen']))

    def test_malformed_versioned_schemas(self):
        catalog=migration.read(ROOT/'game/data/generated/v1_17/combat_catalog.json')
        for path,value in [(['schemaVersion'],2),(['heroes'],None),(['heroes'],catalog['heroes'][:-1]),(['heroes',0,'stats','max_hp_milli'],-1),(['effects',119,'lethal_rules',0,'restore_hp_bp'],9999),(['effects',0,'numbered_levels'],[2]),(['ruleset','clockUnit'],'frame_delta')]:
            broken=copy.deepcopy(catalog);node=broken
            for key in path[:-1]:node=node[key]
            node[path[-1]]=value
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,'combat schema'):migration.validate(ROOT,'catalog',broken)
        contracts=migration.read(ROOT/'game/data/combat/single_level_contracts.json')
        contracts['records'][0]['cardId']='legacy_111'
        with self.assertRaises(ValueError):migration.validate(ROOT,'contracts',contracts)

    def test_aggregate_quantiles_and_hash_excludes_only_runtime(self):
        self.assertEqual(lab.distribution(list(range(1,101))),dict(mean=50.5,median=50.5,p90=90,p99=99,minimum=1,maximum=100))
        document={'records':[{'seed':1,'resultHash':'a','runtime_us':1}]}
        digest=lab.deterministic_digest(document)
        document['records'][0]['runtime_us']=100
        self.assertEqual(digest,lab.deterministic_digest(document))
        document['records'][0]['resultHash']='b'
        self.assertNotEqual(digest,lab.deterministic_digest(document))

    def test_scenario_manifest_scope_and_coverage(self):
        scenarios=migration.read(ROOT/'game/data/combat/scenarios.json')
        rows=scenarios['records']
        self.assertEqual(len({r['id'] for r in rows}),12)
        self.assertEqual(scenarios['seedCorpus'],dict(first=0,count=1000))
        self.assertEqual(rows[-1]['mirrorOf'],rows[-2]['id'])
        for row in rows[:-1]:
            self.assertEqual(set(row),{'id','description','heroes','cards','initial','templates','prevention'})
            for key in ('heroes','cards','initial','templates','prevention'):self.assertEqual(len(row[key]),2)
        for value in scenarios['statusFixtures'].values():self.assertEqual(value['metadata']['origin'],'mechanics_fixture')

if __name__=='__main__':unittest.main(verbosity=2)
