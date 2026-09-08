extends SceneTree

var failures: Array[String] = []
var assertions: int = 0
var catalog: CanonicalCatalog = CanonicalCatalog.new()
const PILOTS: Array[int] = [2, 5, 10, 20, 28, 40, 49, 77, 90, 92, 97, 111, 115, 132, 149]

func check(condition: bool, message: String) -> void:
	assertions += 1
	if not condition: failures.append(message)

func actor(hp: int = 1000000, maximum: int = 1000000) -> EffectActorState:
	var result: EffectActorState = EffectActorState.new()
	result.hp_milli = hp
	result.max_hp_milli = maximum
	return result

func runner(ids: Array[int], seed_value: int = 1, owner: int = 0, hp: int = 500000) -> EffectRunner:
	var result: EffectRunner = EffectRunner.new(seed_value)
	for id: int in ids:
		check(result.bind(owner, catalog.effect("legacy_%03d" % id), "base_text_v1"), "bind %d: %s" % [id, str(result.errors)])
	var actors: Array[EffectActorState] = [actor(hp), actor(hp)]
	check(result.start(actors), "start: " + str(result.errors))
	return result

func send(sim: EffectRunner, trigger: String, payload: Dictionary = {}, owner: int = 0, at_ms: int = 0) -> void:
	check(sim.dispatch(EffectEvent.new(trigger, owner, at_ms, payload)), trigger + ": " + str(sim.errors))

func state(sim: EffectRunner, owner: int = 0) -> Dictionary:
	return sim.snapshot()["actors"][owner]

func reject(sim: EffectRunner, event: EffectEvent, message: String) -> void:
	var before: Dictionary = sim.snapshot()
	check(not sim.dispatch(event) and not sim.errors.is_empty(), "reject " + message)
	check(sim.snapshot() == before, "transactional state/RNG/timers/log " + message)

func _initialize() -> void:
	check(catalog.load_directory(), "catalog " + str(catalog.errors))
	if not catalog.errors.is_empty():
		_finish()
		return
	_test_stats_energy()
	_test_threshold_heals()
	_test_statuses_reflection()
	_test_time_and_order()
	_test_composition()
	_test_errors()
	_test_replay_symmetry()
	_finish()

func _test_stats_energy() -> void:
	var sim: EffectRunner = runner([2, 10])
	check(state(sim)["base_damage_milli"] == 25000, "002 literal +5 base damage")
	for index: int in range(10): send(sim, "basic_attack")
	check(state(sim)["basic_damage_bonus_bp"] == 2000, "010 +4% stacks cap at20%")
	check(sim.snapshot()["rng_state"] == 1, "certain modifiers do not draw RNG")
	var energy: EffectRunner = runner([5])
	for index: int in range(100): send(energy, "basic_attack")
	check(state(energy)["energy_milli"] == 84000, "005 known seed1: 56/100 procs x1.5 MP")
	check(energy.snapshot()["rng_state"] == 2146152485, "known RNG state after100 eligible draws")
	var rejected_bucket: EffectRunner = runner([5], 653637408)
	send(rejected_bucket, "basic_attack")
	check(rejected_bucket.snapshot()["rng_state"] == 1012239698, "unbiased RNG rejects uint32 max and consumes next vector")
	check(state(rejected_bucket)["energy_milli"] == 0, "known rejected-bucket proc result")

func _test_threshold_heals() -> void:
	var sim: EffectRunner = runner([20], 1, 0, 1000000)
	send(sim, "damage_taken", {"amount_milli":399999, "hp_after_milli":600001})
	check(state(sim)["energy_milli"] == 0, "020 one milli below threshold")
	send(sim, "heal", {"amount_milli":100000, "hp_after_milli":700001, "kind":"direct"})
	send(sim, "damage_taken", {"amount_milli":1, "hp_after_milli":700000})
	check(state(sim)["energy_milli"] == 6000, "020 threshold retains loss through heal")
	send(sim, "damage_taken", {"amount_milli":650000, "hp_after_milli":50000})
	check(state(sim)["energy_milli"] == 12000 and sim.snapshot()["rules"][0]["loss"] == 250000, "020 remainder after total1050 HP lost")
	var multi: EffectRunner = EffectRunner.new(1)
	check(multi.bind(0, catalog.effect("legacy_020"), "base_text_v1"), "multi-threshold binding")
	check(multi.start([actor(2000000, 2000000), actor()]), "multi-threshold start")
	send(multi, "damage_taken", {"amount_milli":850000, "hp_after_milli":1150000})
	check(state(multi)["energy_milli"] == 12000 and multi.snapshot()["rules"][0]["loss"] == 50000, "020 multiple crossings in one fact")
	var crit: EffectRunner = runner([40])
	send(crit, "basic_hit", {"critical":false})
	check(state(crit)["hp_milli"] == 500000, "040 no heal without crit")
	send(crit, "basic_hit", {"critical":true})
	send(crit, "skill_hit", {"critical":true})
	check(state(crit)["hp_milli"] == 520000, "040 basic and skill Crit each heal10")
	var skill: EffectRunner = runner([92], 1, 0, 980000)
	send(skill, "skill_cast")
	check(state(skill)["hp_milli"] == 1000000 and skill.snapshot()["commands"][0]["amount"] == 20000, "092 cast heal capped, reports actual amount")
	var minimum: EffectRunner = runner([28], 1, 0, 950000)
	check(minimum.advance_to(1000), "028 tick")
	check(state(minimum)["hp_milli"] == 951000, "028 minimum1 HP exceeds1% missing")
	var cap: EffectRunner = runner([28], 1, 0, 999500)
	check(cap.advance_to(2000), "028 cap ticks")
	check(state(cap)["hp_milli"] == 1000000, "028 never overheals")
	check(cap.snapshot()["commands"][1]["amount"] == 0, "028 zero actual heal at fullHP")

