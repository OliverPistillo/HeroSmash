extends SceneTree

var failures: Array[String] = []
var assertions: int = 0

func check(condition: bool, message: String) -> void:
	assertions += 1
	if not condition: failures.append(message)

func _initialize() -> void:
	var catalog: CanonicalCatalog = CanonicalCatalog.new()
	check(catalog.load_directory(), "load catalog: " + str(catalog.errors))
	if not catalog.errors.is_empty():
		_finish()
		return
	check(catalog.counts() == {"branches":12, "cards":150, "heroes":16, "effects":150, "economy":1}, "complete dataset counts")
	check(catalog.card("legacy_071").cost == 300 and catalog.card("legacy_071").rarity == "Epic", "HEAVY BASH cost exception")
	check(catalog.branch("guardian").display_name == "Guardian", "typed branch")
	check(catalog.hero("fireheart").stats()["hp"] == 930.0 and catalog.hero("fireheart").role == "legacy_oracle", "typed oracle hero")
	check(catalog.economy().constants()["starting_coins"] == 300 and catalog.economy().branch_thresholds() == [4, 10, 20, 40], "typed economy")
	var metadata: Dictionary = catalog.card("legacy_002").legacy_metadata()
	metadata["name"] = "mutated consumer copy"
	check(catalog.card("legacy_002").display_name == "SHARP EDGE", "defensive metadata copy")
	check(catalog.card("unknown") == null and catalog.errors.back().contains("unknown_card"), "unknown ID error")
	var documents: Dictionary = {}
	for dataset: String in CanonicalCatalog.DATASETS:
		documents[dataset] = catalog.read_json("res://data/canonical/" + dataset + ".json")
	var cases: Array = catalog.read_json("res://tests/fixtures/canonical_cases.json")
	for fixture: Dictionary in cases:
		var malformed: Dictionary = documents.duplicate(true)
		var node: Variant = malformed[fixture["dataset"]]
		var path: Array = fixture["path"]
		for index: int in range(path.size() - 1):
			var part: Variant = int(path[index]) if path[index] is float else path[index]
			node = node[part]
		var key: Variant = int(path.back()) if path.back() is float else path.back()
		match fixture["op"]:
			"remove": node.erase(key)
			"pop": node[key].pop_back()
			_: node[key] = fixture["value"]
		check(not catalog.load_documents(malformed), "must reject " + fixture["name"])
		check(not catalog.errors.is_empty(), "clear error for " + fixture["name"])
		check(catalog.card("legacy_002").display_name == "SHARP EDGE", "transactional reload " + fixture["name"])
	var validator: CanonicalSchemaValidator = CanonicalSchemaValidator.new()
	check(not validator.validate({}, {"properties":{"absent":{"unknown_keyword":1}}}).is_empty(), "unknown schema keyword in absent property fails closed")
	check(not validator.validate(true, {"type":"integer"}).is_empty(), "bool is not integer")
	check(not validator.validate([1, 1], {"type":"array", "uniqueItems":true}).is_empty(), "uniqueItems")
	check(validator.validate(null, {"type":["string", "null"]}).is_empty(), "nullable legacy hero skill")
	var bad_file: FileAccess = FileAccess.open("user://v116_invalid.json", FileAccess.WRITE)
	bad_file.store_string("{invalid JSON")
	bad_file.close()
	catalog.errors.clear()
	check(catalog.read_json("user://v116_invalid.json") == null and catalog.errors.back().contains("invalid_json"), "malformed JSON line error")
	DirAccess.remove_absolute("user://v116_invalid.json")
	check(catalog.load_directory(), "valid reload after malformed corpus")
	_finish()

func _finish() -> void:
	print(JSON.stringify({"suite":"canonical_data", "assertions":assertions, "failures":failures, "status":"pass" if failures.is_empty() else "fail"}))
	quit(0 if failures.is_empty() else 1)
