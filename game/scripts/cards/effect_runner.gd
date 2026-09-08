class_name EffectRunner
extends RefCounted
## Data-driven, seeded pilot interpreter. No card-ID branches or scene dependency.

const MAX_VALUE: int = 1000000000
const MAX_TIME_MS: int = 3600000
const MAX_WORK: int = 10000
var errors: Array[String] = []
var _rng: FoundationRng
var _actors: Array[EffectActorState] = []
var _bindings: Array[Dictionary] = []
var _rules: Array[Dictionary] = []
var _commands: Array[Dictionary] = []
var _time_ms: int = 0
var _started: bool = false
var _ended: bool = false
var _work: int = 0
var _definition_schema: Dictionary = {}

func _init(seed_value: int = 1) -> void:
	_rng = FoundationRng.new(seed_value)

func bind(actor: int, effect: EffectDefinition, profile: String, level: int = 0) -> bool:
	errors.clear()
	if _started: return _fail("binding_after_start")
	if actor < 0 or actor > 1: return _fail("invalid_actor")
	if effect == null: return _fail("unknown_effect")
	if _definition_schema.is_empty():
		var reader: CanonicalCatalog = CanonicalCatalog.new()
		var schema: Variant = reader.read_json("res://data/schemas/effects.schema.json")
		if not schema is Dictionary: return _fail("effect_schema_unavailable: " + str(reader.errors))
		_definition_schema = schema["properties"]["records"]["items"]
	var validator: CanonicalSchemaValidator = CanonicalSchemaValidator.new()
	errors.append_array(validator.validate(effect.snapshot(), _definition_schema, "effect_binding"))
	if not errors.is_empty(): return false
	if level != 0: return _fail("unsupported_progression: numbered card levels are unresolved")
	if profile != "base_text_v1" or effect.profile != profile: return _fail("unsupported_profile: explicit base_text_v1 required")
	if effect.lifecycle != "implemented": return _fail("unsupported_semantics " + effect.card_id + ": " + effect.reason)
	if effect.rules().is_empty(): return _fail("implemented_effect_has_no_rules")
	for binding: Dictionary in _bindings:
		if binding["actor"] == actor and binding["card_id"] == effect.card_id: return _fail("duplicate_binding: card-copy progression unresolved")
	if _bindings.size() >= 30: return _fail("binding_limit")
	errors.append_array(EffectCapabilities.validate_rules(effect.rules()))
	if not errors.is_empty(): return false
	_bindings.append({"actor":actor, "card_id":effect.card_id, "rules":effect.rules()})
	return true

func start(actors: Array[EffectActorState]) -> bool:
	errors.clear()
	if _started: return _fail("duplicate_combat_start")
	if actors.size() != 2: return _fail("requires_two_actors")
	for actor: EffectActorState in actors:
		if actor == null: return _fail("null_actor")
		if actor.max_hp_milli < 1 or actor.max_hp_milli > MAX_VALUE or actor.hp_milli < 1 or actor.hp_milli > actor.max_hp_milli:
			return _fail("invalid_actor_hp: death lifecycle is outside base_text_v1")
		for field: String in ["energy_milli", "base_damage_milli", "basic_damage_bonus_bp"]:
			if int(actor.get(field)) < 0 or int(actor.get(field)) > MAX_VALUE: return _fail("invalid_actor_stat")
		for status: String in actor.statuses:
			if not EffectCapabilities.BRANCHES.has(status) or actor.statuses[status] < 0 or actor.statuses[status] > MAX_VALUE: return _fail("invalid_actor_status")
	var checkpoint: Dictionary = _checkpoint()
	for actor: EffectActorState in actors: _actors.append(actor.copy_state())
	for owner: int in range(2):
		for binding: Dictionary in _bindings:
			if binding["actor"] != owner: continue
			for rule: Dictionary in binding["rules"]:
				_rules.append({"actor":owner, "card_id":binding["card_id"], "rule":rule.duplicate(true), "next_ms":int(rule["interval_ms"]), "loss":0, "applied":{}})
	_started = true
	_work = 0
	for owner: int in range(2): _dispatch(EffectEvent.new("combat_start", owner, 0))
	return _commit_or_restore(checkpoint)

func dispatch(event: EffectEvent) -> bool:
	errors.clear()
	if not _started or _ended: return _fail("combat_not_active")
	if event == null: return _fail("null_event")
	if not _validate_event(event): return false
	var checkpoint: Dictionary = _checkpoint()
	_work = 0
	_advance(event.at_ms)
	if errors.is_empty():
		_observe_hp_fact(event)
	if errors.is_empty():
		_dispatch(event)
		if event.trigger == "combat_end": _ended = true
	return _commit_or_restore(checkpoint)

