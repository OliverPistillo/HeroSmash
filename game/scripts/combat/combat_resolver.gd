class_name CombatResolver
extends RefCounted
## Chronological simulation. Every mutable object belongs to this single fight.

const BASIC_CHARGE: int = 10000000000
const ENERGY_DENOMINATOR: int = 10000000
var catalog: CombatCatalog
var actors: Dictionary = {}
var initiative: Array[String] = []
var events: Array[Dictionary] = []
var errors: Array[String] = []
var now: int = 0
var sequence: int = 0
var rng: FoundationRng
var _hash: HashingContext
var _record: bool = false
var _status_serial: int = 0
var _horizon: int = 45000

func _init(data: CombatCatalog) -> void:
	catalog = data

func run(input: Variant, record_events: bool = false) -> Dictionary:
	var validator: CombatInput = CombatInput.new()
	if not validator.check(input, catalog): return {"ok":false, "errors":validator.errors}
	actors.clear()
	initiative.clear()
	events.clear()
	errors.clear()
	now = 0
	sequence = 0
	_status_serial = 0
	_record = record_events
	_horizon = int(input["horizon_ms"])
	rng = FoundationRng.new(int(input["seed"]))
	_hash = HashingContext.new()
	_hash.start(HashingContext.HASH_SHA256)
	for row: Dictionary in input["combatants"]:
		var actor: CombatantState = CombatantState.new(row)
		actors[actor.id] = actor
		initiative.append(actor.id)
		for binding: Dictionary in row["bindings"]:
			var effect: Dictionary = catalog.effect(binding["cardId"])
			for rule: Dictionary in effect["rules"]:
				actor.bindings.append({"cardId":binding["cardId"], "rule":rule, "next_due":int(rule["interval_ms"]), "loss_remainder":0})
			for lethal: Dictionary in effect["lethal_rules"]:
				actor.rebirth_charges += int(lethal["charges"])
				actor.rebirth_hp_bp = int(lethal["restore_hp_bp"])
	initiative.sort()
	if roll(5000): initiative.reverse()
	emit("CombatStarted", "", "", {"initiative":initiative.duplicate(), "seed":input["seed"], "rulesetVersion":CombatCatalog.RULESET_VERSION, "canonicalDataVersion":CombatCatalog.DATA_VERSION})
	for id: String in initiative:
		for row: Dictionary in input["combatants"]:
			if row["id"] == id:
				for status: Dictionary in row["initial_statuses"]: apply_status(status["source"], id, status, 0, 0)
		trigger(actors[id], "combat_start", {}, 0, 0)
	while errors.is_empty():
		process_boundary()
		check_invariants()
		if not errors.is_empty() or living_count() < 2 or now >= _horizon: break
		var next: int = next_boundary()
		if next <= now:
			errors.append("clock_failed_to_advance")
			break
		advance(next - now)
		now = next
	var outcome: String = "timeout"
	var winner: String = ""
	if living_count() == 0: outcome = "draw"
	elif living_count() == 1:
		outcome = "win"
		for id: String in initiative:
			if actors[id].alive: winner = id
	if not errors.is_empty(): outcome = "error"
	var identities: Array = actors.keys()
	identities.sort()
	var final: Array[Dictionary] = []
	for id: String in identities: final.append(actors[id].snapshot(now))
	var first: CombatantState = actors[identities[0]]
	var second: CombatantState = actors[identities[1]]
	var hp_comparison: int = first.hp_milli * int(second.stats["max_hp_milli"]) - second.hp_milli * int(first.stats["max_hp_milli"])
	var leader: String = "" if hp_comparison == 0 else first.id if hp_comparison > 0 else second.id
	var result: Dictionary = {"outcome":outcome, "winner":winner, "timeout_leader":leader if outcome == "timeout" else "", "duration_ms":now, "event_count":sequence + 1, "rng_state":rng.state_value(), "final":final}
	emit("CombatEnded", "", "", {"outcome":outcome, "winner":winner, "duration_ms":now})
	return {"ok":errors.is_empty(), "errors":errors.duplicate(), "result":result, "eventHash":_hash.finish().hex_encode(), "resultHash":CombatJson.digest(result), "events":events if _record else []}

func opponent(actor: CombatantState) -> CombatantState:
	return actors[initiative[1] if actor.id == initiative[0] else initiative[0]]

