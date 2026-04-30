#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json, sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'data/arenas/arena01_beast_crucible.json'
config = json.loads(CONFIG.read_text(encoding='utf-8'))
errors = []
expected = tuple(config['sourceResolution'].values())
for layer in config['layers']:
    asset = layer.get('asset')
    if not asset: continue
    path = ROOT / asset
    if not path.exists():
        errors.append(f'Missing: {asset}')
        continue
    im = Image.open(path)
    has_alpha = im.mode == 'RGBA' or 'transparency' in im.info
    if im.size != expected:
        errors.append(f'Wrong size: {asset} {im.size}, expected {expected}')
    if layer['id'] != 'sky' and not has_alpha:
        errors.append(f'Missing alpha: {asset}')
    print(f'{asset}: {im.size} {im.mode}')

if errors:
    print('\nERRORS:')
    for e in errors: print('-', e)
    raise SystemExit(1)
print('\nOK: arena assets valid')
