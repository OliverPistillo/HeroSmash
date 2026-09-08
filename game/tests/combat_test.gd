extends SceneTree

var catalog: CombatCatalog = CombatCatalog.new()
var failures: Array[String] = []
var assertions: int = 0

func _initialize() -> void:
	check(catalog.load_data(), "catalog loads")
	if not failures.is_empty():
		print(CombatJson.encode({"failures":failures, "errors":catalog.errors}))
		quit(1)
		return
	levels()
	vectors()
	status_policies()
	lifecycle()
	validation()
	timing_and_effects()
	var input: Dictionary = fixture(45000)
	input["combatants"][0]["bindings"] = [binding("005"), binding("010"), binding("028"), binding("040")]
	var run: Dictionary = CombatResolver.new(catalog).run(input, true)
	check(run["ok"], "full fight: " + str(run["errors"]))
	var repeat: Dictionary = CombatResolver.new(catalog).run(CombatJson.normalize(JSON.parse_string(CombatJson.encode(input))), true)
	check(run["eventHash"] == repeat["eventHash"] and run["resultHash"] == repeat["resultHash"], "JSON roundtrip deterministic")
	input["combatants"].reverse()
	input["sides"].reverse()
	var mirror: Dictionary = CombatResolver.new(catalog).run(input)
	check(mirror["eventHash"] == run["eventHash"] and mirror["resultHash"] == run["resultHash"], "identity survives reversed sides and input order")
	var previous_time: int = -1
	var previous_sequence: int = 0
	for event: Dictionary in run["events"]:
		check(event["at_ms"] >= previous_time and event["sequence"] == previous_sequence + 1 and event["parent_sequence"] < event["sequence"], "event order")
		previous_time = event["at_ms"]
		previous_sequence = event["sequence"]
	print(CombatJson.encode({"suite":"combat", "assertions":assertions, "failures":failures}))
	quit(0 if failures.is_empty() else 1)

func check(condition: bool, message: String) -> void:
	assertions += 1
	if not condition: failures.append(message)

func binding(id: String, numbered: bool = false) -> Dictionary:
	return {"cardId":"legacy_" + id, "profile":"numbered" if numbered else "base_text_v1", "level":1 if numbered else 0}

func fixture(horizon: int = 1) -> Dictionary:
	var a: Dictionary = catalog.hero_input("fireheart", "a")
	var b: Dictionary = catalog.hero_input("fireheart", "b")
	for actor: Dictionary in [a, b]:
		actor["origin"] = "unit_fixture"
		actor["stats"]["crit_bp"] = 0
		actor["stats"]["dodge_bp"] = 0
	return {"scenarioId":"unit", "rulesetVersion":CombatCatalog.RULESET_VERSION, "canonicalDataVersion":CombatCatalog.DATA_VERSION, "seed":1, "horizon_ms":horizon, "combatants":[a, b], "sides":["a", "b"]}

func status(kind: String, magnitude: int, duration: int = 3000, stacks: int = 1, policy: String = "add_stack_and_refresh") -> Dictionary:
	return {"type":kind, "duration_ms":duration, "stacks":stacks, "max_stacks":20, "magnitude":magnitude, "stacking_policy":"independent_instances" if kind == "shield" else policy, "refresh_policy":"extend_if_longer", "interval_ms":1000 if kind in ["burn", "toxin"] else 0, "debuff":kind != "shield", "metadata":{"origin":"mechanics_fixture"}}

func initial(definition: Dictionary, source: String) -> Dictionary:
	var result: Dictionary = definition.duplicate(true)
	result["source"] = source
	return result

func prepare() -> CombatResolver:
	var resolver: CombatResolver = CombatResolver.new(catalog)
	var input: Dictionary = fixture()
	var run: Dictionary = resolver.run(input, true)
	check(run["ok"], "prepare vector")
	# Direct pipeline unit vectors start after the independently tested scheduler.
	# Reinitialize the hasher because run() has finalized its stream.
	resolver._hash = HashingContext.new()
	resolver._hash.start(HashingContext.HASH_SHA256)
	for actor: CombatantState in resolver.actors.values(): actor.hp_milli = int(actor.stats["max_hp_milli"])
	return resolver