func emit(kind: String, source: String, target: String, payload: Dictionary, parent: int = 0) -> int:
	sequence += 1
	if sequence > int(catalog.ruleset["maxEvents"]):
		if not "event_limit" in errors: errors.append("event_limit")
		return sequence
	var event: Dictionary = CombatEvent.value(sequence, now, kind, source, target, payload, parent)
	_hash.update((CombatJson.encode(event) + "\n").to_utf8_buffer())
	if _record: events.append(event)
	return sequence

func roll(chance_bp: int) -> bool:
	if chance_bp <= 0: return false
	if chance_bp >= 10000: return true
	var draw: int = rng.next_u32()
	while draw >= 4294960000: draw = rng.next_u32()
	return draw % 10000 < chance_bp

func living_count() -> int:
	var total: int = 0
	for actor: CombatantState in actors.values():
		if actor.alive: total += 1
	return total

func status_sum(actor: CombatantState, kind: String) -> int:
	var result: int = 0
	for status: StatusInstance in actor.statuses:
		if status.type == kind: result += status.magnitude * status.stacks
	return result

func stunned(actor: CombatantState) -> bool:
	return status_sum(actor, "stun") > 0

func ice_rate(actor: CombatantState) -> int:
	return maxi(int(catalog.ruleset["minimumIceRateBp"]), 10000 - status_sum(actor, "ice"))

func basic_rate(actor: CombatantState) -> int:
	return 0 if stunned(actor) else mini(int(actor.stats["attack_speed_milli"]), 4000) * ice_rate(actor)

func energy_rate(actor: CombatantState) -> int:
	return int(actor.stats["energy_regen_milli"]) * (int(catalog.ruleset["stunnedEnergyRateBp"]) if stunned(actor) else ice_rate(actor))

func advance(delta: int) -> void:
	for id: String in initiative:
		var actor: CombatantState = actors[id]
		if not actor.alive: continue
		var seen: Dictionary = {}
		for status: StatusInstance in actor.statuses: seen[status.type] = true
		for kind: String in seen:
			actor.metrics["status_uptime_ms"][kind] = int(actor.metrics["status_uptime_ms"].get(kind, 0)) + delta
		actor.basic_remaining -= delta * basic_rate(actor)
		if not stunned(actor): actor.skill_remaining = maxi(0, actor.skill_remaining - delta)
		var numerator: int = actor.energy_remainder + delta * energy_rate(actor)
		@warning_ignore("integer_division")
		actor.energy_milli += numerator / ENERGY_DENOMINATOR
		actor.energy_remainder = numerator % ENERGY_DENOMINATOR
		if actor.energy_milli >= int(catalog.ruleset["energyCapMilli"]):
			actor.energy_milli = int(catalog.ruleset["energyCapMilli"])
			actor.energy_remainder = 0

func next_boundary() -> int:
	var next: int = _horizon
	for id: String in initiative:
		var actor: CombatantState = actors[id]
		if not actor.alive: continue
		for status: StatusInstance in actor.statuses:
			next = mini(next, status.expires_at)
			if status.interval_ms > 0 and status.next_tick <= status.expires_at: next = mini(next, status.next_tick)
		for binding: Dictionary in actor.bindings:
			if binding["rule"]["trigger"] == "interval": next = mini(next, int(binding["next_due"]))
		if not stunned(actor):
			next = mini(next, now + CombatJson.ceil_div(actor.basic_remaining, basic_rate(actor)))
			var missing: int = int(actor.skill["cost_milli"]) - actor.energy_milli
			if missing <= 0 or energy_rate(actor) > 0:
				var energy_wait: int = 0 if missing <= 0 else CombatJson.ceil_div(missing * ENERGY_DENOMINATOR - actor.energy_remainder, energy_rate(actor))
				next = mini(next, now + maxi(actor.skill_remaining, energy_wait))
	return next

