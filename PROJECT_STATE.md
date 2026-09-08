# Hero Smash — Project State

**State date:** 2026-09-08  
**Macro phase:** v1.15 Revival/Foundation  
**Phase status:** READY TO START  
**Intended branch:** `revival/v1.15-foundation`  
**GitHub baseline:** `main` @ `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

## 1. Current repository reality

The GitHub repository currently contains the later **v1.14.3 JavaScript/Canvas custom-engine prototype**, not the original Godot runtime.

Known implemented areas in that prototype:
- mobile landscape home;
- active/banned branch generation;
- hero draft;
- market;
- economy;
- 8-player bot league;
- automatic combat;
- combat readability/HUD;
- round recap;
- 2.5D arena presentation;
- local save;
- asset pipeline;
- 150-card legacy import.

This prototype is now classified as:
- gameplay reference;
- UX reference;
- data migration source;
- behavior oracle where tests do not yet exist.

It is not the final production runtime.

## 2. Uploaded legacy archive reality

User-provided source archive corresponds to the old local Hero Smash material.

Inventory observed:
- 299 files;
- 243 PNG;
- 41 WebP;
- 10 `.import`;
- 3 JSON;
- 1 TXT;
- 1 JPEG;
- no `.gd`;
- no `.tscn`;
- no `project.godot`.

Important archive groups include:
- arena layered artwork;
- card frames;
- branch icons;
- sprite/reference sheets;
- newer anthropomorphic hero definitions;
- old `deck.json`;
- 150 card images;
- old level/frame assets;
- style/UI/art-bible reference images.

Conclusion:
the archive is primarily an **asset/data/reference source**, not a bootable Godot project.

## 3. New production decision

Locked:
- Godot 4.7.2 stable;
- typed GDScript;
- Blender 5.2 LTS;
- real-time 3D characters;
- 2.5D hybrid arenas;
- Android/iOS landscape first.

Reason:
the requirement for true real-time 3D fighters makes the current Canvas runtime the wrong production renderer, while Godot provides a much cleaner mobile 3D runtime and automation/headless path.

## 4. Data that must survive migration

Must preserve until explicitly revised:
- 12 canonical branches;
- 8 active / 4 banned run rule;
- 150 legacy card identities and IDs;
- original legacy effect text;
- rarity/cost/level metadata;
- current market/economy behavior until verified;
- bot league behavior as baseline;
- hero draft flow;
- direct market → combat → market loop.

## 5. Candidate hero roster source

The archive contains a 20-character anthropomorphic roster including:
- Solkael Lionheart;
- Fenrox Bloodhowl;
- Kitsara Moonveil;
- Aethryon Stormwing;
- Brumgar Earthhide;
- Sylvex Venomkiss;
- Rajuro Strikefang;
- Morvayne Blackquill;
- Karchar Reefbreaker;
- Elunor Lifethorn;
- Gruttar Tuskgold;
- Nyxara Nightstep;
- Oromir Frostclock;
- Rhazgor Crystalhorn;
- Zelkara Jadeclaw;
- Vulkaryn Emberlord;
- Kongaru Ironpalm;
- Lupika Swiftkick;
- Tortugan Runewarden;
- Skarvex Stinglash.

Experimental aliases in that file must normalize:
- Arcane → Essence;
- Venom → Toxin;
- Frost → Ice.

Final roster approval is deferred to its dedicated macro phase.

## 6. Foundation blockers / notes

- The connected GitHub integration can read the repository, but branch/issue creation returned HTTP 403 during bootstrap preparation.
- Therefore `main` was intentionally left untouched.
- The revival branch should be created locally from a fresh clone and pushed only after review.

## 7. v1.15 completion checklist

- [ ] Fresh clone exists at `D:\Dev\HeroSmash`.
- [ ] Local `revival/v1.15-foundation` branch exists.
- [ ] Foundation docs committed.
- [ ] Current repo files fully inventoried.
- [ ] Legacy ZIP/folder fully inventoried.
- [ ] Duplicate assets classified.
- [ ] Authoritative data sources identified.
- [ ] Proposed final repo tree approved.
- [ ] Current JS runtime isolated as legacy/reference without losing history.
- [ ] Minimal Godot project created and validated headlessly.
- [ ] Godot Mobile renderer selected and smoke-tested.
- [ ] Blender → GLB → Godot sample pipeline validated.
- [ ] Reference library created and indexed.
- [ ] Test/CI skeleton created.
- [ ] Migration report generated.
- [ ] `PROJECT_STATE.md` updated with final v1.15 commit and v1.16 start point.

## 8. Next macro phase

After v1.15:
**v1.16 — Canonical Data Migration + Exact Card Semantics Framework**.

Do not begin v1.16 until v1.15 has an inventory report and reproducible Godot bootstrap.
