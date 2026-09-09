class_name DamageEvent
extends RefCounted

var source: String
var target: String
var amount_milli: int
var damage_type: String
var tags: Array[String]
var can_crit: bool
var can_dodge: bool
var reflectable: bool
var parent_sequence: int
var depth: int

func _init(source_id: String, target_id: String, amount: int, kind: String, source_tags: Array[String], critical_eligible: bool = false, dodge_eligible: bool = false, may_reflect: bool = false, parent: int = 0, chain_depth: int = 0) -> void:
	source = source_id
	target = target_id
	amount_milli = amount
	damage_type = kind
	tags = source_tags.duplicate()
	can_crit = critical_eligible
	can_dodge = dodge_eligible
	reflectable = may_reflect
	parent_sequence = parent
	depth = chain_depth
