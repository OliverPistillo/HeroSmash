#!/usr/bin/env python3
"""
HeroSmash v1.7 — Spritesheet Import Tool
Converte spritesheets esistenti (Aseprite JSON hash, TexturePacker) al formato canonico.

Uso:
  python3 tools/import_spritesheet.py <hero_id> <input.json> [output_dir]

Formati supportati:
  - Aseprite JSON hash (con "frameTags")
  - TexturePacker JSON hash / array
  - Formato canonico HeroSmash (pass-through)

Il mapping dei frame tag verso gli stati animazione è:
  idle, attack, skill, hit, death, victory, intro
  (tag non riconosciuti vengono ignorati)
"""
import json, sys, os, re

KNOWN_STATES = ['idle', 'attack', 'skill', 'hit', 'death', 'victory', 'intro']

# Fps default per stato
DEFAULT_FPS = {
    'idle': 7, 'attack': 14, 'skill': 10, 'hit': 12,
    'death': 8, 'victory': 8, 'intro': 10,
}
LOOP_STATES = {'idle', 'victory'}

ROW_ORDER = ['idle', 'attack', 'skill', 'hit', 'death', 'victory', 'intro']


def detect_format(data):
    if 'meta' in data and 'frameW' in data.get('meta', {}):
        return 'herosmash'
    if 'meta' in data and 'frameTags' in data.get('meta', {}):
        return 'aseprite_hash'
    if 'frames' in data and 'meta' in data:
        return 'texturepacker_hash'
    return 'unknown'


def normalize_tag_name(name):
    """Mappa un tag name verso uno stato canonico."""
    n = name.lower().strip()
    for s in KNOWN_STATES:
        if s in n:
            return s
    # Alias comuni
    alias = {'run': 'intro', 'walk': 'intro', 'cast': 'skill', 'spell': 'skill',
             'hurt': 'hit', 'damage': 'hit', 'ko': 'death', 'die': 'death',
             'win': 'victory', 'celebrate': 'victory'}
    for k, v in alias.items():
        if k in n:
            return v
    return None


def convert_aseprite_hash(data, hero_id, frame_w=None, frame_h=None):
    """Converte Aseprite JSON hash al formato canonico."""
    meta     = data['meta']
    frames   = data['frames']
    tags     = meta.get('frameTags', [])
    size     = meta.get('size', {})

    # Trova dimensioni frame (usa primo frame come riferimento)
    first_key = next(iter(frames))
    f0 = frames[first_key]['frame']
    fw = frame_w or f0['w']
    fh = frame_h or f0['h']

    # Raggruppa frame per tag
    frame_list = list(frames.values())
    anim_frames = {}
    for tag in tags:
        state = normalize_tag_name(tag['name'])
        if not state:
            print(f"  ⚠  Tag '{tag['name']}' non riconosciuto, ignorato")
            continue
        from_idx = tag['from']
        to_idx   = tag['to']
        anim_frames[state] = frame_list[from_idx:to_idx + 1]

    # Costruisce la sheet rows
    rows = {}
    for row_idx, state in enumerate(ROW_ORDER):
        if state not in anim_frames:
            print(f"  ⚠  Stato '{state}' mancante nel tag list — sarà vuoto")
            continue
        frames_in_state = anim_frames[state]
        fps = DEFAULT_FPS.get(state, 10)
        # Prova a derivare fps dalla durata del primo frame (Aseprite lo esprime in ms)
        if 'duration' in frames_in_state[0]:
            fps = max(1, round(1000 / frames_in_state[0]['duration']))
        rows[state] = {
            'row':    row_idx,
            'frames': len(frames_in_state),
            'fps':    fps,
            'loop':   state in LOOP_STATES,
        }

    manifest = {
        'meta': {
            'hero':   hero_id,
            'image':  f'assets/sprites/{hero_id}.png',
            'frameW': fw,
            'frameH': fh,
            'sheetW': int(meta['size'].get('w', fw * 8)),
            'sheetH': int(meta['size'].get('h', fh * 7)),
            'source': 'imported_aseprite',
        },
        'animations': rows,
    }
    return manifest


def convert_canonical(data, hero_id):
    """Pass-through se già in formato canonico — aggiorna solo l'hero ID."""
    data['meta']['hero'] = hero_id
    return data


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    hero_id  = sys.argv[1]
    in_json  = sys.argv[2]
    out_dir  = sys.argv[3] if len(sys.argv) > 3 else 'assets/sprites'
    os.makedirs(out_dir, exist_ok=True)

    with open(in_json) as f:
        data = json.load(f)

    fmt = detect_format(data)
    print(f"  Formato rilevato: {fmt}")

    if fmt == 'herosmash':
        manifest = convert_canonical(data, hero_id)
    elif fmt in ('aseprite_hash', 'texturepacker_hash'):
        manifest = convert_aseprite_hash(data, hero_id)
    else:
        print(f"  ❌  Formato non supportato. Adatta manualmente al formato canonico HeroSmash.")
        sys.exit(1)

    out_path = os.path.join(out_dir, f'{hero_id}.json')
    with open(out_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"  ✓  {hero_id}.json scritto in {out_dir}/")
    print(f"     Animazioni: {list(manifest['animations'].keys())}")
    print(f"\n  ⚠  Ricorda di copiare il PNG in {manifest['meta']['image']}")
    print(f"  ⚠  Poi aggiorna data/sprites_manifest.json con source='imported'")

if __name__ == '__main__':
    main()