func levels() -> void:
	var count: int = 0
	for number: int in range(1, 151):
		var id: String = "legacy_%03d" % number
		var first: Dictionary = catalog.source_level(id, 1)
		check(not first.is_empty(), "source card " + id)
		for level: int in range(1, int(first["maxLevel"]) + 1):
			var row: Dictionary = catalog.source_level(id, level)
			check(row["level"] == level and row["cardId"] == id, "exact level identity")
			check(catalog.combat_values(id, level).is_empty() == not bool(row["canonicalNumberedExecutable"]), "level eligibility explicit")
			count += 1
		check(catalog.next_owned_level(id, int(first["maxLevel"])).is_empty(), "reject max acquisition")
		check(catalog.next_owned_level(id, 0).get("next") == 1, "separate acquisition")
	check(count == 582, "all 582 levels")
	check(catalog.source_parameter("legacy_005", 1, "chance")["value"] == 10, "raw chance10 is not base-text60")
	check(catalog.source_level("legacy_001", 6).is_empty(), "no interpolation")
	check(catalog.source_level("bogus", 1).is_empty(), "unknown level card")
	check(catalog.source_parameter("legacy_120", 1, "chance").is_empty(), "missing parameter explicit")

func vectors() -> void:
	var resolver: CombatResolver = prepare()
	var a: CombatantState = resolver.actors["a"]
	var b: CombatantState = resolver.actors["b"]
	resolver.apply_status("a", "b", status("wound", 500), 0, 0)
	resolver.apply_status("b", "b", status("shield", 5000), 0, 0)
	resolver.apply_status("b", "b", status("shield", 3000), 0, 0)
	var before: int = b.hp_milli
	resolver.damage(DamageEvent.new("a", "b", 20000, "physical", ["basic"]))
	check(before - b.hp_milli == 7000, "20 *1.05 -6 armor -5 shield -3 shield =7 HP")
	check(resolver.status_sum(b, "shield") == 0, "both shields exhausted")
	before = b.hp_milli
	resolver.damage(DamageEvent.new("a", "b", 100, "magic", ["dot"]))
	check(before - b.hp_milli == 105, "DoT magic bypass armor and minimum, Wound explicit")
	before = b.hp_milli
	resolver.damage(DamageEvent.new("a", "b", 100, "physical", ["basic"]))
	check(before - b.hp_milli == 1000, "ordinary hit minimum")
	b.stats["dodge_bp"] = 10000
	before = b.hp_milli
	var hit: Dictionary = resolver.damage(DamageEvent.new("a", "b", 10000, "physical", ["basic"], false, true, true))
	check(not hit["hit"] and b.hp_milli == before, "physical dodge")
	resolver.damage(DamageEvent.new("a", "b", 10000, "magic", ["secondary"], false, true, true))
	check(before - b.hp_milli == 10500, "magic cannot dodge even eligible flag")
	var energy_before: int = a.energy_milli
	resolver.heal(a, b, 999999999, "effect", 0, 0)
	check(b.hp_milli == b.stats["max_hp_milli"] and a.energy_milli == energy_before, "healing cap and isolation")
	resolver.apply_status("a", "b", status("ice", 1000, 3000, 20), 0, 0)
	check(resolver.ice_rate(b) == 3500, "Ice lower rate bound")
	resolver.apply_status("a", "b", status("stun", 1), 0, 0)
	check(resolver.basic_rate(b) == 0 and resolver.energy_rate(b) == b.stats["energy_regen_milli"] * 3000, "stun blocks basic,30percent energy ignores Ice")
	resolver.damage(DamageEvent.new("a", "b", 1, "magic", ["reflected"], false, false, false, 0, 17))
	check("reaction_depth_limit" in resolver.errors, "visible recursion guard")

