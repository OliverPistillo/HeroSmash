class_name TwoFighterSlice
extends Node3D
## One resolver stream, two identical visual consumers. QA stage only.

const FIGHTER: PackedScene = preload("res://scenes/characters/solkael_lionheart/hero_solkael_lionheart_v002.tscn")
var fighters: Array[SolkaelFighter] = []
var camera: Camera3D
var vfx_root: Node3D
var events: Array = []
var replay: Dictionary = {}
var timeline_ms: float = 0.0
var speed: float = 1.0
var playing: bool = true
var scenario_index: int = 0
var scenarios: CombatScenarios
var catalog: CombatCatalog
var hud: Label
var effects: Array[Dictionary] = []
var samples: Array[Dictionary] = []
var sample_clock: float = 0.0
var elapsed: float = 0.0
var capture_frames: int = 0
var coverage: Dictionary = {}
var intro_remaining: float = 1.0


func _ready() -> void:
	get_tree().root.content_scale_size = get_tree().root.size
	catalog = CombatCatalog.new()
	assert(catalog.load_data())
	scenarios = CombatScenarios.new(catalog)
	build_stage()
	for index: int in range(2):
		var fighter: SolkaelFighter = FIGHTER.instantiate() as SolkaelFighter
		fighter.entity_id = "alpha" if index == 0 else "beta"
		fighter.position = Vector3(-.65 if index == 0 else .65, 0, 0)
		fighter.rotation.y = PI/2 if index == 0 else -PI/2
		add_child(fighter)
		fighters.append(fighter)
		fighter.cosmetic_cue.connect(on_cue.bind(fighter))
		fighter.cosmetics_cancelled.connect(cancel_effects.bind(fighter.entity_id))
	load_scenario(0)
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	if OS.get_environment("HERO_SLICE_SCENARIO") != "":
		load_scenario(maxi(0,scenarios.ids().find(OS.get_environment("HERO_SLICE_SCENARIO"))))
	if OS.get_environment("HERO_SLICE_SPEED") != "":
		speed = OS.get_environment("HERO_SLICE_SPEED").to_float()
	get_viewport().size_changed.connect(layout_hud)
	layout_hud()
	print("SLICE_READY "+JSON.stringify({"load_ms":Time.get_ticks_msec(),"renderer":RenderingServer.get_current_rendering_method(),"adapter":RenderingServer.get_video_adapter_name()}))


func build_stage() -> void:
	var world: WorldEnvironment = WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color("101b2c")
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color("d8ddeb")
	world.environment.ambient_light_energy = .45
	world.environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	add_child(world)
	var key: DirectionalLight3D = DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-38,-25,0)
	key.shadow_enabled = true
	key.directional_shadow_max_distance = 15
	key.light_energy = 1.2
	add_child(key)
	var fill: DirectionalLight3D = DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-20,140,0)
	fill.light_energy = .45
	fill.light_color = Color("a9c7ed")
	add_child(fill)
	for layer: int in range(3):
		var stage: MeshInstance3D = MeshInstance3D.new()
		var box: BoxMesh = BoxMesh.new()
		box.size = Vector3(12,.10,2.2 if layer==0 else .20)
		stage.mesh = box
		stage.position = Vector3(0,-.055 if layer==0 else -.10,0 if layer==0 else -2.0 if layer==1 else 2.0)
		var mat: StandardMaterial3D = StandardMaterial3D.new()
		mat.albedo_color = Color("29394e") if layer==0 else Color("3f5267")
		mat.roughness = .85
		stage.material_override = mat
		add_child(stage)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_HEIGHT
	camera.size = 3.2
	camera.position = Vector3(0,2.1,7)
	add_child(camera)
	camera.look_at(Vector3(0,1.0,0))
	camera.current = true
	vfx_root = Node3D.new()
	vfx_root.name = "VFXRoot"
	add_child(vfx_root)
	var canvas: CanvasLayer = CanvasLayer.new()
	add_child(canvas)
	hud = Label.new()
	hud.add_theme_font_size_override("font_size",16)
	hud.add_theme_color_override("font_color",Color("efd9ae"))
	canvas.add_child(hud)
	var controls: HBoxContainer = HBoxContainer.new()
	controls.name = "Controls"
	controls.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	controls.position = Vector2(24,-58)
	canvas.add_child(controls)
	for label: String in ["x1","x2","x3","Replay","Next"]:
		var button: Button = Button.new()
		button.text = label
		button.custom_minimum_size = Vector2(62,40)
		controls.add_child(button)
		button.pressed.connect(func() -> void:
			if label.begins_with("x"): speed = label.trim_prefix("x").to_float()
			elif label=="Replay": seek_replay(0)
			else: load_scenario((scenario_index+1)%scenarios.ids().size()))


func layout_hud() -> void:
	var visible: Vector2 = get_viewport().get_visible_rect().size
	hud.position = Vector2(24,16)
	hud.get_parent().get_node("Controls").position = Vector2(24,visible.y-58)


func load_scenario(index: int) -> void:
	scenario_index = index
	var input: Dictionary = scenarios.build(scenarios.ids()[index],5)
	replay = CombatResolver.new(catalog).run(input,true)
	assert(replay["ok"])
	events = replay["events"]
	seek_replay(0)
	intro_remaining = 1.0


