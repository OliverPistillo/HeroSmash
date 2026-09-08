extends SceneTree
## -- list | run SCENARIO SEED REPLAY [HORIZON] | input INPUT_JSON REPLAY
## -- verify REPLAY | batch SCENARIO FIRST COUNT OUTPUT [HORIZON]

func _initialize() -> void:
	var catalog: CombatCatalog = CombatCatalog.new()
	if not catalog.load_data(): finish({"ok":false, "errors":catalog.errors}); return
	var scenarios: CombatScenarios = CombatScenarios.new(catalog)
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.is_empty(): finish({"ok":false, "errors":["command_required"]}); return
	match args[0]:
		"list": finish({"ok":true, "scenarios":scenarios.ids()})
		"run", "input":
			var required: int = 4 if args[0] == "run" else 3
			if args.size() < required or args.size() > required + (1 if args[0] == "run" else 0): finish({"ok":false, "errors":["invalid_arguments"]}); return
			if args[0] == "run" and (not args[2].is_valid_int() or (args.size() == 5 and not args[4].is_valid_int())): finish({"ok":false, "errors":["invalid_integer_argument"]}); return
			var input: Variant = scenarios.build(args[1], int(args[2]), int(args[4]) if args.size() == 5 else 45000) if args[0] == "run" else CombatJson.read_file(args[1])
			if not input is Dictionary: finish({"ok":false, "errors":["invalid_input_file"]}); return
			var result: Dictionary = CombatReplay.create(input, catalog)
			if result["ok"]:
				var path: String = args[3] if args[0] == "run" else args[2]
				if not save(path, result["replay"]): finish({"ok":false, "errors":["output_write_failed"]}); return
				finish({"ok":true, "path":path, "eventHash":result["replay"]["eventHash"], "resultHash":result["replay"]["resultHash"]})
			else: finish(result)
		"verify":
			if args.size() != 2: finish({"ok":false, "errors":["invalid_arguments"]}); return
			finish(CombatReplay.verify(CombatJson.read_file(args[1]), catalog))
		"batch":
			if args.size() < 5 or args.size() > 6 or not args[2].is_valid_int() or not args[3].is_valid_int() or (args.size() == 6 and not args[5].is_valid_int()): finish({"ok":false, "errors":["invalid_arguments"]}); return
			var first: int = int(args[2])
			var count: int = int(args[3])
			if count < 1 or count > 100000 or first < 0 or first + count > 4294967296 or not args[1] in scenarios.ids(): finish({"ok":false, "errors":["invalid_batch_range_or_scenario"]}); return
			var rows: Array[Dictionary] = []
			var start: int = Time.get_ticks_usec()
			for seed_value: int in range(first, first + count):
				var input: Dictionary = scenarios.build(args[1], seed_value, int(args[5]) if args.size() == 6 else 45000)
				var began: int = Time.get_ticks_usec()
				var run: Dictionary = CombatResolver.new(catalog).run(input)
				var elapsed: int = Time.get_ticks_usec() - began
				if not run["ok"]: finish({"ok":false, "seed":seed_value, "errors":run["errors"]}); return
				var result: Dictionary = run["result"]
				var actor_metrics: Array[Dictionary] = []
				for actor: Dictionary in result["final"]: actor_metrics.append({"id":actor["id"], "hp_milli":actor["hp_milli"], "metrics":actor["metrics"]})
				rows.append({"seed":seed_value, "outcome":result["outcome"], "winner":result["winner"], "timeout_leader":result["timeout_leader"], "duration_ms":result["duration_ms"], "event_count":result["event_count"], "actors":actor_metrics, "eventHash":run["eventHash"], "resultHash":run["resultHash"], "runtime_us":elapsed})
			var document: Dictionary = {"schemaVersion":1, "rulesetVersion":CombatCatalog.RULESET_VERSION, "canonicalDataVersion":CombatCatalog.DATA_VERSION, "dataHash":catalog.data_hash, "scenarioId":args[1], "firstSeed":first, "count":count, "runtime_us":Time.get_ticks_usec() - start, "records":rows}
			if not save(args[4], document): finish({"ok":false, "errors":["output_write_failed"]}); return
			finish({"ok":true, "scenarioId":args[1], "count":count, "runtime_us":document["runtime_us"], "path":args[4]})
		_: finish({"ok":false, "errors":["unknown_command"]})

func save(path: String, value: Dictionary) -> bool:
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file == null: return false
	file.store_string(CombatJson.encode(value) + "\n")
	file.flush()
	return file.get_error() == OK

func finish(result: Dictionary) -> void:
	print(CombatJson.encode(result))
	quit(0 if result["ok"] else 1)
