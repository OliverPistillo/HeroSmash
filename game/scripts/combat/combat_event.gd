class_name CombatEvent
extends RefCounted
## Serializable value model. Presentation consumes amounts rather than recalculating.

static func value(sequence: int, now: int, kind: String, source: String, target: String, payload: Dictionary, parent: int = 0) -> Dictionary:
	return {"sequence":sequence, "at_ms":now, "type":kind, "source":source, "target":target, "parent_sequence":parent, "payload":payload}
