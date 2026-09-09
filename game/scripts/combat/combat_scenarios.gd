class_name CombatScenarios
extends RefCounted

var document: Dictionary
var catalog: CombatCatalog

func _init(data: CombatCatalog) -> void:
	catalog = data
	document = CombatJson.read_file("res://data/combat/scenarios.json")

func ids() -> Array[String]:
	var result: Array[String] = []
	for row: Dictionary in document["records"]: result.append(row["id"])
	return result

func build(id: String, seed_value: int, horizon: int = 45000) -> Dictionary:
	var row: Dictionary = {}
	for candidate: Dictionary in document["records"]:
		if candidate["id"] == id: row = candidate
	if row.is_empty(): return {}
	if row.has("mirrorOf"):
		var original: Dictionary = build(row["mirrorOf"], seed_value, horizon)
		original["scenarioId"] = id
		original["sides"].reverse()
		original["combatants"].reverse()
		return original
	var combatants: Array[Dictionary] = []
	for index: int in range(2):
		var actor_id: String = "alpha" if index == 0 else "beta"
		var other_id: String = "beta" if index == 0 else "alpha"
		var actor: Dictionary = catalog.hero_input(row["heroes"][index], actor_id)
		for card_id: String in row["cards"][index]:
			var numbered: bool = card_id in ["049", "090", "120"]
			actor["bindings"].append({"cardId":"legacy_" + card_id, "profile":"numbered" if numbered else "base_text_v1", "level":1 if numbered else 0})
		for kind: String in row["templates"][index]: actor["status_templates"][kind] = document["statusFixtures"][kind].duplicate(true)
		for kind: String in row["initial"][index]:
			var status: Dictionary = document["statusFixtures"][kind].duplicate(true)
			status["source"] = actor_id if kind == "shield" else other_id
			actor["initial_statuses"].append(status)
		if row["prevention"][index] > 0: actor["death_prevention"] = {"charges":row["prevention"][index], "surviving_hp_milli":1000, "origin":"mechanics_fixture"}
		combatants.append(actor)
	return {"scenarioId":id, "rulesetVersion":CombatCatalog.RULESET_VERSION, "canonicalDataVersion":CombatCatalog.DATA_VERSION, "seed":seed_value, "horizon_ms":horizon, "combatants":combatants, "sides":["alpha", "beta"]}
