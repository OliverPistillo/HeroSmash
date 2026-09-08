class_name EffectActorState
extends RefCounted
## Bounded ledger for the pilot. Status physics/damage resolution live elsewhere.

var max_hp_milli: int = 1000000
var hp_milli: int = 1000000
var energy_milli: int = 0
var base_damage_milli: int = 20000
var basic_damage_bonus_bp: int = 0
var statuses: Dictionary[String, int] = {}

func snapshot() -> Dictionary:
	return {"max_hp_milli":max_hp_milli, "hp_milli":hp_milli, "energy_milli":energy_milli, "base_damage_milli":base_damage_milli, "basic_damage_bonus_bp":basic_damage_bonus_bp, "statuses":statuses.duplicate()}

func copy_state() -> EffectActorState:
	var result: EffectActorState = EffectActorState.new()
	result.max_hp_milli = max_hp_milli
	result.hp_milli = hp_milli
	result.energy_milli = energy_milli
	result.base_damage_milli = base_damage_milli
	result.basic_damage_bonus_bp = basic_damage_bonus_bp
	result.statuses = statuses.duplicate()
	return result
