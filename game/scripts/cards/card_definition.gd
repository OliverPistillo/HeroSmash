class_name CardDefinition
extends CanonicalDefinition

var legacy_id: int:
	get: return int(_record["legacyId"])
var display_name: String:
	get: return String(_record["name"])
var original_text: String:
	get: return String(_record["originalText"])
var rarity: String:
	get: return String(_record["rarity"])
var cost: int:
	get: return int(_record["cost"])
var max_level: int:
	get: return int(_record["maxLevel"])

func branch_ids() -> Array[String]:
	var result: Array[String] = []
	result.assign(_record["branches"])
	return result

func legacy_metadata() -> Dictionary:
	return _record["legacy"].duplicate(true)
