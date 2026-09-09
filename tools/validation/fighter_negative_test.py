"""Corrupt real GLB copies to exercise independent asset-admission failure paths."""
from pathlib import Path
import copy
import json
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/asset_pipeline'))
from fighter_glb import GLB,validate


class FighterNegativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=ROOT/'game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v001.glb'
        cls.glb=GLB(cls.source)

    def reject(self,mutate):
        doc=copy.deepcopy(self.glb.doc);binary=bytearray(self.glb.binary)
        mutate(doc,binary)
        data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
        raw=struct.pack('<4sII',b'glTF',2,28+len(data)+len(binary))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(binary),0x004e4942)+binary
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'corrupt.glb';path.write_bytes(raw)
            with self.assertRaises((AssertionError,ValueError,KeyError,IndexError,struct.error)):
                validate(path)

    def test_valid_control(self):self.assertEqual(validate(self.source)['status'],'pass')
    def test_external_buffer(self):self.reject(lambda d,b:d['buffers'][0].update(uri='outside.bin'))
    def test_truncated_view(self):self.reject(lambda d,b:d['bufferViews'][0].update(byteLength=len(b)+100))
    def test_material_naming(self):self.reject(lambda d,b:d['materials'][0].update(name='Material.001'))
    def test_blended_fur(self):self.reject(lambda d,b:d['materials'][0].update(alphaMode='BLEND'))
    def test_unapproved_texture_dependency(self):self.reject(lambda d,b:d.update(images=[{'uri':'legacy.png'}]))
    def test_duplicate_bone(self):self.reject(lambda d,b:d['nodes'][1].update(name=d['nodes'][0]['name']))
    def test_negative_object_scale(self):self.reject(lambda d,b:d['nodes'][0].update(scale=[-1,1,1]))
    def test_missing_clip(self):self.reject(lambda d,b:d['animations'].pop())
    def test_missing_expression(self):self.reject(lambda d,b:d['meshes'][0]['extras']['targetNames'].pop())
    def test_non_neutral_face(self):self.reject(lambda d,b:d['meshes'][0].update(weights=[1]*9))
    def test_invalid_joint(self):self.reject(lambda d,b:d['skins'][0]['joints'].append(999999))

    @staticmethod
    def write_component(doc,binary,accessor,value,component=0):
        a=doc['accessors'][accessor];v=doc['bufferViews'][a['bufferView']]
        assert a['componentType']==5126
        struct.pack_into('<f',binary,v.get('byteOffset',0)+a.get('byteOffset',0)+component*4,value)

    def test_invalid_weights(self):
        self.reject(lambda d,b:self.write_component(d,b,d['meshes'][0]['primitives'][0]['attributes']['WEIGHTS_0'],2.0))
    def test_below_floor_geometry(self):
        self.reject(lambda d,b:self.write_component(d,b,d['meshes'][0]['primitives'][0]['attributes']['POSITION'],-2.0,1))
    def test_nan_position(self):
        self.reject(lambda d,b:self.write_component(d,b,d['meshes'][0]['primitives'][0]['attributes']['POSITION'],float('nan')))
    def test_bad_sparse_count(self):
        def mutate(d,b):
            a=next(a for a in d['accessors'] if 'sparse' in a);a['sparse']['count']=a['count']+1
        self.reject(mutate)
    def test_accumulated_face_morph(self):
        def mutate(d,b):
            a=next(d['accessors'][t['POSITION']] for p in d['meshes'][0]['primitives'] for t in p['targets'] if 'sparse' in d['accessors'][t['POSITION']])
            part=a['sparse']['values'];view=d['bufferViews'][part['bufferView']]
            struct.pack_into('<f',b,view.get('byteOffset',0)+part.get('byteOffset',0),3.0)
        self.reject(mutate)


if __name__=='__main__':unittest.main()
