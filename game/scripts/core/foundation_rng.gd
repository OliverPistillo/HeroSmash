class_name FoundationRng
extends RefCounted
## Deterministic LCG primitive, also used by the opt-in v1.16 effect profile.
## Full combat/draft shuffle distributions remain a separate specification.

var _state: int

func _init(seed_value: int = 1) -> void:
	_state = seed_value & 0xffffffff

func next_u32() -> int:
	_state = (_state * 1664525 + 1013904223) & 0xffffffff
	return _state

func copy_state() -> FoundationRng:
	return FoundationRng.new(_state)

func state_value() -> int:
	return _state
