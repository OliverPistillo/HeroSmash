extends SceneTree

var failures: Array[String] = []
var assertions: int = 0
var contacts: Array[Dictionary] = []


func check(ok: bool, message: String) -> void:
	assertions += 1
	if not ok: failures.append(message)


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	var slice: TwoFighterSlice = (load("res://scenes/qa/two_fighter_slice.tscn") as PackedScene).instantiate() as TwoFighterSlice
	root.add_child(slice)
	slice.set_process(false)
	await process_frame
	check(slice.fighters.size()==2,"two shared instances")
	check(slice.fighters[0].meshes[0].mesh==slice.fighters[1].meshes[0].mesh,"shared mesh resource, no asset duplication")
	var coverage: Dictionary = {}
	var cues: Dictionary = {}
	for fighter: SolkaelFighter in slice.fighters:
		fighter.cosmetic_cue.connect(func(cue: Dictionary) -> void: cues[String(cue["kind"])]=true)
	for id: String in slice.scenarios.ids():
		var input: Dictionary = slice.scenarios.build(id,5)
		var replay: Dictionary = CombatResolver.new(slice.catalog).run(input,true)
		check(replay["ok"],"real resolver:"+id)
		var original: String = CombatJson.digest(replay)
		var events: Array = replay["events"]
		# CombatStarted and the first hit may share t=0. Observe the actual start
		# event independently; the QA scene holds a one-second visual prelude.
		for fighter: SolkaelFighter in slice.fighters:
			fighter.seek_replay([],0)
			fighter.present([events[0]],int(events[0]["at_ms"]))
			coverage[fighter.adapter.current_clip]=true
		for speed: int in [1,2,3]:
			for fighter: SolkaelFighter in slice.fighters:
				fighter.seek_replay([],0)
				fighter.adapter.enqueue(events)
			var at_ms: int = 0
			var end: int = int(replay["result"]["duration_ms"])
			while at_ms<=end+50:
				for fighter: SolkaelFighter in slice.fighters:
					fighter.present([],at_ms)
					coverage[fighter.adapter.current_clip]=true
				at_ms += 16*speed
			for fighter: SolkaelFighter in slice.fighters:
				check(fighter.adapter.errors.is_empty(),id+":no adapter errors x"+str(speed))
				var final_dead: bool = fighter.adapter.dead
				fighter.seek_replay(events,end)
				check(fighter.adapter.dead==final_dead and fighter.adapter.cue_count==0,id+":silent seek x"+str(speed))
		check(CombatJson.digest(replay)==original,id+":resolver stream unchanged")
	for name: String in ["intro","attack_light","skill_cast","dodge","hit_react","ko","victory"]:
		check(coverage.has(name),"real stream clip coverage:"+name)
	for name: String in ["hit","vfx_spawn","barrier","periodic","reflection"]:
		check(cues.has(name),"real stream cue coverage:"+name)
	for index: int in range(2):
		var attacker: SolkaelFighter = slice.fighters[index]
		var defender: SolkaelFighter = slice.fighters[1-index]
		for clip_name: String in ["attack_light","attack_heavy"]:
			for fighter: SolkaelFighter in slice.fighters: fighter.seek_replay([],0)
			attacker.adapter.current_clip = clip_name
			attacker.adapter.clock_ms = 0
			attacker.adapter.clip_started_ms = 0
			attacker.show_clip(clip_name,.304 if clip_name=="attack_light" else .7)
			defender.show_clip("idle",0)
			slice.update_blocking()
			await process_frame
			var contact: Vector3 = attacker.socket_transform("socket_weapon_l" if clip_name=="attack_light" else "socket_weapon_r").origin
			var target: Vector3 = defender.socket_transform("socket_hurtbox_chest").origin+defender.basis.z*.25
			var gap: float = absf(contact.x-target.x)
			contacts.append({"entity":attacker.entity_id,"clip":clip_name,"visual_step_in_m":.10 if clip_name=="attack_light" else .24,"target_axis_gap_m":gap})
			check(gap<.09,"gauntlet reaches chest/guard plane:"+clip_name+str(gap))
	for fighter: SolkaelFighter in slice.fighters:
		for socket: String in ["socket_weapon_l","socket_weapon_r","socket_vfx_head","socket_vfx_chest","socket_hurtbox_head"]:
			check(fighter.socket_transform(socket).origin.is_finite(),"finite contact anchor:"+socket)
		for clip: Dictionary in fighter.contract["clips"]:
			fighter.show_clip(String(clip["name"]),float(clip["duration_seconds"])*.5)
			await process_frame
			check(fighter.skeleton.get_bone_pose_position(fighter.skeleton.find_bone("root")).length()<.00001,"no root motion:"+String(clip["name"]))
			fighter.skeleton.force_update_all_bone_transforms()
			var floor_y: float = INF
			var mesh_instance: MeshInstance3D = fighter.meshes[0]
			# CPU evaluation also works with the headless dummy renderer, which
			# does not register render-server skins for bake_mesh_from_current_skeleton_pose.
			var skin: Skin = mesh_instance.skin
			var transforms: Array[Transform3D] = []
			for bind: int in range(skin.get_bind_count()):
				var bone: int = fighter.skeleton.find_bone(skin.get_bind_name(bind))
				if bone<0: bone = skin.get_bind_bone(bind)
				transforms.append(fighter.skeleton.global_transform*fighter.skeleton.get_bone_global_pose(bone)*skin.get_bind_pose(bind))
			for surface: int in range(mesh_instance.mesh.get_surface_count()):
				var arrays: Array = mesh_instance.mesh.surface_get_arrays(surface)
				var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
				var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
				var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
				for vertex_index: int in range(vertices.size()):
					var point: Vector3 = Vector3.ZERO
					for influence: int in range(4):
						var offset: int = vertex_index*4+influence
						point += (transforms[bones[offset]]*vertices[vertex_index])*weights[offset]
					floor_y = minf(floor_y,point.y)
			contacts.append({"entity":fighter.entity_id,"clip":clip["name"],"floor_y_m":floor_y,"left_fist":fighter.socket_transform("socket_weapon_l").origin,"right_fist":fighter.socket_transform("socket_weapon_r").origin})
			check(floor_y>=-.035 and floor_y<.08,"evaluated skinned floor:"+String(clip["name"])+" "+str(floor_y))
		fighter.show_clip("idle",0)
		await process_frame
		check(abs(fighter.socket_transform("foot_l").origin.y)<.3,"floor anchor remains near stage")
		slice.on_cue({"kind":"barrier","at_ms":0},fighter)
		fighter.seek_replay([],0)
		check(slice.effects.filter(func(item: Dictionary) -> bool: return item["entity"]==fighter.entity_id).is_empty(),"seek cancels attached VFX")
	print("TWO_FIGHTER_TEST_"+("PASS" if failures.is_empty() else "FAIL")+" "+JSON.stringify({"assertions":assertions,"failures":failures,"clips":coverage,"cues":cues,"contacts":contacts}))
	slice.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