func seek_replay(at_ms: int) -> void:
	timeline_ms = at_ms
	for fighter: SolkaelFighter in fighters:
		fighter.seek_replay(events,at_ms)


func _process(delta: float) -> void:
	elapsed += delta
	if intro_remaining > 0:
		intro_remaining = maxf(0,intro_remaining-delta)
		for fighter: SolkaelFighter in fighters:
			fighter.show_clip("intro",1.0-intro_remaining)
	elif playing:
		timeline_ms += delta*1000.0*speed
		for fighter: SolkaelFighter in fighters:
			fighter.present([],int(timeline_ms))
			coverage[fighter.adapter.current_clip] = true
		update_blocking()
		if timeline_ms > float(replay["result"]["duration_ms"])+3000:
			load_scenario((scenario_index+1)%scenarios.ids().size())
	for index: int in range(effects.size()-1,-1,-1):
		var item: Dictionary = effects[index]
		if timeline_ms > float(item["until"]):
			(item["node"] as Node).queue_free()
			effects.remove_at(index)
	hud.text = "SOLKAEL  /  COMBAT SLICE   x%d\n%s   %.1fs" % [int(speed),scenarios.ids()[scenario_index],timeline_ms/1000.0]
	sample_clock += delta
	if sample_clock >= 1.0:
		sample_clock = 0
		var rid: RID = get_viewport().get_viewport_rid()
		var sample: Dictionary = {"elapsed_s":elapsed,"fps":Engine.get_frames_per_second(),"process_ms":Performance.get_monitor(Performance.TIME_PROCESS)*1000,"render_cpu_ms":RenderingServer.viewport_get_measured_render_time_cpu(rid),"render_gpu_ms":RenderingServer.viewport_get_measured_render_time_gpu(rid),"memory_bytes":OS.get_static_memory_usage(),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"texture_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)}
		samples.append(sample)
		if samples.size()>600:samples.pop_front()
		print("SLICE_SAMPLE "+JSON.stringify(sample))
	capture_frames += 1
	var capture: String = OS.get_environment("HERO_SLICE_CAPTURE")
	var profile_seconds: float = OS.get_environment("HERO_SLICE_PROFILE_SECONDS").to_float()
	if capture != "" and ((profile_seconds<=0 and capture_frames==180) or (profile_seconds>0 and elapsed>=profile_seconds)):
		set_process(false)
		capture_result(capture)


func cancel_effects(entity: String) -> void:
	for index: int in range(effects.size()-1,-1,-1):
		if effects[index]["entity"] == entity:
			(effects[index]["node"] as Node).queue_free()
			effects.remove_at(index)


func update_blocking() -> void:
	# Same visual step-in for either side. The resolver has no world-position input.
	for index: int in range(fighters.size()):
		var fighter: SolkaelFighter = fighters[index]
		var direction: float = 1.0 if index==0 else -1.0
		fighter.position.x = -.65*direction
		if fighter.adapter.current_clip in ["attack_light","attack_heavy"]:
			var since_contact: float = float(fighter.adapter.clock_ms-fighter.adapter.clip_started_ms)/1000.0
			var step_in: float = .10 if fighter.adapter.current_clip=="attack_light" else .24
			fighter.position.x += direction*step_in*maxf(0.0,1.0-since_contact/.35)


func on_cue(cue: Dictionary, fighter: SolkaelFighter) -> void:
	coverage[String(cue["kind"])] = true
	# Bounded solid geometry effects: no alpha cards, particles or extra lights.
	if effects.size()>=12:return
	var effect: MeshInstance3D = MeshInstance3D.new()
	var ring: TorusMesh = TorusMesh.new()
	var barrier: bool = cue["kind"] in ["barrier","vfx_spawn"]
	ring.inner_radius = .49 if barrier else .09
	ring.outer_radius = .52 if barrier else .12
	ring.rings = 32 if barrier else 12
	ring.ring_segments = 6
	effect.mesh = ring
	var mat: StandardMaterial3D = StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color("93bd70") if cue["kind"]=="periodic" else Color("a8d8ff") if cue["kind"]=="reflection" else Color("ffb347")
	effect.material_override = mat
	effect.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	vfx_root.add_child(effect)
	effect.global_position = fighter.socket_transform("socket_vfx_chest").origin
	if cue["kind"]=="hit":
		effect.global_position = fighter.socket_transform("socket_weapon_r" if fighter.adapter.current_clip=="attack_heavy" else "socket_weapon_l").origin
	effect.rotation.z = PI/2
	if barrier:effect.global_position += fighter.basis.z*.35
	effects.append({"node":effect,"entity":fighter.entity_id,"until":int(cue["at_ms"])+(450 if barrier else 160)})
	if OS.get_environment("HERO_SLICE_HOLD_BARRIER")=="1" and barrier:
		playing = false


func capture_result(path: String) -> void:
	await RenderingServer.frame_post_draw
	assert(get_viewport().get_texture().get_image().save_png(path)==OK)
	var result: Dictionary = {"resolution":[get_viewport().size.x,get_viewport().size.y],"source":"desktop Vulkan Mobile; not a physical phone","samples":samples,"coverage":coverage,"event_hash":replay["eventHash"],"errors":[fighters[0].adapter.errors,fighters[1].adapter.errors]}
	var file: FileAccess = FileAccess.open(path.get_basename()+".json",FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"  "))
	print("SLICE_CAPTURE_PASS")
	get_tree().quit()
