extends SceneTree
## Explicit QA scene; not installed as the game's main scene.

var fighter: SolkaelFighter
var frame_count: int = 0
var cpu_ms: Array[float] = []
var gpu_ms: Array[float] = []
var frame_ms: Array[float] = []
var captures: String = ""
var clip: String = "idle"
var pose_time: float = 0.0
var expression: String = ""
var turntable: bool = false
var previous_us: int = 0
var mesh_stage: Node3D
var barrier: MeshInstance3D
var replay_events: Array = []
var replay_hash: String = ""
var barrier_until_ms: int = 0
var subtitle: Label
var profile_animation: bool = false
var replay_entity_id: String = ""
var replay_scenario: String = ""


func _initialize() -> void:
	call_deferred("setup")


func setup() -> void:
	root.content_scale_size = root.size
	captures = OS.get_environment("HERO_FIGHTER_CAPTURE")
	clip = OS.get_environment("HERO_FIGHTER_CLIP")
	if clip == "":
		clip = "idle"
	pose_time = OS.get_environment("HERO_FIGHTER_POSE").to_float()
	expression = OS.get_environment("HERO_FIGHTER_EXPRESSION")
	turntable = OS.get_environment("HERO_FIGHTER_VIDEO") == "1"
	profile_animation = OS.get_environment("HERO_FIGHTER_PROFILE") == "1"
	if OS.get_environment("HERO_FIGHTER_REPLAY") == "1":
		var catalog: CombatCatalog = CombatCatalog.new()
		assert(catalog.load_data())
		var scenarios: CombatScenarios = CombatScenarios.new(catalog)
		var id: String = scenarios.ids()[0]
		for candidate: String in scenarios.ids():
			if "toxin" in candidate.to_lower():
				id = candidate
		if OS.get_environment("HERO_FIGHTER_SCENARIO") != "":
			id = OS.get_environment("HERO_FIGHTER_SCENARIO")
		var input: Dictionary = scenarios.build(id,5)
		assert(not input.is_empty())
		replay_scenario = id
		replay_entity_id = String(input["combatants"][0]["id"])
		var run: Dictionary = CombatResolver.new(catalog).run(input,true)
		assert(run["ok"])
		replay_events = run["events"]
		replay_hash = run["eventHash"]
	mesh_stage = Node3D.new()
	root.add_child(mesh_stage)
	var environment: WorldEnvironment = WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("121b2a")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color("c3d3ef")
	environment.environment.ambient_light_energy = 0.24
	environment.environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	mesh_stage.add_child(environment)
	var key: DirectionalLight3D = DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-28,-30,0)
	key.light_energy = 1.25
	key.shadow_enabled = true
	mesh_stage.add_child(key)
	var fill: DirectionalLight3D = DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-15,140,0)
	fill.light_energy = 0.55
	fill.light_color = Color("92bdf6")
	mesh_stage.add_child(fill)
	var floor_mesh: MeshInstance3D = MeshInstance3D.new()
	var cylinder: CylinderMesh = CylinderMesh.new()
	cylinder.top_radius = 1.35
	cylinder.bottom_radius = 1.4
	cylinder.height = 0.08
	cylinder.radial_segments = 64
	floor_mesh.mesh = cylinder
	floor_mesh.position.y = -0.045
	var floor_material: StandardMaterial3D = StandardMaterial3D.new()
	floor_material.albedo_color = Color("28334a")
	floor_material.roughness = 0.85
	floor_mesh.material_override = floor_material
	mesh_stage.add_child(floor_mesh)
	var camera: Camera3D = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 3.0
	mesh_stage.add_child(camera)
	camera.position = Vector3(2.8,1.9,5)
	camera.look_at(Vector3(0,1.05,0))
	if OS.get_environment("HERO_FIGHTER_PORTRAIT") == "1":
		camera.size = .72
		camera.position = Vector3(.45,1.92,3.5)
		camera.look_at(Vector3(0,1.81,0))
	if OS.get_environment("HERO_FIGHTER_DETAIL") == "gauntlet":
		camera.size = .85
		camera.position = Vector3(.7,1.7,3.5)
		camera.look_at(Vector3(.35,1.5,.15))
	elif OS.get_environment("HERO_FIGHTER_DETAIL") == "material":
		camera.size = 1.1
		camera.position = Vector3(.8,1.45,3.5)
		camera.look_at(Vector3(0,1.3,0))
	camera.current = true
	fighter = (load("res://scenes/characters/solkael_lionheart/hero_solkael_lionheart_v002.tscn") as PackedScene).instantiate() as SolkaelFighter
	if replay_entity_id != "":
		fighter.entity_id = replay_entity_id
	mesh_stage.add_child(fighter)
	fighter.rotation_degrees.y = OS.get_environment("HERO_FIGHTER_YAW").to_float()
	barrier = MeshInstance3D.new()
	var ring: TorusMesh = TorusMesh.new()
	ring.inner_radius = .58
	ring.outer_radius = .615
	ring.rings = 48
	ring.ring_segments = 8
	barrier.mesh = ring
	barrier.position = Vector3(0,1.2,.5)
	barrier.rotation_degrees.x = 90
	var amber: StandardMaterial3D = StandardMaterial3D.new()
	amber.albedo_color = Color("ffb347")
	amber.emission_enabled = true
	amber.emission = Color("ffb347")
	amber.emission_energy_multiplier = 1.3
	barrier.material_override = amber
	barrier.visible = false
	fighter.add_child(barrier)
	fighter.cosmetic_cue.connect(func(cue: Dictionary) -> void:
		if cue["kind"] in ["vfx_spawn", "barrier"]:
			barrier.visible = true
			barrier_until_ms = int(cue["at_ms"])+450)
	fighter.cosmetics_cancelled.connect(func() -> void: barrier.visible = false)
	var canvas: CanvasLayer = CanvasLayer.new()
	mesh_stage.add_child(canvas)
	var title: Label = Label.new()
	title.text = "SOLKAEL  /  LIONHEART"
	title.position = Vector2(44,16)
	title.add_theme_font_size_override("font_size",24)
	title.add_theme_color_override("font_color",Color("dac494"))
	canvas.add_child(title)
	var caption_background: ColorRect = ColorRect.new()
	caption_background.position = Vector2(0,root.size.y-30)
	caption_background.size = Vector2(root.size.x,30)
	caption_background.color = Color("07111f")
	canvas.add_child(caption_background)
	subtitle = Label.new()
	subtitle.text = "GUARDIAN + SHIELD   •   ART LOCK v1   •   " + clip.to_upper()
	subtitle.position = Vector2(44,root.size.y-24)
	subtitle.add_theme_font_size_override("font_size",14)
	canvas.add_child(subtitle)
	RenderingServer.viewport_set_measure_render_time(root.get_viewport_rid(), true)
	previous_us = Time.get_ticks_usec()
	process_frame.connect(step)


