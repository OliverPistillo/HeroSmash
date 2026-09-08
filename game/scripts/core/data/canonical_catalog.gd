class_name CanonicalCatalog
extends RefCounted
## Transactional typed catalog; unsuccessful load never replaces a valid catalog.

const DATASETS: Array[String] = ["branches", "cards", "heroes", "economy", "effects"]
const BRANCH_NAMES: Array[String] = ["Assault", "Guardian", "Essence", "Rage", "Ice", "Toxin", "Shield", "Healing", "Power", "Precision", "Wound", "Dodge"]
var errors: Array[String] = []
var _branches: Dictionary[String, BranchDefinition] = {}
var _cards: Dictionary[String, CardDefinition] = {}
var _heroes: Dictionary[String, HeroDefinition] = {}
var _effects: Dictionary[String, EffectDefinition] = {}
var _economy: EconomyDefinition

func branch(id: String) -> BranchDefinition:
	if not _branches.has(id): errors.append("unknown_branch: " + id)
	return _branches.get(id)

func card(id: String) -> CardDefinition:
	if not _cards.has(id): errors.append("unknown_card: " + id)
	return _cards.get(id)

func hero(id: String) -> HeroDefinition:
	if not _heroes.has(id): errors.append("unknown_hero: " + id)
	return _heroes.get(id)

func effect(id: String) -> EffectDefinition:
	if not _effects.has(id): errors.append("unknown_effect: " + id)
	return _effects.get(id)

func economy() -> EconomyDefinition:
	return _economy

func counts() -> Dictionary[String, int]:
	return {"branches":_branches.size(), "cards":_cards.size(), "heroes":_heroes.size(), "effects":_effects.size(), "economy":0 if _economy == null else 1}

func read_json(path: String) -> Variant:
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null:
		errors.append("file_open: " + path)
		return null
	if file.get_length() > 3000000:
		errors.append("file_too_large: " + path)
		return null
	var parser: JSON = JSON.new()
	if parser.parse(file.get_as_text()) != OK:
		errors.append("invalid_json %s:%d: %s" % [path, parser.get_error_line(), parser.get_error_message()])
		return null
	return parser.data

func load_directory(directory: String = "res://data/canonical") -> bool:
	errors.clear()
	var documents: Dictionary = {}
	for dataset: String in DATASETS:
		documents[dataset] = read_json(directory.path_join(dataset + ".json"))
	if not errors.is_empty(): return false
	return load_documents(documents)

func load_documents(documents: Dictionary) -> bool:
	errors.clear()
	if documents.size() != DATASETS.size():
		errors.append("dataset set mismatch")
	for dataset: String in DATASETS:
		var schema: Variant = read_json("res://data/schemas/" + dataset + ".schema.json")
		if schema is Dictionary:
			var validator: CanonicalSchemaValidator = CanonicalSchemaValidator.new()
			errors.append_array(validator.validate(documents.get(dataset), schema, dataset))
	if not errors.is_empty(): return false
	_validate_relations(documents)
	if not errors.is_empty(): return false
	var next_branches: Dictionary[String, BranchDefinition] = {}
	var next_cards: Dictionary[String, CardDefinition] = {}
	var next_heroes: Dictionary[String, HeroDefinition] = {}
	var next_effects: Dictionary[String, EffectDefinition] = {}
	for record: Dictionary in documents["branches"]["records"]:
		next_branches[record["id"]] = BranchDefinition.new(record)
	for record: Dictionary in documents["cards"]["records"]:
		next_cards[record["id"]] = CardDefinition.new(record)
	for record: Dictionary in documents["heroes"]["records"]:
		next_heroes[record["id"]] = HeroDefinition.new(record)
	for record: Dictionary in documents["effects"]["records"]:
		next_effects[record["id"]] = EffectDefinition.new(record)
	_branches = next_branches
	_cards = next_cards
	_heroes = next_heroes
	_effects = next_effects
	_economy = EconomyDefinition.new(documents["economy"]["records"][0])
	return true

func _require(condition: bool, message: String) -> void:
	if not condition: errors.append(message)

