extends Node3D
## Foundation presentation only. Owns no gameplay rules or definitions.

@onready var camera: Camera3D = $Camera3D
@onready var safe_area: MarginContainer = $UI/SafeArea

func _ready() -> void:
	camera.look_at(Vector3(0, 0.55, 0))
	get_viewport().size_changed.connect(_update_safe_area)
	_update_safe_area()
	var players: Array[Node] = $PipelineSample.find_children("*", "AnimationPlayer", true, false)
	for node: Node in players:
		var player: AnimationPlayer = node as AnimationPlayer
		for animation_name: StringName in player.get_animation_list():
			if String(animation_name).ends_with("idle"):
				player.get_animation(animation_name).loop_mode = Animation.LOOP_LINEAR
				player.play(animation_name)
	print("FOUNDATION_BOOT_OK renderer=", RenderingServer.get_current_rendering_method())
	if "--capture-foundation" in OS.get_cmdline_user_args():
		await _capture()

func _update_safe_area() -> void:
	if DisplayServer.get_name() == "headless":
		return
	var window_size: Vector2i = DisplayServer.window_get_size()
	var safe: Rect2i = DisplayServer.get_display_safe_area()
	var window_position: Vector2i = DisplayServer.window_get_position()
	var scale_factor: float = get_viewport().get_visible_rect().size.x / maxf(window_size.x, 1.0)
	var left: int = maxi(0, safe.position.x - window_position.x)
	var top: int = maxi(0, safe.position.y - window_position.y)
	var right: int = maxi(0, window_position.x + window_size.x - safe.end.x)
	var bottom: int = maxi(0, window_position.y + window_size.y - safe.end.y)
	safe_area.add_theme_constant_override("margin_left", 32 + int(left * scale_factor))
	safe_area.add_theme_constant_override("margin_right", 32 + int(right * scale_factor))
	safe_area.add_theme_constant_override("margin_top", 28 + int(top * scale_factor))
	safe_area.add_theme_constant_override("margin_bottom", 28 + int(bottom * scale_factor))

func _capture() -> void:
	for frame: int in range(8):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var output: String = OS.get_environment("HERO_SMASH_CAPTURE")
	if output.is_empty():
		push_error("HERO_SMASH_CAPTURE must name the screenshot output")
		get_tree().quit(1)
		return
	var error: Error = get_viewport().get_texture().get_image().save_png(output)
	print("FOUNDATION_CAPTURE result=", error, " path=", output)
	get_tree().quit(0 if error == OK else 1)