func process_boundary() -> void:
	# All due ticks are earned before damage is drained: simultaneous lethal DoTs can draw.
	var ticks: Array[DamageEvent] = []
	for id: String in initiative:
		var actor: CombatantState = actors[id]
		if not actor.alive: continue
		for status: StatusInstance in actor.statuses:
			if status.interval_ms > 0 and status.next_tick == now and now <= status.expires_at:
				var numerator: int = status.magnitude * status.stacks * status.interval_ms + status.tick_remainder
				@warning_ignore("integer_division")
				var amount: int = numerator / 1000
				status.tick_remainder = numerator % 1000
				status.next_tick += status.interval_ms
				var parent: int = emit("StatusTick", status.source, id, {"status_id":status.id, "type":status.type, "amount_milli":amount, "stacks":status.stacks})
				ticks.append(DamageEvent.new(status.source, id, amount, "magic", ["dot"], false, false, false, parent))
	for tick: DamageEvent in ticks: damage(tick)
	for id: String in initiative:
		var actor: CombatantState = actors[id]
		for status: StatusInstance in actor.statuses.duplicate():
			if status.expires_at <= now: expire(actor, status, "time", 0)
	for id: String in initiative:
		var actor: CombatantState = actors[id]
		if actor.alive: trigger(actor, "interval", {}, 0, 0)
	# A basic proc or opponent's hit may make an already visited actor skill-ready.
	# Drain readiness in stable rounds at this timestamp, without inventing a frame delay.
	var acted: bool = true
	var rounds: int = 0
	while acted and errors.is_empty():
		acted = false
		rounds += 1
		if rounds > 4:
			errors.append("same_time_action_limit")
			break
		for id: String in initiative:
			var actor: CombatantState = actors[id]
			if not actor.alive or not opponent(actor).alive or stunned(actor): continue
			if actor.skill_remaining == 0 and actor.energy_milli >= int(actor.skill["cost_milli"]):
				act(actor, true)
				acted = true
			elif actor.basic_remaining <= 0:
				act(actor, false)
				acted = true

func act(actor: CombatantState, skill: bool) -> void:
	var enemy: CombatantState = opponent(actor)
	var parent: int
	var amount: int
	var kind: String = "physical"
	if skill:
		actor.skill_remaining = int(actor.skill["cooldown_ms"])
		actor.energy_milli -= int(actor.skill["cost_milli"])
		actor.metrics["skill_casts"] += 1
		parent = emit("SkillCast", actor.id, enemy.id, {"name":actor.skill["name"], "energy_milli":actor.energy_milli})
		trigger(actor, "skill_cast", {}, parent, 0)
		kind = actor.skill["damage_type"]
		amount = multiply_bp(int(actor.stats["attack_milli"] if kind == "physical" else actor.stats["focus_milli"]), int(actor.skill["power_bp"]))
	else:
		actor.basic_remaining += BASIC_CHARGE
		actor.metrics["basic_attacks"] += 1
		parent = emit("BasicAttack", actor.id, enemy.id, {})
		trigger(actor, "basic_attack", {}, parent, 0)
		amount = multiply_bp(int(actor.stats["attack_milli"]), 10000 + actor.basic_bonus_bp)
	var hit: Dictionary = damage(DamageEvent.new(actor.id, enemy.id, amount, kind, ["skill" if skill else "basic"], true, kind == "physical", true, parent))
	if not hit.get("hit", false): return
	if skill and enemy.alive and actor.skill["status"] != "" and enemy.generation == int(hit["target_generation"]):
		apply_status(actor.id, enemy.id, hero_status(actor), int(hit["sequence"]), 0)
	if actor.alive: trigger(actor, "skill_hit" if skill else "basic_hit", {"critical":hit["critical"]}, int(hit["sequence"]), 0)

func hero_status(actor: CombatantState) -> Dictionary:
	var kind: String = actor.skill["status"]
	var magnitude: int = 1
	if kind in ["toxin", "burn"]: magnitude = int(actor.skill["dot_milli_per_second"])
	elif kind == "wound": magnitude = int(catalog.ruleset["legacyWoundFallbackBp"])
	elif kind == "ice": magnitude = int(catalog.ruleset["legacyIceFallbackBp"])
	return {"type":kind, "duration_ms":actor.skill["duration_ms"], "stacks":1, "max_stacks":catalog.ruleset["legacyStatusMaxStacks"], "magnitude":magnitude, "stacking_policy":"refresh_duration" if kind == "stun" else "add_stack_and_refresh", "refresh_policy":"extend_if_longer", "interval_ms":catalog.ruleset["dotIntervalMs"] if kind in ["toxin", "burn"] else 0, "debuff":true, "metadata":{"origin":"legacy_hero_skill", "heroId":actor.hero_id}}