func _test_statuses_reflection() -> void:
	var reflect: EffectRunner = runner([49])
	send(reflect, "dodge", {"incoming_milli":12345, "reflectable":false})
	check(reflect.snapshot()["rng_state"] == 1 and reflect.snapshot()["commands"].is_empty(), "049 nonreflectable input consumes no RNG")
	for index: int in range(100): send(reflect, "dodge", {"incoming_milli":12345, "reflectable":true})
	check(reflect.snapshot()["commands"].size() == 51, "049 known51/100 full-reflection intents")
	for command: Dictionary in reflect.snapshot()["commands"]:
		check(command["amount"] == 12345 and command["damage_kind"] == "magic" and not command["reflectable"] and command["target_actor"] == 1, "049 handler amount/type/target/recursion flag")
	check(state(reflect, 1)["hp_milli"] == 500000, "damage intent does not invent mitigation")
	var shield: EffectRunner = runner([77])
	send(shield, "heal", {"amount_milli":1, "hp_after_milli":500001, "kind":"direct"})
	check(shield.snapshot()["rng_state"] == 1, "077 direct heal not Regen")
	send(shield, "heal", {"amount_milli":0, "hp_after_milli":500001, "kind":"regen"})
	check(shield.snapshot()["rng_state"] == 1, "077 zero heal no proc draw")
	for index: int in range(100): send(shield, "heal", {"amount_milli":1, "hp_after_milli":500002 + index, "kind":"regen"})
	check(state(shield)["statuses"]["shield"] == 116, "077 known29/100 procs x4 shield stacks")
	var cross: EffectRunner = runner([149])
	send(cross, "status_applied", {"status":"ice", "stacks":1})
	check(cross.snapshot()["rng_state"] == 1, "149 non-Wound does not draw")
	for index: int in range(100): send(cross, "status_applied", {"status":"wound", "stacks":1})
	check(state(cross, 1)["statuses"]["toxin"] == 116, "149 Wound events yield29 procs x4 Toxin")
	var toxin: EffectRunner = runner([115])
	check(toxin.advance_to(3000), "115 intervals")
	check(state(toxin, 1)["statuses"]["toxin"] == 12 and state(toxin, 1)["hp_milli"] == 500000, "115 stack application without invented tick damage")

func _test_time_and_order() -> void:
	var whole: EffectRunner = runner([28, 90, 115])
	var split: EffectRunner = runner([28, 90, 115])
	check(whole.advance_to(2000), "advance whole2s")
	for time: int in [1, 499, 500, 777, 999, 1000, 1001, 1500, 1999, 2000]: check(split.advance_to(time), "partitioned advance")
	check(whole.snapshot() == split.snapshot(), "timer partition independence including command order")
	check(state(whole)["hp_milli"] == 509950, "028 two missing-HP ticks 5000+4950")
	var commands: Array = whole.snapshot()["commands"]
	check(commands.size() == 8 and commands[0]["at_ms"] == 500 and commands[0]["source_card"] == "legacy_090", "090 first tick after500ms")
	check(commands[1]["source_card"] == "legacy_028" and commands[2]["source_card"] == "legacy_090" and commands[3]["source_card"] == "legacy_115", "same-time declared binding order")
	var wound: EffectRunner = EffectRunner.new(42)
	check(wound.bind(0, catalog.effect("legacy_090"), "base_text_v1"), "090 bind")
	var target: EffectActorState = actor()
	target.statuses["wound"] = 7
	check(wound.start([actor(), target]), "090 start")
	check(wound.advance_to(500), "090 single tick")
	check(state(wound, 1)["statuses"]["wound"] == 7, "090 no Wound consumption")
	var boundary: EffectRunner = runner([28, 92])
	send(boundary, "skill_cast", {}, 0, 1000)
	check(boundary.snapshot()["commands"][0]["source_card"] == "legacy_028" and boundary.snapshot()["commands"][1]["source_card"] == "legacy_092", "scheduled tick precedes external event")
	send(boundary, "combat_end", {}, 0, 1000)
	var before: Dictionary = boundary.snapshot()
	check(not boundary.advance_to(2000) and boundary.snapshot() == before, "combat_end stops future intervals")

