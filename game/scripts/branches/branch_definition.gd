class_name BranchDefinition
extends CanonicalDefinition

var display_name: String:
	get: return String(_record["name"])

func legacy_metadata() -> Dictionary:
	return _record["legacy"].duplicate(true)
