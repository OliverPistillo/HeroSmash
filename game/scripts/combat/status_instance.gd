class_name StatusInstance
extends RefCounted

var id: String
var type: String
var source: String
var target: String
var applied_at: int
var duration_ms: int
var expires_at: int
var stacks: int
var max_stacks: int
var magnitude: int
var capacity_milli: int
var stacking_policy: String
var refresh_policy: String
var interval_ms: int
var next_tick: int
var tick_remainder: int = 0
var debuff: bool
var metadata: Dictionary

func _init(instance_id: String, definition: Dictionary, source_id: String, target_id: String, now: int) -> void:
	id = instance_id
	type = definition["type"]
	source = source_id
	target = target_id
	applied_at = now
	duration_ms = int(definition["duration_ms"])
	expires_at = now + duration_ms
	stacks = int(definition["stacks"])
	max_stacks = int(definition["max_stacks"])
	magnitude = int(definition["magnitude"])
	capacity_milli = magnitude * stacks if type == "shield" else 0
	stacking_policy = definition["stacking_policy"]
	refresh_policy = definition["refresh_policy"]
	interval_ms = int(definition["interval_ms"])
	next_tick = now + interval_ms if interval_ms > 0 else 0
	debuff = bool(definition["debuff"])
	metadata = definition["metadata"].duplicate(true)

func snapshot(now: int) -> Dictionary:
	return {"id":id, "type":type, "source":source, "target":target, "appliedAt":applied_at, "duration":duration_ms, "expiresAt":expires_at, "remaining":maxi(0, expires_at - now), "stacks":stacks, "maxStacks":max_stacks, "magnitude":magnitude, "capacity_milli":capacity_milli, "stackingPolicy":stacking_policy, "refreshPolicy":refresh_policy, "periodicInterval":interval_ms, "nextTick":next_tick, "tickRemainder":tick_remainder, "debuff":debuff, "metadata":metadata.duplicate(true)}