func _test_composition() -> void:
	# Synthetic rule proves composition/caps; it is not a new card definition.
	var record: Dictionary = catalog.effect("legacy_002").snapshot()
	var rule: Dictionary = record["rules"][0]
	rule["trigger"] = "basic_attack"
	rule["actions"][0]["cap"] = 10000
	var bonus: Dictionary = catalog.effect("legacy_010").rules()[0]["actions"][0]
	bonus["cap"] = 800
	rule["actions"].append(bonus)
	var sim: EffectRunner = EffectRunner.new(1)
	check(sim.bind(0, EffectDefinition.new(record), "base_text_v1"), "synthetic composition bind")
	check(sim.start([actor(), actor()]), "synthetic composition start")
	for index: int in range(3): send(sim, "basic_attack")
	check(state(sim)["base_damage_milli"] == 30000 and state(sim)["basic_damage_bonus_bp"] == 800, "composed actions have independent caps")
	check(sim.snapshot()["commands"][0]["field"] == "base_damage_milli" and sim.snapshot()["commands"][1]["field"] == "basic_damage_bonus_bp", "composed action order")
	for chance: int in [0, 10000]:
		var proc: Dictionary = catalog.effect("legacy_005").snapshot()
		proc["rules"][0]["chance_bp"] = chance
		var certain: EffectRunner = EffectRunner.new(42)
		check(certain.bind(0, EffectDefinition.new(proc), "base_text_v1"), "probability endpoint bind")
		check(certain.start([actor(), actor()]), "probability endpoint start")
		send(certain, "basic_attack")
		check(certain.snapshot()["rng_state"] == 42 and state(certain)["energy_milli"] == (1500 if chance == 10000 else 0), "probability endpoints consume no RNG")

func _test_errors() -> void:
	var blank: EffectRunner = EffectRunner.new(1)
	for id: int in [1, 97, 111, 132]:
		check(not blank.bind(0, catalog.effect("legacy_%03d" % id), "base_text_v1") and blank.errors[0].contains("unsupported_semantics"), "unresolved/unreviewed error " + str(id))
	check(not blank.bind(0, catalog.effect("legacy_002"), "base_text_v1", 1), "all numbered progression explicitly rejected")
	check(not blank.bind(0, catalog.effect("legacy_002"), ""), "profile opt-in required")
	check(not blank.bind(2, catalog.effect("legacy_002"), "base_text_v1"), "invalid binding actor")
	check(not blank.bind(0, null, "base_text_v1"), "null effect")
	var malformed: Dictionary = catalog.effect("legacy_002").snapshot()
	malformed["rules"][0]["actions"][0]["amount"] = "5000"
	check(not blank.bind(0, EffectDefinition.new(malformed), "base_text_v1"), "manual malformed typed definition rejected")
	for id: int in range(1, 151):
		var definition: EffectDefinition = catalog.effect("legacy_%03d" % id)
		if definition.lifecycle != "implemented":
			check(not blank.bind(0, definition, "base_text_v1") and blank.errors[0].contains("unsupported_semantics"), "all138 unavailable semantics fail explicitly")
	check(blank.bind(0, catalog.effect("legacy_002"), "base_text_v1"), "valid binding")
	check(not blank.bind(0, catalog.effect("legacy_002"), "base_text_v1"), "duplicate copy rejected")
	check(not blank.start([actor(-1), actor()]), "invalid initialHP")
	check(blank.start([actor(), actor()]), "retry valid start")
	check(not blank.start([actor(), actor()]), "duplicate start")
	check(not blank.bind(1, catalog.effect("legacy_002"), "base_text_v1"), "late binding rejected")
	var sim: EffectRunner = runner([5, 28])
	reject(sim, EffectEvent.new("basic_hit", 0, 0, {"critical":1}), "bool payload")
	reject(sim, EffectEvent.new("basic_attack", 0, 0, {"extra":true}), "unknown payload")
	reject(sim, EffectEvent.new("basic_attack", 2, 0), "actor2")
	reject(sim, EffectEvent.new("basic_attack", 0, -1), "negative time")
	reject(sim, EffectEvent.new("interval", 0, 0), "external timer spoof")
	reject(sim, EffectEvent.new("combat_start", 0, 0), "external start spoof")
	reject(sim, EffectEvent.new("shop_enter", 0, 0), "unimplemented future trigger")
	reject(sim, EffectEvent.new("damage_taken", 0, 0, {"amount_milli":500000, "hp_after_milli":0}), "unresolved death")
	reject(sim, EffectEvent.new("damage_taken", 0, 0, {"amount_milli":true, "hp_after_milli":400000}), "boolean amount")
	reject(sim, EffectEvent.new("heal", 0, 0, {"amount_milli":1.5, "hp_after_milli":500002, "kind":"regen"}), "fractional amount")
	reject(sim, EffectEvent.new("heal", 0, 1000, {"amount_milli":1, "hp_after_milli":500001, "kind":"regen"}), "inconsistent post-tick HP fact rolls back timer heal")
	check(sim.advance_to(1000), "valid timer after rejected event")
	reject(sim, EffectEvent.new("basic_attack", 0, 999), "time reversal")
	var before: Dictionary = sim.snapshot()
	check(not sim.advance_to(EffectRunner.MAX_TIME_MS + 1) and sim.snapshot() == before, "time upper bound")
	var work: EffectRunner = runner([28, 90, 115])
	before = work.snapshot()
	check(not work.advance_to(EffectRunner.MAX_TIME_MS) and work.errors[0].contains("work_limit"), "bounded catch-up workload")
	check(work.snapshot() == before, "work limit rolls back all ticks")
	var overflow: EffectRunner = EffectRunner.new(1)
	var rich: EffectActorState = actor()
	rich.energy_milli = EffectRunner.MAX_VALUE
	check(overflow.bind(0, catalog.effect("legacy_005"), "base_text_v1"), "overflow bind")
	check(overflow.start([rich, actor()]), "overflow initial boundary")
	send(overflow, "basic_attack") # First known roll fails, second succeeds.
	reject(overflow, EffectEvent.new("basic_attack", 0, 0), "numeric overflow rolls back successful proc RNG")
	check(rich.energy_milli == EffectRunner.MAX_VALUE, "caller actor remains unmodified")
	var copied: Dictionary = sim.snapshot()
	copied["actors"][0]["hp_milli"] = -1
	check(state(sim)["hp_milli"] > 0, "snapshot defensive copy")
	var drained: Array[Dictionary] = sim.drain_commands()
	check(not drained.is_empty() and sim.snapshot()["commands"].is_empty(), "bounded consumer command drain")

