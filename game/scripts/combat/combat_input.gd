class_name CombatInput
extends RefCounted
## Fail closed at the public boundary; fixture overrides are explicit, never implicit.

const STATUS_TYPES: Array[String] = ["shield", "toxin", "burn", "wound", "ice", "stun"]
const POLICIES: Array[String] = ["replace", "refresh_duration", "add_stack", "add_stack_and_refresh", "independent_instances", "stronger_wins"]
var errors: Array[String] = []

func check(input: Variant, catalog: CombatCatalog) -> bool:
	errors.clear()
	if not input is Dictionary:
		errors.append("input_not_object")
		return false
	if not keys(input, ["scenarioId", "rulesetVersion", "canonicalDataVersion", "seed", "horizon_ms", "combatants", "sides"]): return false
	if not input.get("rulesetVersion") is String or not input.get("canonicalDataVersion") is String:
		errors.append("version_type_invalid")
	elif input["rulesetVersion"] != CombatCatalog.RULESET_VERSION or input["canonicalDataVersion"] != CombatCatalog.DATA_VERSION: errors.append("version_mismatch")
	if not label(input.get("scenarioId")): errors.append("scenario_id_invalid")
	if not CombatJson.integer(input.get("seed"), 0, 4294967295): errors.append("seed_invalid")
	if not CombatJson.integer(input.get("horizon_ms"), 1, 45000): errors.append("horizon_invalid")
	if not input.get("combatants") is Array or input["combatants"].size() != 2:
		errors.append("exactly_two_combatants_required")
		return false
	var ids: Array[String] = []
	for record: Variant in input["combatants"]:
		if not record is Dictionary:
			errors.append("combatant_not_object")
			continue
		check_actor(record, catalog)
		if record.get("id") is String:
			if record["id"] in ids: errors.append("duplicate_identity")
			ids.append(record["id"])
	if not input.get("sides") is Array or input["sides"].size() != 2 or not input["sides"][0] is String or not input["sides"][1] is String or input["sides"][0] == input["sides"][1]:
		errors.append("invalid_presentation_sides")
	else:
		for side: Variant in input["sides"]:
			if not side in ids: errors.append("unknown_side_identity")
	for record: Variant in input["combatants"]:
		if record is Dictionary and record.get("initial_statuses") is Array:
			for status: Variant in record["initial_statuses"]:
				if status is Dictionary and not status.get("source") in ids: errors.append("unknown_status_source")
	return errors.is_empty()