func damage(intent: DamageEvent) -> Dictionary:
	if intent.depth > int(catalog.ruleset["maxReactionDepth"]):
		errors.append("reaction_depth_limit")
		return {}
	var source: CombatantState = actors[intent.source]
	var target: CombatantState = actors[intent.target]
	if not target.alive or not errors.is_empty(): return {}
	var critical: bool = false
	var amount: int = intent.amount_milli
	if intent.can_crit:
		source.metrics["crit_attempts"] += 1
		critical = roll(mini(int(catalog.ruleset["criticalCapBp"]), int(source.stats["crit_bp"])))
		if critical: amount = multiply_bp(amount, int(source.stats["crit_multiplier_bp"]))
	var offensive: int = amount
	if amount > 1000000000:
		errors.append("damage_numeric_limit")
		return {}
	amount = multiply_bp(amount, 10000 + status_sum(target, "wound"))
	if intent.damage_type == "physical": amount = maxi(0, amount - int(target.stats["armor_milli"]))
	if "basic" in intent.tags or "skill" in intent.tags: amount = maxi(int(catalog.ruleset["minimumAttackDamageMilli"]), amount)
	if intent.can_dodge and intent.damage_type == "physical":
		target.metrics["dodge_attempts"] += 1
		if roll(int(target.stats["dodge_bp"])):
			target.metrics["dodge_count"] += 1
			var dodged: int = emit("Dodged", source.id, target.id, {"incoming_milli":amount, "tags":intent.tags}, intent.parent_sequence)
			trigger(target, "dodge", {"reflectable":intent.reflectable, "incoming_milli":amount}, dodged, intent.depth + 1)
			return {"hit":false}
	if critical: source.metrics["crit_count"] += 1
	var remaining: int = amount
	var absorbed: int = 0
	for status: StatusInstance in target.statuses.duplicate():
		if status.type != "shield" or remaining == 0: continue
		var taken: int = mini(remaining, status.capacity_milli)
		status.capacity_milli -= taken
		remaining -= taken
		absorbed += taken
		emit("ShieldAbsorbed", source.id, target.id, {"status_id":status.id, "absorbed_milli":taken, "capacity_milli":status.capacity_milli}, intent.parent_sequence)
		if status.capacity_milli == 0: expire(target, status, "absorption", intent.parent_sequence)
	var actual: int = mini(remaining, target.hp_milli)
	var generation: int = target.generation
	target.hp_milli -= actual
	source.metrics[intent.damage_type + "_damage_milli"] += actual
	if "dot" in intent.tags: source.metrics["dot_damage_milli"] += actual
	target.metrics["damage_taken_milli"] += actual
	target.metrics["shield_absorbed_milli"] += absorbed
	var parent: int = emit("DamageApplied", source.id, target.id, {"damage_type":intent.damage_type, "tags":intent.tags, "attempted_milli":intent.amount_milli, "offensive_milli":offensive, "mitigated_milli":amount, "absorbed_milli":absorbed, "actual_milli":actual, "overkill_milli":remaining - actual, "hp_milli":target.hp_milli, "critical":critical, "depth":intent.depth}, intent.parent_sequence)
	trigger(target, "damage_taken", {"actual_milli":actual}, parent, intent.depth + 1)
	if target.hp_milli == 0: lethal(target, intent, parent)
	return {"hit":true, "critical":critical, "sequence":parent, "target_generation":generation}

