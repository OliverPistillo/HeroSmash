class_name CombatReplay
extends RefCounted

static func create(input: Dictionary, catalog: CombatCatalog) -> Dictionary:
	var run: Dictionary = CombatResolver.new(catalog).run(input, true)
	if not run["ok"]: return run
	return {"ok":true, "replay":{"formatVersion":1, "rulesetVersion":CombatCatalog.RULESET_VERSION, "canonicalDataVersion":CombatCatalog.DATA_VERSION, "dataHash":catalog.data_hash, "scenarioId":input["scenarioId"], "seed":input["seed"], "initialState":input.duplicate(true), "events":run["events"], "finalState":run["result"], "eventHash":run["eventHash"], "resultHash":run["resultHash"]}}

static func verify(replay: Variant, catalog: CombatCatalog) -> Dictionary:
	if not replay is Dictionary: return {"ok":false, "errors":["replay_not_object"]}
	var validator: CombatInput = CombatInput.new()
	if not validator.keys(replay, ["formatVersion", "rulesetVersion", "canonicalDataVersion", "dataHash", "scenarioId", "seed", "initialState", "events", "finalState", "eventHash", "resultHash"]): return {"ok":false, "errors":validator.errors}
	if not CombatJson.integer(replay["formatVersion"], 1, 1) or not CombatJson.integer(replay["seed"], 0, 4294967295): return {"ok":false, "errors":["replay_numeric_header_invalid"]}
	for key: String in ["rulesetVersion", "canonicalDataVersion", "dataHash", "scenarioId", "eventHash", "resultHash"]:
		if not replay[key] is String: return {"ok":false, "errors":["replay_header_type_invalid"]}
	if replay["formatVersion"] != 1 or replay["rulesetVersion"] != CombatCatalog.RULESET_VERSION or replay["canonicalDataVersion"] != CombatCatalog.DATA_VERSION or replay["dataHash"] != catalog.data_hash: return {"ok":false, "errors":["replay_version_or_data_mismatch"]}
	if not validator.check(replay["initialState"], catalog): return {"ok":false, "errors":validator.errors}
	if replay["seed"] != replay["initialState"]["seed"] or replay["scenarioId"] != replay["initialState"]["scenarioId"]: return {"ok":false, "errors":["replay_header_input_mismatch"]}
	if not replay["events"] is Array or replay["events"].size() > 20000 or not replay["finalState"] is Dictionary: return {"ok":false, "errors":["replay_payload_invalid"]}
	var regenerated: Dictionary = create(replay["initialState"], catalog)
	if not regenerated["ok"]: return regenerated
	if CombatJson.encode(regenerated["replay"]) != CombatJson.encode(replay): return {"ok":false, "errors":["replay_stream_result_or_hash_mismatch"]}
	return {"ok":true, "eventHash":replay["eventHash"], "resultHash":replay["resultHash"]}
