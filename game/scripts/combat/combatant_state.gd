class_name CombatantState
extends RefCounted

var id: String
var hero_id: String
var stats: Dictionary
var skill: Dictionary
var hp_milli: int
var energy_milli: int
var energy_remainder: int = 0
var basic_remaining: int = 0
var skill_remaining: int = 0
var basic_bonus_bp: int = 0
var alive: bool = true
var generation: int = 0
var prevention_charges: int
var prevention_hp: int
var rebirth_charges: int = 0
var rebirth_hp_bp: int = 0
var statuses: Array[StatusInstance] = []
var bindings: Array[Dictionary] = []
var status_templates: Dictionary
var metrics: Dictionary = {}

func _init(record: Dictionary) -> void:
	id = record["id"]
	hero_id = record["heroId"]
	stats = record["stats"].duplicate(true)
	skill = record["skill"].duplicate(true)
	hp_milli = int(record["hp_milli"])
	energy_milli = int(record["energy_milli"])
	prevention_charges = int(record["death_prevention"]["charges"])
	prevention_hp = int(record["death_prevention"]["surviving_hp_milli"])
	status_templates = record["status_templates"].duplicate(true)
	for key: String in ["physical_damage_milli", "magic_damage_milli", "dot_damage_milli", "damage_taken_milli", "healing_milli", "shield_generated_milli", "shield_absorbed_milli", "crit_count", "crit_attempts", "dodge_count", "dodge_attempts", "skill_casts", "basic_attacks", "status_applications", "death_prevention_count", "rebirth_count", "ko_count"]:
		metrics[key] = 0
	metrics["lethal_source"] = ""
	metrics["status_uptime_ms"] = {}

func snapshot(now: int) -> Dictionary:
	var status_rows: Array[Dictionary] = []
	for status: StatusInstance in statuses: status_rows.append(status.snapshot(now))
	return {"id":id, "heroId":hero_id, "stats":stats.duplicate(true), "skill":skill.duplicate(true), "hp_milli":hp_milli, "energy_milli":energy_milli, "energy_remainder":energy_remainder, "basic_remaining":basic_remaining, "skill_remaining":skill_remaining, "basic_bonus_bp":basic_bonus_bp, "alive":alive, "generation":generation, "prevention_charges":prevention_charges, "rebirth_charges":rebirth_charges, "statuses":status_rows, "bindings":bindings.duplicate(true), "metrics":metrics.duplicate(true)}