func lethal(target: CombatantState, intent: DamageEvent, parent: int) -> void:
	target.metrics["lethal_source"] = intent.source + ":" + ",".join(intent.tags)
	var notified: int = emit("LethalReached", intent.source, target.id, {"generation":target.generation, "tags":intent.tags}, parent)
	if target.prevention_charges > 0:
		target.prevention_charges -= 1
		target.hp_milli = target.prevention_hp
		target.metrics["death_prevention_count"] += 1
		emit("DeathPrevented", target.id, target.id, {"hp_milli":target.hp_milli, "charges":target.prevention_charges, "origin":"mechanics_fixture"}, notified)
	elif target.rebirth_charges > 0:
		target.rebirth_charges -= 1
		target.generation += 1
		target.metrics["rebirth_count"] += 1
		var reborn: int = emit("RebirthTriggered", target.id, target.id, {"cardId":"legacy_120", "generation":target.generation}, notified)
		for status: StatusInstance in target.statuses.duplicate():
			if status.debuff: expire(target, status, "dispel", reborn)
		target.hp_milli = maxi(1, multiply_bp(int(target.stats["max_hp_milli"]), target.rebirth_hp_bp))
		emit("CombatantRevived", target.id, target.id, {"hp_milli":target.hp_milli, "generation":target.generation}, reborn)
	else:
		target.alive = false
		target.metrics["ko_count"] += 1
		emit("CombatantKO", intent.source, target.id, {"generation":target.generation, "tags":intent.tags}, notified)
		for status: StatusInstance in target.statuses.duplicate(): expire(target, status, "death", notified)

func trigger(actor: CombatantState, kind: String, context: Dictionary, parent: int, depth: int) -> void:
	if depth > int(catalog.ruleset["maxReactionDepth"]):
		errors.append("reaction_depth_limit")
		return
	if not actor.alive or not errors.is_empty(): return
	# Local ordered reaction queue: children finish before the next parent action.
	var queue: Array[Dictionary] = []
	for binding: Dictionary in actor.bindings:
		var rule: Dictionary = binding["rule"]
		if rule["trigger"] != kind: continue
		if kind == "interval":
			if binding["next_due"] != now: continue
			binding["next_due"] += int(rule["interval_ms"])
		var count: int = 1
		if int(rule["loss_threshold_milli"]) > 0:
			binding["loss_remainder"] += int(context.get("actual_milli", 0))
			@warning_ignore("integer_division")
			count = int(binding["loss_remainder"]) / int(rule["loss_threshold_milli"])
			binding["loss_remainder"] %= int(rule["loss_threshold_milli"])
		var condition: Dictionary = rule["condition"]
		if condition["kind"] == "critical" and not context.get("critical", false): continue
		if condition["kind"] == "reflectable" and not context.get("reflectable", false): continue
		if condition["kind"] == "regen" and context.get("heal_kind") != "regen": continue
		if condition["kind"] == "status" and context.get("status") != condition["value"]: continue
		for occurrence: int in range(count):
			if not roll(int(rule["chance_bp"])): continue
			for action: Dictionary in rule["actions"]: queue.append({"action":action, "cardId":binding["cardId"]})
	for reaction: Dictionary in queue:
		if not actor.alive or not errors.is_empty(): break
		var action_parent: int = emit("EffectTriggered", actor.id, actor.id, {"cardId":reaction["cardId"], "trigger":kind, "action":reaction["action"]["type"]}, parent)
		execute_action(actor, reaction["action"], context, kind, action_parent, depth + 1)

func execute_action(actor: CombatantState, action: Dictionary, context: Dictionary, trigger_kind: String, parent: int, depth: int) -> void:
	var target: CombatantState = actor if action["target"] == "self" else opponent(actor)
	var amount: int = int(action["amount"])
	match action["type"]:
		"modify_stat":
			if action["field"] == "base_damage_milli": actor.stats["attack_milli"] += amount
			elif action["field"] == "basic_damage_bonus_bp": actor.basic_bonus_bp = mini(int(action["cap"]), actor.basic_bonus_bp + amount)
			else: errors.append("unknown_stat_operator")
		"gain_energy":
			actor.energy_milli = mini(int(catalog.ruleset["energyCapMilli"]), actor.energy_milli + amount)
			if actor.energy_milli == int(catalog.ruleset["energyCapMilli"]): actor.energy_remainder = 0
			emit("EnergyGained", actor.id, actor.id, {"energy_milli":actor.energy_milli}, parent)
		"heal":
			if action["formula"] == "missing_hp_percent": amount = maxi(int(action["minimum"]), multiply_bp(int(target.stats["max_hp_milli"]) - target.hp_milli, int(action["factor_bp"])))
			heal(actor, target, amount, "regen" if trigger_kind == "interval" else "effect", parent, depth)
		"add_shield", "apply_status":
			var definition: Dictionary = actor.status_templates[action["field"]].duplicate(true)
			definition["stacks"] = mini(amount, int(definition["max_stacks"]))
			apply_status(actor.id, target.id, definition, parent, depth)
		"deal_damage":
			damage(DamageEvent.new(actor.id, target.id, amount, action["damage_kind"], ["secondary"], false, false, false, parent, depth))
		"special_handler":
			if action["handler"] == "reflect_incoming_once": damage(DamageEvent.new(actor.id, target.id, int(context["incoming_milli"]), "magic", ["reflected"], false, false, false, parent, depth))
			else: errors.append("unknown_special_handler")
		_: errors.append("unknown_effect_operator")