func _test_replay_symmetry() -> void:
	for seed_value: int in [0, 1, 2, 42, 999, 123456, -1, 2147483647]:
		var first: EffectRunner = runner([2, 5, 10, 40, 49, 90, 115, 149], seed_value)
		var second: EffectRunner = runner([2, 5, 10, 40, 49, 90, 115, 149], seed_value)
		for index: int in range(100):
			var time: int = index * 100
			for sim: EffectRunner in [first, second]:
				send(sim, "basic_attack", {}, 0, time)
				send(sim, "basic_hit", {"critical":index % 3 == 0}, 0, time)
				send(sim, "dodge", {"incoming_milli":20000, "reflectable":true}, 0, time)
				send(sim, "status_applied", {"status":"wound", "stacks":1}, 0, time)
		check(first.snapshot() == second.snapshot(), "full seeded replay equality seed=" + str(seed_value))
	var player: EffectRunner = runner([2, 5, 10, 40, 49, 90, 115, 149], 42, 0)
	var bot: EffectRunner = runner([2, 5, 10, 40, 49, 90, 115, 149], 42, 1)
	for index: int in range(100):
		for owner: int in range(2):
			var sim: EffectRunner = player if owner == 0 else bot
			send(sim, "basic_attack", {}, owner, index * 100)
			send(sim, "basic_hit", {"critical":true}, owner, index * 100)
			send(sim, "dodge", {"incoming_milli":20000, "reflectable":true}, owner, index * 100)
			send(sim, "status_applied", {"status":"wound", "stacks":1}, owner, index * 100)
	check(state(player, 0) == state(bot, 1) and state(player, 1) == state(bot, 0), "actor mirror state symmetry")
	check(player.snapshot()["rng_state"] == bot.snapshot()["rng_state"], "actor mirror RNG symmetry")
	var player_log: Array = player.snapshot()["commands"]
	var bot_log: Array = bot.snapshot()["commands"]
	for command: Dictionary in bot_log:
		command["source_actor"] = 1 - int(command["source_actor"])
		command["target_actor"] = 1 - int(command["target_actor"])
	check(player_log == bot_log, "actor mirror command symmetry")

func _finish() -> void:
	print(JSON.stringify({"suite":"effects", "assertions":assertions, "pilot_cards":PILOTS, "implemented_contracts":12, "replay_seeds":8, "events_per_replay":400, "failures":failures, "status":"pass" if failures.is_empty() else "fail"}))
	quit(0 if failures.is_empty() else 1)
