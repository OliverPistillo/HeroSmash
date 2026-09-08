class_name CombatCatalog
extends RefCounted

const RULESET_VERSION: String = "combat_v1.17.1"
const DATA_VERSION: String = "v1.16.1"
var errors: Array[String] = []
var ruleset: Dictionary = {}
var data_hash: String = ""
var _heroes: Dictionary = {}
var _effects: Dictionary = {}
var _levels: Dictionary = {}
var _canonical: CanonicalCatalog = CanonicalCatalog.new()

func load_data() -> bool:
	return load_document(CombatJson.read_file("res://data/generated/v1_17/combat_catalog.json"))

func load_document(document: Variant) -> bool:
	errors.clear()
	if not validate_schema(document, "catalog"): return false
	if not _canonical.load_directory():
		errors.append_array(_canonical.errors)
		return false
	var next_heroes: Dictionary = {}
	var next_effects: Dictionary = {}
	var stat_map: Dictionary = {"hp":"max_hp_milli", "atk":"attack_milli", "arm":"armor_milli", "focus":"focus_milli", "spd":"attack_speed_milli", "crit":"crit_bp", "critD":"crit_multiplier_bp", "regen":"energy_regen_milli", "dodge":"dodge_bp"}
	for hero_record: Dictionary in document["heroes"]:
		var original: HeroDefinition = _canonical.hero(hero_record["id"])
		if original == null or next_heroes.has(hero_record["id"]):
			errors.append("unknown_or_duplicate_hero")
			continue
		var raw: Dictionary = original.snapshot()["legacy"]
		for key: String in stat_map:
			var destination: String = stat_map[key]
			if int(hero_record["stats"][destination]) != roundi(float(raw["stats"][key]) * (10000 if destination.ends_with("_bp") else 1000)): errors.append("compiled_hero_stat_drift")
		var skill_map: Dictionary = {"cd":"cooldown_ms", "energy":"cost_milli", "pow":"power_bp", "dur":"duration_ms", "dot":"dot_milli_per_second"}
		for key: String in skill_map:
			if int(hero_record["skill"][skill_map[key]]) != roundi(float(raw["skill"][key]) * (10000 if key == "pow" else 1000)): errors.append("compiled_skill_value_drift")
		if hero_record["skill"]["name"] != raw["skill"]["name"] or hero_record["skill"]["status"] != (raw["skill"]["status"] if raw["skill"]["status"] != null else "") or hero_record["skill"]["damage_type"] != ("physical" if raw["skill"]["type"] == "phys" else "magic"): errors.append("compiled_skill_kind_drift")
		next_heroes[hero_record["id"]] = hero_record.duplicate(true)
	for effect_record: Dictionary in document["effects"]:
		var original: EffectDefinition = _canonical.effect(effect_record["id"])
		if original == null or next_effects.has(effect_record["id"]):
			errors.append("unknown_or_duplicate_effect")
			continue
		if effect_record["rules"] != CombatJson.normalize(original.rules()) or effect_record["base_text_allowed"] != (original.lifecycle == "implemented") or effect_record["source_text_hash"] != original.snapshot()["originalTextSha256"]: errors.append("compiled_effect_drift")
		var allowed: Array = [1] if effect_record["id"] in ["legacy_049", "legacy_090", "legacy_120"] else []
		if effect_record["numbered_levels"] != allowed or (not effect_record["lethal_rules"].is_empty()) != (effect_record["id"] == "legacy_120"): errors.append("compiled_level_or_lethal_drift")
		next_effects[effect_record["id"]] = effect_record.duplicate(true)
	if not errors.is_empty(): return false
	ruleset = document["ruleset"].duplicate(true)
	data_hash = CombatJson.digest(document)
	_heroes = next_heroes
	_effects = next_effects
	_levels.clear()
	return true

func validate_schema(document: Variant, name: String) -> bool:
	var schema: Dictionary = CombatJson.read_file("res://data/schemas/combat.schema.json")
	var expanded: Dictionary = expand_refs(schema["$defs"][name], schema["$defs"])
	errors.append_array(CanonicalSchemaValidator.new().validate(document, expanded, name))
	return errors.is_empty()

