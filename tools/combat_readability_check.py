#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
combat = (ROOT / "src/game/CombatSystem.js").read_text(encoding="utf-8")
scene = (ROOT / "src/scenes/CombatScene.js").read_text(encoding="utf-8")

checks = {
    "recap_physical": "physical" in combat,
    "recap_magic": "magic" in combat,
    "recap_dot": "dot" in combat,
    "status_icons": "STATUS_ICONS" in scene,
    "combat_log": "drawEventLog" in scene,
    "skill_ready": "SKILL READY" in combat + scene,
    "help_overlay": "drawLegend" in scene,
    "shielded": "shielded" in combat + scene,
}
for k, v in checks.items():
    print(f"{k}: {'OK' if v else 'MISSING'}")
if not all(checks.values()):
    raise SystemExit(1)