func status_policies() -> void:
	for policy: String in CombatInput.POLICIES:
		var resolver: CombatResolver = prepare()
		var b: CombatantState = resolver.actors["b"]
		resolver.apply_status("a", "b", status("toxin", 1000, 3000, 2, policy), 0, 0)
		var old_id: String = b.statuses[0].id
		resolver.now += 500
		resolver.apply_status("a", "b", status("toxin", 2000, 4000, 3, policy), 0, 0)
		var entry: StatusInstance = b.statuses[-1]
		if policy == "independent_instances": check(b.statuses.size() == 2, "independent instances")
		elif policy in ["replace", "stronger_wins"]: check(entry.id != old_id and entry.stacks == 3 and entry.next_tick == 1501, "replace phase:" + policy)
		elif policy == "refresh_duration": check(entry.stacks == 2 and entry.magnitude == 1000 and entry.next_tick == 1001 and entry.expires_at == 4501, "refresh keeps phase/magnitude/stacks")
		elif policy == "add_stack": check(entry.stacks == 5 and entry.expires_at == 3001 and entry.magnitude == 1000, "add only")
		else: check(entry.stacks == 5 and entry.expires_at == 4501 and entry.magnitude == 2000 and entry.next_tick == 1001, "add refresh stronger preserves phase")
		resolver.apply_status("a", "b", status("toxin", 1, 3000, 20, policy), 0, 0)
		check(b.statuses[0].stacks <= 20, "cap policy:" + policy)
		if policy == "stronger_wins": check(b.statuses[0].magnitude == 2000, "weaker ignored")
	var input: Dictionary = fixture(3000)
	input["combatants"][1]["initial_statuses"] = [initial(status("toxin", 7000), "a")]
	var run: Dictionary = CombatResolver.new(catalog).run(input, true)
	var times: Array[int] = []
	for event: Dictionary in run["events"]:
		if event["type"] == "StatusTick":
			times.append(event["at_ms"])
			check(event["source"] == "a" and event["payload"]["amount_milli"] == 7000, "periodic source and magnitude")
	check(times == [1000, 2000, 3000], "first delayed and last expiry-inclusive tick")
	check(run["result"]["final"][1]["metrics"]["status_uptime_ms"]["toxin"] == 3000, "uptime union")
	input["combatants"][1]["initial_statuses"][0]["duration_ms"] = 999
	run = CombatResolver.new(catalog).run(input, true)
	check(run["result"]["final"][0]["metrics"]["dot_damage_milli"] == 0, "short duration no invented prorated tick")

func lifecycle() -> void:
	var resolver: CombatResolver = prepare()
	var b: CombatantState = resolver.actors["b"]
	b.prevention_charges = 1
	b.prevention_hp = 1000
	b.rebirth_charges = 1
	b.rebirth_hp_bp = 4000
	resolver.apply_status("a", "b", status("toxin", 14000), 0, 0)
	resolver.apply_status("b", "b", status("shield", 1000), 0, 0)
	resolver.damage(DamageEvent.new("a", "b", 1000000, "magic", ["secondary"]))
	check(b.hp_milli == 1000 and b.prevention_charges == 0 and b.rebirth_charges == 1 and b.alive, "prevention before rebirth")
	resolver.damage(DamageEvent.new("a", "b", 1000000, "magic", ["secondary"]))
	check(b.hp_milli == 372000 and b.generation == 1 and b.rebirth_charges == 0 and b.statuses.is_empty(), "one rebirth40percent and cleanse")
	resolver.damage(DamageEvent.new("a", "b", 1000000, "magic", ["secondary"]))
	check(not b.alive and b.hp_milli == 0 and b.metrics["ko_count"] == 1, "final KO after spent charges")
	resolver.damage(DamageEvent.new("a", "b", 1000000, "magic", ["secondary"]))
	resolver.heal(resolver.actors["a"], b, 1000000, "effect", 0, 0)
	check(b.metrics["ko_count"] == 1 and b.hp_milli == 0, "no duplicate KO or generic resurrection")
	var input: Dictionary = fixture(1000)
	for actor: Dictionary in input["combatants"]:
		actor["hp_milli"] = 1000
		actor["initial_statuses"] = [initial(status("stun", 1, 1000), actor["id"]), initial(status("toxin", 1000, 1000), "b" if actor["id"] == "a" else "a")]
	var draw: Dictionary = CombatResolver.new(catalog).run(input, true)
	check(draw["ok"] and draw["result"]["outcome"] == "draw" and draw["result"]["duration_ms"] == 1000, "simultaneous lethal ticks drain to doubleKO at horizon")
	# Reflection is full post-armor damage,50percent roll, never reflected again.
	var reflected_count: int = 0
	for seed_value: int in range(64):
		input = fixture()
		input["seed"] = seed_value
		for actor: Dictionary in input["combatants"]:
			actor["stats"]["dodge_bp"] = 10000
			actor["bindings"] = [binding("049", true)]
		var run: Dictionary = CombatResolver.new(catalog).run(input, true)
		check(run["ok"], "reflection resolves")
		for event: Dictionary in run["events"]:
			if event["type"] == "DamageApplied":
				check(event["payload"]["tags"] == ["reflected"] and event["payload"]["actual_milli"] == 20000 and not event["payload"]["critical"], "full20reflection no crit/recursive dodge")
				reflected_count += 1
	check(reflected_count > 30 and reflected_count < 100, "reflection chance not guaranteed half-damage")