func heal(source: CombatantState, target: CombatantState, amount: int, kind: String, parent: int, depth: int) -> void:
	if not target.alive or target.hp_milli <= 0: return
	var actual: int = mini(amount, int(target.stats["max_hp_milli"]) - target.hp_milli)
	if actual <= 0: return
	target.hp_milli += actual
	source.metrics["healing_milli"] += actual
	var fact: int = emit("HealApplied", source.id, target.id, {"actual_milli":actual, "heal_kind":kind, "hp_milli":target.hp_milli}, parent)
	trigger(source, "heal", {"heal_kind":kind}, fact, depth + 1)

func apply_status(source_id: String, target_id: String, definition: Dictionary, parent: int, depth: int) -> void:
	var target: CombatantState = actors[target_id]
	if not target.alive or not errors.is_empty(): return
	var existing: StatusInstance = null
	for status: StatusInstance in target.statuses:
		if status.type == definition["type"] and status.source == source_id:
			existing = status
			break
	var policy: String = definition["stacking_policy"]
	if existing != null and policy == "stronger_wins" and int(definition["magnitude"]) <= existing.magnitude:
		emit("StatusIgnored", source_id, target_id, {"status_id":existing.id, "reason":"not_stronger"}, parent)
		return
	if existing != null and policy in ["replace", "stronger_wins"]:
		expire(target, existing, "replacement", parent)
		existing = null
	if existing == null or policy == "independent_instances":
		if target.statuses.size() >= 64:
			errors.append("status_instance_limit")
			return
		_status_serial += 1
		existing = StatusInstance.new("status_%06d" % _status_serial, definition, source_id, target_id, now)
		target.statuses.append(existing)
	else:
		if policy in ["add_stack", "add_stack_and_refresh"]: existing.stacks = mini(existing.max_stacks, existing.stacks + int(definition["stacks"]))
		if policy == "add_stack_and_refresh": existing.magnitude = maxi(existing.magnitude, int(definition["magnitude"]))
		if policy in ["refresh_duration", "add_stack_and_refresh"]:
			if definition["refresh_policy"] == "reset": existing.expires_at = now + int(definition["duration_ms"])
			elif definition["refresh_policy"] == "extend_if_longer": existing.expires_at = maxi(existing.expires_at, now + int(definition["duration_ms"]))
	var source: CombatantState = actors[source_id]
	source.metrics["status_applications"] += 1
	if existing.type == "shield": source.metrics["shield_generated_milli"] += existing.capacity_milli
	var fact: int = emit("StatusApplied", source_id, target_id, existing.snapshot(now), parent)
	trigger(source, "status_applied", {"status":existing.type}, fact, depth + 1)

func expire(target: CombatantState, status: StatusInstance, reason: String, parent: int) -> void:
	target.statuses.erase(status)
	emit("StatusExpired", status.source, target.id, {"status_id":status.id, "type":status.type, "reason":reason}, parent)

func check_invariants() -> void:
	for actor: CombatantState in actors.values():
		if actor.hp_milli < 0 or actor.hp_milli > int(actor.stats["max_hp_milli"]) or actor.alive != (actor.hp_milli > 0): errors.append("hp_lifecycle_invariant")
		if actor.energy_milli < 0 or actor.energy_milli > int(catalog.ruleset["energyCapMilli"]) or actor.metrics["ko_count"] > 1: errors.append("resource_or_duplicate_death_invariant")
		for status: StatusInstance in actor.statuses:
			if status.stacks <= 0 or status.stacks > status.max_stacks or status.expires_at < now or status.capacity_milli < 0: errors.append("status_invariant")

static func multiply_bp(value: int, basis_points: int) -> int:
	@warning_ignore("integer_division")
	return value * basis_points / 10000
