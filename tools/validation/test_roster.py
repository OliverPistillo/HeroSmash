"""Adversarial changes to the data/rights/pipeline contracts must be rejected."""
import copy
import unittest

import roster as gate


class RosterContracts(unittest.TestCase):
    def setUp(self):
        self.roster = gate.read('docs/product-specs/roster/hero_roster.json')
        self.source = gate.read('docs/references/visual/v1.18/hero_candidates.source.json')

    def rejected_roster(self, mutate):
        mutate(self.roster)
        with self.assertRaises(AssertionError):
            gate.validate_roster(self.roster, self.source)

    def test_duplicate_id(self):
        self.rejected_roster(lambda d: d['heroes'][1].update(id=d['heroes'][0]['id']))

    def test_lost_reserve(self):
        self.rejected_roster(lambda d: d['heroes'].pop())

    def test_unsourced_branch(self):
        self.rejected_roster(lambda d: d['heroes'][0]['identity'].update(secondary_branch='Ice'))

    def test_unsourced_gender(self):
        self.rejected_roster(lambda d: d['heroes'][0]['identity']['gender_presentation'].update(status='defined', value='male'))

    def test_missing_view(self):
        self.rejected_roster(lambda d: d['heroes'][0]['references']['coverage'].pop('back'))

    def test_proposal_claimed_as_source(self):
        self.rejected_roster(lambda d: d['heroes'][0]['design_proposal'].update(status='source-confirmed'))

    def test_source_rewrite(self):
        self.rejected_roster(lambda d: d['heroes'][0]['source']['record'].update(personality='Invented'))

    def test_unknown_rights_rejected_for_production(self):
        item=gate.read('docs/references/visual/v1.18/reference_inventory.json')['items'][0]
        item.update(approval_status='production-approved',production_usable=True)
        with self.assertRaises(AssertionError): gate.validate_rights(item)

    def test_proprietary_rights_rejected_for_production(self):
        item=gate.read('docs/references/visual/v1.18/reference_inventory.json')['items'][0]
        for rights in ['third-party-reference-only','prohibited-for-production']:
            with self.subTest(rights=rights):
                item.update(rights_status=rights,approval_status='production-approved',production_usable=True)
                with self.assertRaises(AssertionError): gate.validate_rights(item)

    def test_licensed_flag_without_evidence_rejected(self):
        item=gate.read('docs/references/visual/v1.18/reference_inventory.json')['items'][0]
        item.update(rights_status='licensed',approval_status='production-approved',production_usable=True)
        with self.assertRaises(AssertionError): gate.validate_rights(item)

    def test_missing_oracle_cell(self):
        data=gate.read('docs/product-specs/roster/oracle_mapping.json')
        data['oracles'][0]['cells'].pop()
        with self.assertRaises(AssertionError): gate.validate_mapping(data,self.roster['heroes'],gate.read('game/data/canonical/heroes.json'))

    def test_false_exact_match(self):
        data=gate.read('docs/product-specs/roster/oracle_mapping.json')
        data['oracles'][0]['cells'][0]['rating']='exact conceptual replacement'
        with self.assertRaises(AssertionError): gate.validate_mapping(data,self.roster['heroes'],gate.read('game/data/canonical/heroes.json'))

    def test_rig_cycle(self):
        data=gate.read('docs/art/rig_families.json')
        data['families'][0]['base_hierarchy']['spine_01']='head'
        with self.assertRaises(AssertionError): gate.validate_rigs(data,self.roster['heroes'])

    def test_uncovered_launch_hero(self):
        data=gate.read('docs/art/rig_families.json')
        data['families'][0]['launch_heroes'].pop()
        with self.assertRaises(AssertionError): gate.validate_rigs(data,self.roster['heroes'])

    def test_animation_and_axes_corruption(self):
        conv=gate.read('docs/art/character_conventions.json')
        anim=gate.read('docs/art/animation_contract.json')
        expr=gate.read('docs/art/expression_library.json')
        variants=[]
        a=copy.deepcopy(anim); a['clips'][1]['loop']=True; variants.append((conv,a,expr))
        a=copy.deepcopy(anim); a['clips'][0]['name']='Idle.001'; variants.append((conv,a,expr))
        a=copy.deepcopy(anim); a['clips'][0]['root_motion']=True; variants.append((conv,a,expr))
        c=copy.deepcopy(conv); c['axes']['blender_to_godot_matrix'][2][1]=1; variants.append((c,anim,expr))
        e=copy.deepcopy(expr); e['expressions'].pop(); variants.append((conv,anim,e))
        for n,args in enumerate(variants):
            with self.subTest(corruption=n):
                with self.assertRaises(AssertionError): gate.validate_contracts(*args,self.roster['heroes'])

    def test_low_contrast_rejected(self):
        brand=gate.read('docs/art/brand_ui_language.json')
        brand['color_tokens']['text_secondary']=brand['color_tokens']['surface']
        with self.assertRaises(AssertionError): gate.validate_brand(brand,gate.read('docs/art/card_visual_language.json'))


if __name__ == '__main__':
    unittest.main()
