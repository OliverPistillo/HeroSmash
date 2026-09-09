extends SceneTree

var assertions: int = 0
var failures: Array[String] = []

func check(value: bool, message: String) -> void:
	assertions += 1
	if not value: failures.append(message)

func _initialize() -> void:
	var catalog: CombatCatalog = CombatCatalog.new()
	check(catalog.load_data(), "catalog")
	var scenarios: CombatScenarios = CombatScenarios.new(catalog)
	for id: String in scenarios.ids():
		var input: Dictionary = scenarios.build(id, 5)
		var created: Dictionary = CombatReplay.create(input, catalog)
		check(created["ok"], "scenario:" + id)
		if not created["ok"]: continue
		var replay: Dictionary = created["replay"]
		check(CombatReplay.verify(CombatJson.normalize(JSON.parse_string(CombatJson.encode(replay))), catalog)["ok"], "serialized roundtrip:" + id)
		var copy: Dictionary = input.duplicate(true)
		copy["sides"].reverse()
		copy["combatants"].reverse()
		var mirrored: Dictionary = CombatReplay.create(copy, catalog)["replay"]
		check(mirrored["eventHash"] == replay["eventHash"] and mirrored["resultHash"] == replay["resultHash"], "all mechanisms entity symmetry:" + id)
		for mutation: String in ["seed", "version", "data", "scenario", "event", "final", "event_hash", "result_hash", "input"]:
			var corrupt: Dictionary = replay.duplicate(true)
			match mutation:
				"seed": corrupt["seed"] += 1
				"version": corrupt["rulesetVersion"] = "old"
				"data": corrupt["dataHash"] = "0".repeat(64)
				"scenario": corrupt["scenarioId"] = "wrong"
				"event": corrupt["events"][1]["at_ms"] = -1
				"final": corrupt["finalState"]["final"][0]["hp_milli"] += 1
				"event_hash": corrupt["eventHash"] = "0".repeat(64)
				"result_hash": corrupt["resultHash"] = "0".repeat(64)
				"input": corrupt["initialState"]["combatants"][0]["stats"]["max_hp_milli"] += 1
			check(not CombatReplay.verify(corrupt, catalog)["ok"], "reject replay tampering:" + mutation)
		for key: String in replay:
			var corrupt: Dictionary = replay.duplicate(true)
			corrupt[key] = null
			check(not CombatReplay.verify(corrupt, catalog)["ok"], "reject null replay:" + key)
	var document: Dictionary = CombatJson.read_file("res://data/generated/v1_17/combat_catalog.json")
	var before: String = catalog.data_hash
	for mutation: String in ["version", "duplicate", "stat", "operator", "lethal", "type"]:
		var corrupt: Dictionary = document.duplicate(true)
		match mutation:
			"version": corrupt["rulesetVersion"] = 5
			"duplicate": corrupt["heroes"][1] = corrupt["heroes"][0]
			"stat": corrupt["heroes"][0]["stats"]["max_hp_milli"] += 1
			"operator": corrupt["effects"][1]["rules"][0]["actions"][0]["amount"] += 1
			"lethal": corrupt["effects"][119]["lethal_rules"][0]["restore_hp_bp"] = 9999
			"type": corrupt["heroes"] = null
		check(not catalog.load_document(corrupt), "reject generated drift:" + mutation)
		check(catalog.data_hash == before and catalog.hero_input("fireheart", "a")["stats"]["max_hp_milli"] == 930000, "transactional catalog:" + mutation)
	print(CombatJson.encode({"suite":"combat_replay", "assertions":assertions, "failures":failures}))
	quit(0 if failures.is_empty() else 1)
