class_name EffectEvent
extends RefCounted
## Input fact; strict payload validation occurs before publishing any result.

var trigger: String
var actor: int
var at_ms: int
var payload: Dictionary

func _init(event_trigger: String, actor_id: int, timestamp_ms: int, values: Dictionary = {}) -> void:
	trigger = event_trigger
	actor = actor_id
	at_ms = timestamp_ms
	payload = values.duplicate(true)
