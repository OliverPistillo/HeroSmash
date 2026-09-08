class_name FoundationRng
extends RefCounted
## Small deterministic harness RNG. Gameplay RNG/shuffle contract is deferred.

var _state: int

func _init(seed_value: int = 1) -> void:
	_state = seed_value & 0xffffffff

func next_u32() -> int:
	_state = (_state * 1664525 + 1013904223) & 0xffffffff
	return _state
