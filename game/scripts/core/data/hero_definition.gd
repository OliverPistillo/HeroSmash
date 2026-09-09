class_name HeroDefinition
extends CanonicalDefinition

var display_name: String:
	get: return String(_record["name"])
var role: String:
	get: return String(_record["role"])

func branch_ids() -> Array[String]:
	var result: Array[String] = []
	result.assign(_record["branches"])
	return result

func stats() -> Dictionary[String, float]:
	var result: Dictionary[String, float] = {}
	for key: String in _record["stats"]:
		result[key] = float(_record["stats"][key])
	return result

func legacy_metadata() -> Dictionary:
	return _record["legacy"].duplicate(true)