func _memberships(raw: Array, legacy_id: int) -> Array[String]:
	var result: Array[String] = []
	for item: String in raw:
		for token: String in item.replace(";", ",").split(","):
			var name: String = token.strip_edges().to_lower()
			if name.is_empty(): continue
			if name == "guadian" and legacy_id == 70: name = "guardian"
			_require(EffectCapabilities.BRANCHES.has(name), "unknown branch: " + name)
			_require(not result.has(name), "repeated normalized branch")
			result.append(name)
	return result

func _validate_relations(documents: Dictionary) -> void:
	for dataset: String in DATASETS:
		var ids: Array[String] = []
		var sources: Dictionary = {}
		for source: Dictionary in documents[dataset]["sources"]:
			_require(not sources.has(source["path"]), "duplicate provenance source")
			sources[source["path"]] = source["sha256"]
		for record: Dictionary in documents[dataset]["records"]:
			_require(not ids.has(record["id"]), dataset + ": duplicate id")
			ids.append(record["id"])
			var provenance: Dictionary = record["provenance"]
			_require(sources.get(provenance["source"]) == provenance["sourceSha256"], dataset + ": invalid provenance reference")
	var branch_rows: Array = documents["branches"]["records"]
	for index: int in range(12):
		var branch_record: Dictionary = branch_rows[index]
		_require(branch_record["id"] == EffectCapabilities.BRANCHES[index] and branch_record["name"] == BRANCH_NAMES[index], "canonical branch order/name")
		_require(branch_record["id"] == branch_record["legacy"]["id"] and branch_record["name"] == branch_record["legacy"]["name"], "branch metadata mismatch")
	var rarities: Dictionary = {"Normal":0, "Epic":0, "Legendary":0}
	var memberships: Dictionary = {1:0, 2:0}
	var cards: Array = documents["cards"]["records"]
	for index: int in range(150):
		var record: Dictionary = cards[index]
		var raw: Dictionary = record["legacy"]
		_require(int(record["legacyId"]) == index + 1 and record["legacyId"] == raw["id"] and record["id"] == "legacy_%03d" % int(raw["id"]), "legacy IDs/order mismatch")
		for pair: Array in [["name", "name"], ["originalText", "effect"], ["rarity", "rarity"], ["cost", "cost"]]:
			_require(record[pair[0]] == raw[pair[1]], record["id"] + ": metadata mismatch " + pair[0])
		_require(record["branches"] == _memberships(raw["branch"], int(raw["id"])), "branch normalization mismatch")
		_require(record["maxLevel"] == raw["levels"].size() and record["maxLevel"] == {"Normal":5, "Epic":3, "Legendary":1}[record["rarity"]], "maxLevel mismatch")
		for level_index: int in range(raw["levels"].size()):
			_require(raw["levels"][level_index]["level"] == level_index + 1, "invalid level sequence")
		rarities[record["rarity"]] += 1
		memberships[record["branches"].size()] += 1
		var effect_record: Dictionary = documents["effects"]["records"][index]
		_require(effect_record["cardId"] == record["id"] and effect_record["id"] == record["id"], "effect coverage/order")
		_require(effect_record["originalTextSha256"] == String(record["originalText"]).sha256_text(), "effect text guard mismatch")
		_require((not effect_record["rules"].is_empty()) == (effect_record["lifecycle"] == "implemented"), "lifecycle/rules mismatch")
		errors.append_array(EffectCapabilities.validate_rules(effect_record["rules"]))
	_require(rarities == {"Normal":90, "Epic":36, "Legendary":24}, "rarity distribution mismatch")
	_require(memberships == {1:84, 2:66}, "membership distribution mismatch")
	for hero_record: Dictionary in documents["heroes"]["records"]:
		var raw: Dictionary = hero_record["legacy"]
		for key: String in ["id", "name", "stats"]:
			_require(hero_record[key] == raw[key], "hero metadata mismatch")
		_require(hero_record["branches"] == raw["favoredBranches"] and hero_record["branches"].has(raw["favoredBranch"]), "hero branch mismatch")
