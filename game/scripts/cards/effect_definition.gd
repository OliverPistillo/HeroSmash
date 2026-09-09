class_name EffectDefinition
extends CanonicalDefinition

var card_id: String:
	get: return String(_record["cardId"])
var profile: String:
	get: return String(_record["profile"])
var lifecycle: String:
	get: return String(_record["lifecycle"])
var reason: String:
	get: return String(_record["reason"])

func rules() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for rule: Dictionary in _record["rules"]:
		result.append(rule.duplicate(true))
	return result