func expand_refs(node: Variant, definitions: Dictionary) -> Variant:
	if node is Array:
		var result: Array = []
		for value: Variant in node: result.append(expand_refs(value, definitions))
		return result
	if node is Dictionary:
		if node.has("$ref"): return expand_refs(definitions[String(node["$ref"]).trim_prefix("#/$defs/")], definitions)
		var result: Dictionary = {}
		for key: String in node:
			# The v1.16 validator supports boolean additionalProperties only.
			# Numeric oracle values are checked explicitly when levels load.
			result[key] = true if key == "additionalProperties" and node[key] is Dictionary else expand_refs(node[key], definitions)
		if result.has("const") and not result.has("type"):
			result["type"] = {TYPE_INT:"integer", TYPE_FLOAT:"number", TYPE_STRING:"string", TYPE_BOOL:"boolean", TYPE_DICTIONARY:"object", TYPE_ARRAY:"array"}[typeof(result["const"])]
		return result
	return node

func hero_input(hero_id: String, combatant_id: String) -> Dictionary:
	if not _heroes.has(hero_id):
		errors.append("unknown_hero: " + hero_id)
		return {}
	var hero: Dictionary = _heroes[hero_id]
	return {"id":combatant_id, "heroId":hero_id, "origin":"canonical_hero", "stats":hero["stats"].duplicate(true), "skill":hero["skill"].duplicate(true), "hp_milli":hero["stats"]["max_hp_milli"], "energy_milli":0, "bindings":[], "initial_statuses":[], "status_templates":{}, "death_prevention":{"charges":0, "surviving_hp_milli":0, "origin":"none"}}

func effect(id: String) -> Dictionary:
	return _effects.get(id, {}).duplicate(true)

func hero(id: String) -> Dictionary:
	return _heroes.get(id, {}).duplicate(true)

func source_level(card_id: String, level: int) -> Dictionary:
	errors.clear()
	if _levels.is_empty():
		var document: Variant = CombatJson.read_file("res://data/generated/v1_17/card_levels.json")
		if not validate_schema(document, "levels"):
			errors.append("invalid_level_catalog")
			return {}
		for row: Dictionary in document["records"]:
			for value: Variant in row["legacyOracleValues"].values():
				if not (value is int or value is float) or not is_finite(float(value)):
					errors.append("nonfinite_oracle_value")
					_levels.clear()
					return {}
			var key: String = row["cardId"] + ":" + str(row["level"])
			var original: CardDefinition = _canonical.card(row["cardId"])
			if original == null:
				errors.append("unknown_level_card")
				_levels.clear()
				return {}
			var card_record: Dictionary = CombatJson.normalize(original.snapshot())
			if int(row["level"]) > int(card_record["maxLevel"]) or row["maxLevel"] != card_record["maxLevel"] or row["sourceLevel"] != card_record["legacy"]["levels"][int(row["level"]) - 1] or row["canonicalNumberedExecutable"] != (row["cardId"] in ["legacy_049", "legacy_090", "legacy_120"]):
				errors.append("source_level_drift")
				_levels.clear()
				return {}
			if _levels.has(key):
				errors.append("duplicate_level")
				_levels.clear()
				return {}
			_levels[key] = row
	var key: String = card_id + ":" + str(level)
	if not _levels.has(key): errors.append("unknown_card_or_level: " + key)
	return _levels.get(key, {}).duplicate(true)

func source_parameter(card_id: String, level: int, key: String) -> Dictionary:
	var row: Dictionary = source_level(card_id, level)
	if row.is_empty(): return {}
	var parameters: Dictionary = row["sourceLevel"].get("parameters", {})
	if not parameters.has(key):
		errors.append("missing_source_parameter: " + key)
		return {}
	return {"value":parameters[key], "binding_status":"source_value_only", "provenance":row["provenance"]}

func legacy_oracle_values(card_id: String, level: int) -> Dictionary:
	var row: Dictionary = source_level(card_id, level)
	return row.get("legacyOracleValues", {}).duplicate(true)

func combat_values(card_id: String, level: int) -> Dictionary:
	var row: Dictionary = source_level(card_id, level)
	if row.is_empty(): return {}
	if not row["canonicalNumberedExecutable"]:
		errors.append("unresolved_numbered_effect_binding: " + card_id)
		return {}
	return effect(card_id)

func next_owned_level(card_id: String, current_level: int) -> Dictionary:
	var row: Dictionary = source_level(card_id, 1)
	if row.is_empty(): return {}
	if current_level < 0 or current_level >= int(row["maxLevel"]):
		errors.append("level_out_of_range_or_maximum")
		return {}
	return {"previous":current_level, "next":current_level + 1, "classification":"legacy_acquisition_transition_only"}