func step() -> void:
	frame_count += 1
	var reviewed_clip: String = clip
	var elapsed: float = float(Time.get_ticks_usec()-previous_us)/1000.0
	previous_us = Time.get_ticks_usec()
	if not replay_events.is_empty():
		fighter.present(replay_events if frame_count==1 else [],frame_count*1000/30)
		reviewed_clip = fighter.adapter.current_clip
		if frame_count*1000/30 > barrier_until_ms:
			barrier.visible = false
	elif turntable:
		var names: Array = fighter.contract["clips"].map(func(item: Dictionary) -> String: return String(item["name"]))
		var index: int = mini(frame_count / 90, names.size()-1)
		fighter.show_clip(String(names[index]), float(frame_count % 90)/30.0)
		reviewed_clip = String(names[index])
		fighter.rotation.y = sin(float(frame_count)/90.0)*0.35
	else:
		fighter.show_clip(clip,pose_time+float(frame_count)/60.0 if profile_animation else pose_time)
	if expression != "":
		fighter.set_expression(expression)
	subtitle.text = "GUARDIAN + SHIELD   •   " + ("RESOLVER REPLAY   •   " if not replay_events.is_empty() else "ART LOCK v1   •   ") + reviewed_clip.to_upper()
	if frame_count > 60:
		cpu_ms.append(RenderingServer.viewport_get_measured_render_time_cpu(root.get_viewport_rid()))
		gpu_ms.append(RenderingServer.viewport_get_measured_render_time_gpu(root.get_viewport_rid()))
		frame_ms.append(elapsed)
	if frame_count == (1800 if profile_animation else 360 if turntable and not replay_events.is_empty() else 900 if turntable else 90):
		process_frame.disconnect(step)
		await RenderingServer.frame_post_draw
		if captures != "":
			var err: Error = root.get_texture().get_image().save_png(captures)
			assert(err == OK)
		cpu_ms.sort()
		gpu_ms.sort()
		frame_ms.sort()
		var report: Dictionary = {"status":"pass", "resolution":[root.size.x,root.size.y], "adapter":RenderingServer.get_video_adapter_name(), "rendering_method":RenderingServer.get_current_rendering_method(), "render_cpu_ms_p50":cpu_ms[cpu_ms.size()/2], "render_gpu_ms_p50":gpu_ms[gpu_ms.size()/2], "render_cpu_ms_p95":cpu_ms[int(cpu_ms.size()*.95)], "render_gpu_ms_p95":gpu_ms[int(gpu_ms.size()*.95)], "frame_ms_p50":frame_ms[frame_ms.size()/2], "draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), "rendered_primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME), "rendered_objects":Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME), "video_memory_bytes":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED), "texture_memory_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED), "samples":cpu_ms.size(), "clip":clip, "limitations":"Single desktop fighter plus QA stage; not physical phone or two-fighter arena budgets"}
		report["replay_event_hash"] = replay_hash
		report["cosmetic_cues"] = fighter.adapter.cue_count
		report["adapter_errors"] = fighter.adapter.errors
		report["movie_mode"] = turntable
		report["animated_profile"] = profile_animation
		report["replay_entity_id"] = replay_entity_id
		report["replay_scenario"] = replay_scenario
		if not replay_events.is_empty():
			assert(fighter.adapter.entity_id == replay_entity_id and fighter.adapter.cue_count > 0, "Replay review must exercise the actual resolver entity")
		if captures != "":
			var file: FileAccess = FileAccess.open(captures.get_basename()+".json",FileAccess.WRITE)
			file.store_string(JSON.stringify(report,"  "))
		print("FIGHTER_REVIEW_PASS "+JSON.stringify(report))
		quit(0)
