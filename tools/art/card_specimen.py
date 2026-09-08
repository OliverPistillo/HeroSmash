"""Render a labeled phone-scale layout diagram; does not use legacy imagery."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, required=True, help="Existing local font; never downloaded or shipped")
    parser.add_argument("--output", type=Path, default=ROOT / ".work/reports/roster-card-proof")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    language = json.loads((ROOT / "docs/art/card_visual_language.json").read_text())
    tokens = json.loads((ROOT / "docs/art/brand_ui_language.json").read_text())["color_tokens"]
    font = lambda size: ImageFont.truetype(str(args.font), size)
    report = dict(schema_version=1, status="pass", scope="Temporary geometry/text planning diagram, no production art or runtime UI", font_sha256=hashlib.sha256(args.font.read_bytes()).hexdigest(), font_name=args.font.name, checks=[], artifacts=[])
    for width, height in language["phone_proof"]["resolutions"]:
        for variant in [0, 1]:
            canvas = Image.new("RGB", (width, height), tokens["canvas"])
            draw = ImageDraw.Draw(canvas)
            boxes = []
            def text(pos, value, size, fill=tokens["text_primary"], region=None):
                # Anchor lt puts the ink box at pos regardless of font ascender metrics.
                bounds = draw.textbbox(pos, value, font=font(size), anchor="lt")
                if bounds[0] < pos[0]:
                    pos = (pos[0] + pos[0] - bounds[0], pos[1])
                    bounds = draw.textbbox(pos, value, font=font(size), anchor="lt")
                if region:
                    assert bounds[0] >= region[0] and bounds[1] >= region[1] and bounds[2] <= region[2] and bounds[3] <= region[3], (value, bounds, region)
                    boxes.append(bounds)
                draw.text(pos, value, font=font(size), fill=fill, anchor="lt")
            text((44, 12), "HERO SMASH / PROVA DI GERARCHIA", 18)
            text((44, 40), "Esempi sintetici: nessuna nuova carta o statistica", 12, tokens["text_secondary"])
            gap = 12
            card_width = (width - 88 - 2 * gap) // 3
            states = ["ACQUISTABILE", "SELEZIONATA", "NON DISPONIBILE"] if variant == 0 else ["POSSEDUTA", "MAX", "NORMALE"]
            for n, rarity in enumerate(language["rarities"]):
                x = 44 + n * (card_width + gap)
                y = 72
                right = x + card_width
                accent = tokens[rarity.lower()]
                draw.polygon([(x, y), (right - 8, y), (right, y + 8), (right, 303), (x, 303)], fill=tokens["surface"], outline=tokens["focus"] if states[n] == "SELEZIONATA" else accent, width=3 if states[n] == "SELEZIONATA" else 2)
                draw.rectangle((right-48, 76, right-4, 120), outline=accent, width=2)
                text((right-34, 86), str([2, 4, 6][n]), 20, region=(right-48, 76, right-4, 120))
                text((x+8, 84), rarity.upper(), 12, accent, (x+8, 80, right-52, 102))
                text((x+8, 124), "Carta di esempio", 14, region=(x+8, 124, right-8, 143))
                text((x+8, 142), ["A / titolo lungo", "B / doppio ramo", "C / stato chiaro"][n], 14, region=(x+8, 142, right-8, 161))
                cursor = x + 8
                for branch in [["Guardian"], ["Essence", "Wound"], ["Shield"]][n]:
                    # Original labeled icon placeholders; final branch glyphs are unresolved.
                    draw.ellipse((cursor, 162, cursor+20, 182), outline=tokens["border"], width=1)
                    text((cursor+6, 166), branch[0], 10, region=(cursor, 162, cursor+20, 182))
                    text((cursor+24, 165), branch, 12, tokens["text_secondary"], (cursor+24, 163, right-8, 183))
                    cursor += 24 + int(draw.textlength(branch, font=font(12))) + 8
                draw.rectangle((x+8, 186, right-8, 236), fill=tokens["surface_raised"])
                center = (x+right)//2
                draw.polygon([(center, 192), (center+16, 211), (center, 230), (center-16, 211)], outline=accent, width=2)
                text((x+8, 242), "Riepilogo effetto", 13, region=(x+8, 240, right-8, 261))
                text((x+8, 258), "Dettagli: tocca carta", 13, tokens["text_secondary"], (x+8, 258, right-8, 278))
                # Short display labels retain full meaning in the inspection flow.
                short = {"ACQUISTABILE":"PRONTA", "SELEZIONATA":"SCELTA", "NON DISPONIBILE":"BLOCCATA", "POSSEDUTA":"OWNED", "MAX":"MAX", "NORMALE":"NORMALE"}[states[n]]
                text((x+8, 286), short, 12, tokens["text_secondary"], (x+8, 283, right-66, 300))
                level = "Lv 3/3" if states[n] == "MAX" else ["Lv 1/5", "Lv 2/3", "Lv 1/1"][n]
                text((right-57, 286), level, 12, region=(right-60, 283, right-5, 300))
            button = (width-204, 319, width-44, 363)
            draw.rectangle(button, fill=tokens["accent_gold"])
            text((width-182, 333), "ISPEZIONA", 16, tokens["canvas"])
            text((44, 322), "PROPOSTA / NON UI FINALE", 12, tokens["text_secondary"])
            text((44, 342), "3 carte; target azione 44 px", 12, tokens["text_secondary"])
            assert button[3] <= height-8
            for i, a in enumerate(boxes):
                for b in boxes[i+1:]:
                    assert not (a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]), (a,b)
            name=f"card-proof-{width}x{height}-{variant}.png"
            path=args.output/name
            canvas.save(path)
            report["checks"].append(dict(resolution=[width,height],variant=variant,states=states,text_regions=len(boxes),no_overlap=True,safe_area=True,minimum_interactive_height=44))
            report["artifacts"].append(dict(path=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (args.output/'card-proof.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(f"PASS: four phone diagrams, bounded text, no overlap; {args.output}")


if __name__ == '__main__':
    main()