func validation() -> void:
	var base: Dictionary = fixture()
	for mutation: String in ["negative_hp", "nan", "unknown_card", "unresolved", "missing_template", "wrong_version", "unknown_field", "level2", "duplicate", "bad_policy", "canonical_edit"]:
		var input: Dictionary = base.duplicate(true)
		var actor: Dictionary = input["combatants"][0]
		match mutation:
			"negative_hp": actor["hp_milli"] = -1
			"nan": actor["stats"]["attack_milli"] = NAN
			"unknown_card": actor["bindings"] = [binding("999")]
			"unresolved": actor["bindings"] = [binding("111")]
			"missing_template": actor["bindings"] = [binding("115")]
			"wrong_version": input["rulesetVersion"] = "future"
			"unknown_field": actor["is_player"] = true
			"level2": actor["bindings"] = [{"cardId":"legacy_005", "profile":"numbered", "level":2}]
			"duplicate": input["combatants"][1]["id"] = "a"
			"bad_policy":
				actor["initial_statuses"] = [initial(status("toxin", 1000), "b")]
				actor["initial_statuses"][0]["stacking_policy"] = "guess"
			"canonical_edit": actor["origin"] = "canonical_hero"
		var run: Dictionary = CombatResolver.new(catalog).run(input)
		check(not run["ok"] and not run.has("result"), "reject without partial fight:" + mutation)
	for key: String in base:
		var input: Dictionary = base.duplicate(true)
		input[key] = null
		check(not CombatResolver.new(catalog).run(input)["ok"], "reject null top-level:" + key)
	for key: String in base["combatants"][0]:
		var input: Dictionary = base.duplicate(true)
		input["combatants"][0][key] = null
		check(not CombatResolver.new(catalog).run(input)["ok"], "reject null combatant:" + key)

func timing_and_effects() -> void:
	var input: Dictionary = fixture(7000)
	for actor: Dictionary in input["combatants"]: actor["stats"]["attack_speed_milli"] = 1000
	var run: Dictionary = CombatResolver.new(catalog).run(input, true)
	var basics: Array[int] = []
	var skills: Array[int] = []
	for event: Dictionary in run["events"]:
		if event["source"] == "a" and event["type"] == "BasicAttack": basics.append(event["at_ms"])
		if event["source"] == "a" and event["type"] == "SkillCast": skills.append(event["at_ms"])
	check(basics == [0,1000,2000,3000,4000,5000,6000,7000] and skills == [5000], "integer readiness, skill priority, no lost basic at tie")
	input["combatants"][0]["initial_statuses"] = [initial(status("stun", 1, 2000), "b")]
	run = CombatResolver.new(catalog).run(input, true)
	skills.clear()
	for event: Dictionary in run["events"]:
		if event["source"] == "a" and event["type"] == "SkillCast": skills.append(event["at_ms"])
	check(skills == [6400], "stun regeneration30percent produces exact6400ms cast")
	input = fixture(1)
	input["combatants"][0]["bindings"] = [binding("002"), binding("010"), binding("020")]
	var resolver: CombatResolver = CombatResolver.new(catalog)
	run = resolver.run(input, true)
	var a: CombatantState = resolver.actors["a"]
	check(a.stats["attack_milli"] == 31000 and a.basic_bonus_bp == 400, "002 and010 integrated at attack")
	resolver._hash = HashingContext.new()
	resolver._hash.start(HashingContext.HASH_SHA256)
	var energy: int = a.energy_milli
	resolver.damage(DamageEvent.new("b", "a", 399000, "magic", ["secondary"]))
	check(a.energy_milli == energy + 6000, "020 includes opening20HP then399HP crosses400 once")
	check(a.bindings[-1]["loss_remainder"] == 19000, "020 actual loss remainder retained")
	var before: int = a.hp_milli
	resolver.actors["b"].stats["crit_bp"] = 10000
	resolver.rng = FoundationRng.new(1)
	resolver.damage(DamageEvent.new("b", "a", 20000, "physical", ["basic"], true))
	check(before - a.hp_milli == 24000, "critical20x1.5 minus6armor")
	# Apply two independently attributed DoTs and prove union uptime and fractional ticks.
	input = fixture(1000)
	var periodic: Dictionary = status("toxin", 1001, 1000, 1, "independent_instances")
	periodic["interval_ms"] = 250
	input["combatants"][1]["initial_statuses"] = [initial(periodic, "a"), initial(periodic, "b")]
	run = CombatResolver.new(catalog).run(input, true)
	check(run["result"]["final"][0]["metrics"]["dot_damage_milli"] == 1001 and run["result"]["final"][1]["metrics"]["dot_damage_milli"] == 1001, "per-instance integer remainder and source attribution")
	check(run["result"]["final"][1]["metrics"]["status_uptime_ms"]["toxin"] == 1000, "independent status uptime is union")
