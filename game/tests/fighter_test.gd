extends SceneTree

var assertions: int = 0
var failures: Array[String] = []
var specs: Array = []


func check(value: bool, message: String) -> void:
	assertions += 1
	if not value:
		failures.append(message)


func _initialize() -> void:
	call_deferred("run_tests")


func new_adapter(id: String = "A") -> FighterEventAdapter:
	var adapter: FighterEventAdapter = FighterEventAdapter.new()
	adapter.configure(id,specs)
	return adapter


func event(sequence: int, at_ms: int, kind: String, source: String = "A", target: String = "B", payload: Dictionary = {}) -> Dictionary:
	return CombatEvent.value(sequence,at_ms,kind,source,target,payload)


func run_tests() -> void:
	specs = (JSON.parse_string(FileAccess.get_file_as_string(SolkaelFighter.CONTRACT_PATH)) as Dictionary)["clips"]
	var adapter: FighterEventAdapter = new_adapter()
	var attack: Dictionary = event(1,100,"BasicAttack")
	var original: Dictionary = attack.duplicate(true)
	adapter.enqueue([attack,attack])
	check(adapter.advance(99).is_empty(),"future event has no early cue")
	check(adapter.advance(100).size()==1,"single authoritative contact cue")
	check(adapter.current_clip=="attack_light" and is_equal_approx(adapter.pose_seconds(),.38*.8),"contact phase aligns with resolver timestamp")
	check(adapter.advance(100).is_empty(),"duplicate tick silent")
	adapter.enqueue([attack])
	check(adapter.advance(110).is_empty(),"duplicate delivery silent")
	check(attack==original,"caller dictionary unchanged")
	adapter.advance(1000)
	check(adapter.current_clip=="idle","completed attack falls back to idle")
	adapter = new_adapter()
	adapter.enqueue([attack,event(2,100,"DamageApplied","A","B",{"critical":true,"tags":["basic"],"actual_milli":10})])
	check(adapter.advance(100).size()==1 and adapter.current_clip=="attack_heavy","critical basic attack uses heavy presentation without duplicate cue")
	adapter = new_adapter()
	adapter.enqueue([attack])
	check(adapter.advance(500).is_empty(),"late arrival suppresses stale one-shot")
	check(is_equal_approx(adapter.pose_seconds(),.704),"late pose catches up without delaying contact")
	var knock_out: Dictionary = event(2,100,"CombatantKO","B","A")
	adapter = new_adapter()
	adapter.enqueue([knock_out,attack])
	check(adapter.advance(100).is_empty() and adapter.dead and adapter.current_clip=="ko","same-tick KO cancels outgoing cues")
	adapter.enqueue([event(3,150,"SkillCast")])
	check(adapter.advance(150).is_empty() and adapter.current_clip=="ko","KO suppresses pending outgoing action")
	adapter.advance(10000)
	check(adapter.current_clip=="ko","KO holds final pose")
	adapter.seek([attack,knock_out],99)
	check(not adapter.dead and adapter.cue_count==0,"seek before KO clears dead state and sounds")
	adapter.seek([attack,knock_out],150)
	check(adapter.dead and adapter.cue_count==0,"seek after KO reconstructs silently")
	adapter.enqueue([event(3,200,"CombatantRevived","A","A")])
	adapter.advance(200)
	check(not adapter.dead and adapter.current_clip=="idle","resolver revival re-enables presentation")
	adapter.enqueue([event(4,220,"Dodged","B","A")])
	adapter.advance(220)
	check(adapter.current_clip=="dodge","authoritative target dodge")
	adapter.enqueue([event(5,230,"DamageApplied","A","B",{"actual_milli":100,"tags":["reflected"]})])
	adapter.advance(230)
	check(adapter.current_clip=="dodge","reflected source damage does not start an attack")
	adapter.enqueue([event(6,240,"DamageApplied","B","A",{"actual_milli":100})])
	check(adapter.advance(240).size()==1 and adapter.current_clip=="hit_react","target damage consumes provided amount only")
	adapter.enqueue([event(7,250,"ShieldAbsorbed","B","A")])
	check(adapter.advance(250)[0]["kind"]=="barrier","barrier reaction from resolver event")
	adapter.enqueue([event(8,260,"CombatEnded","","",{"winner":"A"})])
	adapter.advance(260)
	check(adapter.current_clip=="victory","winner identity selects victory")
	adapter.advance(250)
	check("rewind_requires_seek" in adapter.errors,"raw backward clock rejected")
	adapter = new_adapter()
	adapter.enqueue([attack])
	var conflict: Dictionary = attack.duplicate(true)
	conflict["target"] = "C"
	adapter.enqueue([conflict,{},null])
	check("conflicting_sequence" in adapter.errors and adapter.errors.count("malformed_event")==2,"conflict and malformed rejection")
	var reduced: Array = specs.filter(func(c: Dictionary) -> bool: return c["name"] != "attack_light")
	adapter.configure("A",reduced)
	adapter.enqueue([attack])
	adapter.advance(100)
	check(adapter.current_clip=="idle" and "missing_clip:attack_light" in adapter.errors,"missing clip fallback is nonblocking")
	var fighter: SolkaelFighter = (load("res://scenes/characters/solkael_lionheart/hero_solkael_lionheart.tscn") as PackedScene).instantiate() as SolkaelFighter
	root.add_child(fighter)
	await process_frame
	check(fighter.skeleton.get_bone_count()==71,"all shared bones, fingers, extensions and sockets imported")
	check(fighter.meshes.size()==1,"one skinned mesh")
	for clip: Dictionary in specs:
		var name: String = String(clip["name"])
		check(fighter.clip_names.has(name),"imported clip:"+name)
		var animation: Animation = fighter.animation_player.get_animation(StringName(fighter.clip_names[name]))
		check((animation.loop_mode==Animation.LOOP_LINEAR)==bool(clip["loop"]),"loop metadata:"+name)
		fighter.show_clip(name,float(clip["duration_seconds"])*.5)
		await process_frame
		var index: int = fighter.skeleton.find_bone("root")
		check(fighter.skeleton.get_bone_pose_position(index).length()<.00001,"no root translation:"+name)
		check(fighter.skeleton.get_bone_pose_rotation(index).angle_to(Quaternion.IDENTITY)<.0001,"no root rotation:"+name)
	for expression_name: String in fighter.contract["expressions"]:
		fighter.set_expression(expression_name)
		var nonzero: int = 0
		for mesh: MeshInstance3D in fighter.meshes:
			for index: int in range(mesh.mesh.get_blend_shape_count()):
				if mesh.get_blend_shape_value(index)>.9:
					nonzero += 1
		check(nonzero==(0 if expression_name=="neutral" else 1),"exclusive expression:"+expression_name)
	for socket_name: String in ["socket_weapon_l","socket_weapon_r","socket_vfx_head","socket_vfx_chest","socket_hurtbox_head"]:
		check(fighter.socket_transform(socket_name).origin.is_finite(),"valid socket:"+socket_name)
	# Feed real unchanged resolver streams and verify replay bytes remain untouched.
	var catalog: CombatCatalog = CombatCatalog.new()
	check(catalog.load_data(),"real catalog loads")
	var scenarios: CombatScenarios = CombatScenarios.new(catalog)
	for scenario_id: String in scenarios.ids():
		var input: Dictionary = scenarios.build(scenario_id,5)
		var run: Dictionary = CombatResolver.new(catalog).run(input,true)
		check(run["ok"],"resolver:"+scenario_id)
		var before: String = CombatJson.digest(run)
		var events: Array = run["events"]
		for entity: Dictionary in input["combatants"]:
			var stream: FighterEventAdapter = new_adapter(String(entity["id"]))
			stream.enqueue(events)
			for e: Dictionary in events:
				stream.advance(int(e["at_ms"]))
			check(stream.errors.is_empty(),"real stream acceptance:"+scenario_id+String(entity["id"]))
			var final_clip: String = stream.current_clip
			stream.seek(events,int(run["result"]["duration_ms"]))
			check(stream.current_clip==final_clip and stream.cue_count==0,"real seek/live parity:"+scenario_id+String(entity["id"]))
		check(CombatJson.digest(run)==before,"immutable real resolver stream:"+scenario_id)
	fighter.queue_free()
	await process_frame
	print("FIGHTER_TEST_"+("PASS" if failures.is_empty() else "FAIL")+" "+JSON.stringify({"assertions":assertions,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
