class_name FighterEventAdapter
extends RefCounted
## Consumes immutable CombatEvent dictionaries. Never owns or changes combat state.
## Sequence IDs are scoped to reset_stream(); rewind reconstructs state without cues.

var entity_id: String = ""
var dead: bool = false
var clock_ms: int = 0
var current_clip: String = "idle"
var clip_started_ms: int = 0
var clip_offset: float = 0.0
var last_sequence: int = 0
var cue_count: int = 0
var errors: Array[String] = []
var _seen: Dictionary = {}
var _clips: Dictionary = {}
var _pending: Array[Dictionary] = []


func configure(id: String, clip_specs: Array) -> void:
	entity_id = id
	_clips.clear()
	for item: Dictionary in clip_specs:
		_clips[String(item["name"])] = item.duplicate(true)
	reset_stream()


func reset_stream() -> void:
	dead = false
	clock_ms = 0
	current_clip = "idle"
	clip_started_ms = 0
	clip_offset = 0.0
	last_sequence = 0
	cue_count = 0
	_seen.clear()
	_pending.clear()
	errors.clear()


func enqueue(events: Array) -> void:
	for value: Variant in events:
		if not value is Dictionary:
			errors.append("malformed_event")
			continue
		var event: Dictionary = value
		if not _valid(event):
			errors.append("malformed_event")
			continue
		var sequence: int = int(event["sequence"])
		if _seen.has(sequence):
			if _seen[sequence] != event:
				errors.append("conflicting_sequence")
			continue
		_seen[sequence] = event.duplicate(true)
		_pending.append(event.duplicate(true))
	_pending.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return int(a["at_ms"]) < int(b["at_ms"]) if a["at_ms"] != b["at_ms"] else int(a["sequence"]) < int(b["sequence"]))


func _valid(event: Dictionary) -> bool:
	for key: String in ["sequence", "at_ms", "type", "source", "target", "payload", "parent_sequence"]:
		if not event.has(key):
			return false
	return event["sequence"] is int and event["at_ms"] is int and int(event["sequence"]) > 0 and int(event["at_ms"]) >= 0 and event["parent_sequence"] is int and int(event["parent_sequence"]) >= 0 and int(event["parent_sequence"]) < int(event["sequence"]) and event["type"] is String and event["source"] is String and event["target"] is String and event["payload"] is Dictionary


func advance(to_ms: int, suppress_cues: bool = false) -> Array[Dictionary]:
	var cues: Array[Dictionary] = []
	if to_ms < clock_ms:
		errors.append("rewind_requires_seek")
		return cues
	clock_ms = to_ms
	while not _pending.is_empty() and int(_pending[0]["at_ms"]) <= to_ms:
		var event: Dictionary = _pending.pop_front()
		var at_ms: int = int(event["at_ms"])
		# Older arrivals cannot rewind a pose selected by a newer resolver sequence.
		if int(event["sequence"]) <= last_sequence:
			continue
		last_sequence = int(event["sequence"])
		var source_matches: bool = event["source"] == entity_id
		var target_matches: bool = event["target"] == entity_id
		var cue: String = ""
		match String(event["type"]):
			"BasicAttack":
				if source_matches and not dead:
					_start("attack_light", at_ms, "hit")
					cue = "hit"
			"SkillCast":
				if source_matches and not dead:
					_start("skill_cast", at_ms, "cast")
					cue = "vfx_spawn"
			"DamageApplied":
				if source_matches and not dead and bool(event["payload"].get("critical", false)) and "basic" in event["payload"].get("tags", []):
					_start("attack_heavy", at_ms, "hit")
				if target_matches and not dead and int(event["payload"].get("actual_milli", 0)) > 0:
					_start("hit_react", at_ms)
					cue = "impact"
			"Dodged":
				if target_matches and not dead:
					_start("dodge", at_ms)
			"ShieldAbsorbed":
				if target_matches and not dead:
					cue = "barrier"
			"CombatantKO":
				if target_matches:
					dead = true
					_start("ko", at_ms)
					# Suppress pending outgoing cosmetics when KO shares this tick.
					cues.clear()
			"CombatantRevived":
				if target_matches:
					dead = false
					_start("idle", at_ms)
			"CombatStarted":
				_start("intro", at_ms)
			"CombatEnded":
				if not dead:
					_start("victory" if event["payload"].get("winner", "") == entity_id else "idle", at_ms)
		if cue != "" and not suppress_cues and to_ms - at_ms <= 80:
			cues.append({"sequence": event["sequence"], "at_ms": at_ms, "kind": cue, "entity_id": entity_id})
	var spec: Dictionary = _clips.get(current_clip, {})
	if not spec.is_empty() and not bool(spec.get("loop", false)) and not dead:
		if pose_seconds() >= float(spec["duration_seconds"]):
			_start("idle", to_ms)
	cue_count += cues.size()
	return cues


func _start(clip: String, at_ms: int, contact: String = "") -> void:
	current_clip = clip if _clips.has(clip) else "idle"
	if current_clip != clip:
		errors.append("missing_clip:" + clip)
	clip_started_ms = at_ms
	clip_offset = 0.0
	if contact != "" and _clips.has(clip):
		for marker: Dictionary in _clips[clip].get("markers", []):
			if marker["name"] == contact:
				clip_offset = float(marker["phase"]) * float(_clips[clip]["duration_seconds"])


func pose_seconds() -> float:
	return maxf(0.0, float(clock_ms - clip_started_ms) / 1000.0 + clip_offset)


func seek(events: Array, to_ms: int) -> void:
	reset_stream()
	enqueue(events)
	advance(to_ms, true)