func check_actor(record: Dictionary, catalog: CombatCatalog) -> void:
	if not keys(record, ["id", "heroId", "origin", "stats", "skill", "hp_milli", "energy_milli", "bindings", "initial_statuses", "status_templates", "death_prevention"]): return
	if not label(record.get("id")): errors.append("invalid_actor_id")
	if not record.get("heroId") is String or catalog.hero(str(record.get("heroId"))).is_empty():
		errors.append("unknown_hero")
		return
	if not record.get("origin") in ["canonical_hero", "unit_fixture"]: errors.append("unlabeled_actor_origin")
	if not record.get("stats") is Dictionary or not record.get("skill") is Dictionary:
		errors.append("invalid_stats_or_skill")
		return
	var stats: Dictionary = record["stats"]
	var skill: Dictionary = record["skill"]
	var original: Dictionary = catalog.hero(record["heroId"])
	if record["origin"] == "canonical_hero" and (stats != original["stats"] or skill != original["skill"]): errors.append("canonical_hero_modified")
	if not keys(stats, ["max_hp_milli", "attack_milli", "armor_milli", "focus_milli", "attack_speed_milli", "crit_bp", "crit_multiplier_bp", "energy_regen_milli", "dodge_bp"]): return
	for key: String in stats:
		var maximum: int = 10000000
		if key == "max_hp_milli": maximum = 1000000000
		elif key.ends_with("_bp"): maximum = 10000 if key != "crit_multiplier_bp" else 100000
		elif key == "attack_speed_milli": maximum = 10000
		if not CombatJson.integer(stats[key], 1 if key in ["max_hp_milli", "attack_speed_milli"] else 0, maximum): errors.append("invalid_stat:" + key)
	if not errors.is_empty(): return
	if not keys(skill, ["name", "cooldown_ms", "cost_milli", "power_bp", "damage_type", "status", "duration_ms", "dot_milli_per_second"]): return
	if not label(skill.get("name")) or not skill.get("damage_type") in ["physical", "magic"] or not skill.get("status") in ["", "toxin", "burn", "wound", "ice", "stun"]: errors.append("invalid_skill_kind")
	for key: String in ["cooldown_ms", "cost_milli", "power_bp", "duration_ms", "dot_milli_per_second"]:
		if not CombatJson.integer(skill.get(key), 1 if key in ["cooldown_ms", "duration_ms"] else 0, 45000 if key.ends_with("_ms") else 100000): errors.append("invalid_skill_value:" + key)
	if not CombatJson.integer(record.get("hp_milli"), 1, int(stats.get("max_hp_milli", 0))): errors.append("invalid_initial_hp")
	if not CombatJson.integer(record.get("energy_milli"), 0, 100000): errors.append("invalid_initial_energy")
	var prevention: Variant = record.get("death_prevention")
	if not prevention is Dictionary or not keys(prevention, ["charges", "surviving_hp_milli", "origin"]):
		errors.append("invalid_prevention")
	elif not CombatJson.integer(prevention.get("charges"), 0, 10) or not CombatJson.integer(prevention.get("surviving_hp_milli"), 0, int(stats.get("max_hp_milli", 0))):
		errors.append("invalid_prevention_values")
	elif prevention["charges"] > 0 and (prevention["surviving_hp_milli"] <= 0 or prevention.get("origin") != "mechanics_fixture"):
		errors.append("prevention_requires_explicit_fixture")
	if not record.get("status_templates") is Dictionary or record["status_templates"].size() > 6:
		errors.append("invalid_status_templates")
		return
	for kind: String in record["status_templates"]:
		var template: Variant = record["status_templates"][kind]
		check_status(template, false)
		if template is Dictionary and template.get("type") != kind: errors.append("template_type_mismatch")
	if not record.get("initial_statuses") is Array or record["initial_statuses"].size() > 32:
		errors.append("invalid_initial_statuses")
	else:
		for status: Variant in record["initial_statuses"]: check_status(status, true)
	if not record.get("bindings") is Array or record["bindings"].size() > 16:
		errors.append("invalid_bindings")
		return
	var seen: Dictionary = {}
	for binding: Variant in record["bindings"]:
		if not binding is Dictionary or not keys(binding, ["cardId", "profile", "level"]):
			errors.append("invalid_binding")
			continue
		if not binding.get("cardId") is String or not binding.get("profile") is String or not CombatJson.integer(binding.get("level"), 0, 5):
			errors.append("invalid_binding_identity_or_level")
			continue
		var effect: Dictionary = catalog.effect(binding["cardId"])
		if effect.is_empty() or seen.has(binding["cardId"]):
			errors.append("unknown_or_duplicate_card")
			continue
		seen[binding["cardId"]] = true
		if binding["profile"] == "numbered":
			if not binding["level"] in effect["numbered_levels"]: errors.append("unresolved_numbered_effect_binding:" + binding["cardId"])
		elif binding["profile"] == "base_text_v1":
			if binding["level"] != 0 or not effect["base_text_allowed"]: errors.append("unresolved_literal_binding:" + binding["cardId"])
		else: errors.append("unknown_execution_profile")
		for rule: Dictionary in effect["rules"]:
			for action: Dictionary in rule["actions"]:
				if action["type"] in ["add_shield", "apply_status"] and not record["status_templates"].has(action["field"]): errors.append("missing_explicit_status_parameters:" + action["field"])

func check_status(value: Variant, initial: bool) -> bool:
	var before: int = errors.size()
	if not value is Dictionary:
		errors.append("status_not_object")
		return false
	var fields: Array[String] = ["type", "duration_ms", "stacks", "max_stacks", "magnitude", "stacking_policy", "refresh_policy", "interval_ms", "debuff", "metadata"]
	if initial: fields.append("source")
	if not keys(value, fields): return false
	if not value.get("type") in STATUS_TYPES or not value.get("stacking_policy") in POLICIES or not value.get("refresh_policy") in ["none", "reset", "extend_if_longer"]: errors.append("invalid_status_kind_or_policy")
	for key: String in ["duration_ms", "stacks", "max_stacks", "magnitude", "interval_ms"]:
		var upper: int = 45000 if key.ends_with("_ms") else 1000 if key in ["stacks", "max_stacks"] else 1000000
		if not CombatJson.integer(value.get(key), 0 if key == "interval_ms" else 1, upper): errors.append("invalid_status_value:" + key)
	if not errors.size() == before: return false
	if value["stacks"] > value["max_stacks"]: errors.append("status_stack_cap")
	if value["type"] in ["wound", "ice"] and value["magnitude"] > 10000: errors.append("status_bp_bound")
	if value["type"] == "shield" and value["stacking_policy"] != "independent_instances": errors.append("shield_requires_independent_capacity")
	if (value["type"] in ["toxin", "burn"]) != (value["interval_ms"] > 0): errors.append("status_period_mismatch")
	if not value["debuff"] is bool or value["debuff"] != (value["type"] != "shield"): errors.append("status_debuff_mismatch")
	if not value["metadata"] is Dictionary or not value["metadata"].get("origin") in ["mechanics_fixture", "legacy_hero_skill"]: errors.append("status_provenance_required")
	return errors.size() == before

func keys(value: Dictionary, expected: Array[String]) -> bool:
	for key: String in expected:
		if not value.has(key):
			errors.append("missing_field:" + key)
			return false
	for key: Variant in value:
		if not key is String or not key in expected:
			errors.append("unknown_field:" + str(key))
			return false
	return true

func label(value: Variant) -> bool:
	return value is String and not value.is_empty() and value.length() <= 100