func advance_to(timestamp_ms: int) -> bool:
	errors.clear()
	if not _started or _ended: return _fail("combat_not_active")
	if timestamp_ms < _time_ms or timestamp_ms > MAX_TIME_MS: return _fail("invalid_timestamp")
	var checkpoint: Dictionary = _checkpoint()
	_work = 0
	_advance(timestamp_ms)
	return _commit_or_restore(checkpoint)

func snapshot() -> Dictionary:
	var states: Array[Dictionary] = []
	for actor: EffectActorState in _actors: states.append(actor.snapshot())
	return {"at_ms":_time_ms, "started":_started, "ended":_ended, "rng_state":_rng.state_value(), "actors":states, "rules":_rules.duplicate(true), "commands":_commands.duplicate(true)}

func drain_commands() -> Array[Dictionary]:
	var result: Array[Dictionary] = _commands.duplicate(true)
	_commands.clear()
	return result

func _fail(message: String) -> bool:
	errors.append(message)
	return false

func _checkpoint() -> Dictionary:
	var actors: Array[EffectActorState] = []
	for actor: EffectActorState in _actors: actors.append(actor.copy_state())
	return {"actors":actors, "rules":_rules.duplicate(true), "commands":_commands.duplicate(true), "rng":_rng.copy_state(), "time":_time_ms, "started":_started, "ended":_ended}

func _commit_or_restore(checkpoint: Dictionary) -> bool:
	if errors.is_empty(): return true
	_actors = checkpoint["actors"]
	_rules = checkpoint["rules"]
	_commands = checkpoint["commands"]
	_rng = checkpoint["rng"]
	_time_ms = checkpoint["time"]
	_started = checkpoint["started"]
	_ended = checkpoint["ended"]
	return false

func _integer(value: Variant, lower: int = 0, upper: int = MAX_VALUE) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value)) and value >= lower and value <= upper

func _validate_event(event: EffectEvent) -> bool:
	if event.actor < 0 or event.actor > 1: return _fail("invalid_actor")
	if event.at_ms < _time_ms or event.at_ms > MAX_TIME_MS: return _fail("invalid_timestamp")
	if not EffectCapabilities.TRIGGERS.has(event.trigger): return _fail("unsupported_trigger: " + event.trigger)
	if event.trigger in ["combat_start", "interval"]: return _fail("runner_owned_trigger: " + event.trigger)
	var fields: Array[String] = []
	match event.trigger:
		"basic_hit", "skill_hit":
			fields = ["critical"]
			if not event.payload.get("critical") is bool: return _fail("critical must be bool")
		"damage_taken", "heal":
			fields = ["amount_milli", "hp_after_milli"]
			if not _integer(event.payload.get("amount_milli")) or not _integer(event.payload.get("hp_after_milli"), 1, _actors[event.actor].max_hp_milli): return _fail("invalid_hp_fact: zero HP requires unresolved death lifecycle")
			if event.trigger == "heal":
				fields.append("kind")
				if not ["regen", "direct"].has(event.payload.get("kind")): return _fail("unknown heal kind")
		"dodge":
			fields = ["incoming_milli", "reflectable"]
			if not _integer(event.payload.get("incoming_milli"), 1) or not event.payload.get("reflectable") is bool: return _fail("invalid_dodge_payload")
		"status_applied":
			fields = ["status", "stacks"]
			if not EffectCapabilities.BRANCHES.has(event.payload.get("status")) or not _integer(event.payload.get("stacks"), 1): return _fail("invalid_status_payload")
	if event.payload.size() != fields.size(): return _fail("unexpected_payload_fields")
	for field: String in fields:
		if not event.payload.has(field): return _fail("missing_payload: " + field)
	return true

func _observe_hp_fact(event: EffectEvent) -> void:
	if event.trigger not in ["damage_taken", "heal"]: return
	var actor: EffectActorState = _actors[event.actor]
	var amount: int = int(event.payload["amount_milli"])
	var after: int = int(event.payload["hp_after_milli"])
	var expected: int = actor.hp_milli + (amount if event.trigger == "heal" else -amount)
	if expected != after:
		_fail("inconsistent_hp_fact after scheduled ticks")
		return
	actor.hp_milli = after

