class_name CanonicalDefinition
extends RefCounted

var _record: Dictionary
var id: String:
	get: return String(_record["id"])

func _init(record: Dictionary) -> void:
	_record = record.duplicate(true)

func provenance() -> Dictionary:
	return _record["provenance"].duplicate(true)

func snapshot() -> Dictionary:
	return _record.duplicate(true)