func _advance(timestamp_ms: int) -> void:
	while errors.is_empty():
		var due: int = MAX_TIME_MS + 1
		for binding: Dictionary in _rules:
			if binding["rule"]["trigger"] == "interval": due = mini(due, int(binding["next_ms"]))
		if due > timestamp_ms: break
		_time_ms = due
		for binding: Dictionary in _rules:
			if binding["rule"]["trigger"] != "interval" or binding["next_ms"] != due: continue
			_execute_rule(binding, EffectEvent.new("interval", binding["actor"], due))
			binding["next_ms"] += int(binding["rule"]["interval_ms"])
			if not errors.is_empty(): break
	if errors.is_empty(): _time_ms = timestamp_ms

func _dispatch(event: EffectEvent) -> void:
	for binding: Dictionary in _rules:
		if binding["actor"] == event.actor and binding["rule"]["trigger"] == event.trigger:
			_execute_rule(binding, event)
			if not errors.is_empty(): return

func _condition(condition: Dictionary, event: EffectEvent) -> bool:
	match condition["kind"]:
		"always": return true
		"critical": return bool(event.payload["critical"])
		"regen": return event.payload["kind"] == "regen" and event.payload["amount_milli"] > 0
		"status": return event.payload["status"] == condition["value"]
		"reflectable": return bool(event.payload["reflectable"])
	return false

func _roll(chance_bp: int) -> bool:
	if chance_bp <= 0: return false
	if chance_bp >= 10000: return true
	# Reject the incomplete top bucket: no modulo bias, no floating-point RNG.
	var value: int = _rng.next_u32()
	while value >= 4294960000: value = _rng.next_u32()
	return value % 10000 < chance_bp

func _execute_rule(binding: Dictionary, event: EffectEvent) -> void:
	var rule: Dictionary = binding["rule"]
	if not _condition(rule["condition"], event): return
	var repeats: int = 1
	var threshold: int = int(rule["loss_threshold_milli"])
	if threshold > 0:
		binding["loss"] += int(event.payload["amount_milli"])
		repeats = int(binding["loss"]) / threshold
		binding["loss"] = int(binding["loss"]) % threshold
	if _work + maxi(1, repeats) > MAX_WORK:
		_fail("effect_work_limit")
		return
	_work += maxi(1, repeats)
	for repeat_index: int in range(repeats):
		if not _roll(int(rule["chance_bp"])): continue
		for action_index: int in range(rule["actions"].size()):
			_apply(rule["actions"][action_index], binding, event, action_index)
			if not errors.is_empty(): return

func _apply(action: Dictionary, binding: Dictionary, event: EffectEvent, action_index: int) -> void:
	var owner: int = binding["actor"]
	var target: int = owner if action["target"] == "self" else 1 - owner
	var actor: EffectActorState = _actors[target]
	var amount: int = int(action["amount"])
	if action["formula"] == "missing_hp_percent":
		amount = maxi(int(action["minimum"]), (actor.max_hp_milli - actor.hp_milli) * int(action["factor_bp"]) / 10000)
	match action["type"]:
		"heal":
			amount = mini(amount, actor.max_hp_milli - actor.hp_milli)
			actor.hp_milli += amount
		"gain_energy": actor.energy_milli += amount
		"modify_stat":
			if int(action["cap"]) > 0:
				amount = mini(amount, maxi(0, int(action["cap"]) - int(binding["applied"].get(action_index, 0))))
			binding["applied"][action_index] = int(binding["applied"].get(action_index, 0)) + amount
			actor.set(action["field"], int(actor.get(action["field"])) + amount)
		"apply_status", "add_shield": actor.statuses[action["field"]] = actor.statuses.get(action["field"], 0) + amount
		"special_handler":
			# Capabilities validate the explicit handler ID before binding.
			amount = int(event.payload["incoming_milli"])
		"deal_damage": pass # Intent only. A future resolver owns mitigation/death.
		_: _fail("unsupported_action: " + action["type"])
	for field: String in ["energy_milli", "base_damage_milli", "basic_damage_bonus_bp"]:
		if int(actor.get(field)) > MAX_VALUE: _fail("state_numeric_limit")
	for value: int in actor.statuses.values():
		if value > MAX_VALUE: _fail("state_numeric_limit")
	if _commands.size() >= 100000: _fail("command_buffer_limit: drain commands")
	if not errors.is_empty(): return
	_commands.append({"at_ms":_time_ms, "source_card":binding["card_id"], "source_actor":owner, "target_actor":target, "action":"deal_damage" if action["type"] == "special_handler" else action["type"], "amount":amount, "unit":action["unit"], "field":action["field"], "damage_kind":action["damage_kind"], "reflectable":action["type"] != "special_handler", "heal_kind":"regen" if action["type"] == "heal" else ""})
