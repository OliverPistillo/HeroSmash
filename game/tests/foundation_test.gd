extends SceneTree

const Rng = preload("res://scripts/core/foundation_rng.gd")
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)

func _run() -> void:
	var version: Dictionary = Engine.get_version_info()
	check(version["major"] == 4 and version["minor"] == 7 and version["patch"] == 2 and version["status"] == "stable", "Godot version pin")
	check(ProjectSettings.get_setting("rendering/renderer/rendering_method") == "mobile", "Mobile renderer configured")
	check(ProjectSettings.get_setting("display/window/handheld/orientation") == 0, "Landscape configured")
	var rng: RefCounted = Rng.new(1)
	for expected: int in [1015568748, 1586005467, 2165703038]:
		check(rng.next_u32() == expected, "Known RNG vector")
	var first: RefCounted = Rng.new(42)
	var second: RefCounted = Rng.new(42)
	for index: int in range(1000):
		check(first.next_u32() == second.next_u32(), "Seed repeatability")
	var packed: PackedScene = load("res://scenes/app/bootstrap.tscn") as PackedScene
	check(packed != null, "Bootstrap scene loads")
	if packed != null:
		var instance: Node = packed.instantiate()
		root.add_child(instance)
		await process_frame
		check(instance.find_children("*", "Skeleton3D", true, false).size() == 1, "One imported skeleton")
		check(instance.find_children("*", "MeshInstance3D", true, false).size() >= 2, "Imported mesh and arena floor")
		var animated: bool = false
		for node: Node in instance.find_children("*", "AnimationPlayer", true, false):
			var player: AnimationPlayer = node as AnimationPlayer
			for animation_name: StringName in player.get_animation_list():
				animated = animated or String(animation_name).ends_with("idle")
		check(animated, "Imported idle animation")
		instance.queue_free()
		await process_frame
	if failures.is_empty():
		print("FOUNDATION_TEST_PASS seed_vectors=3 repeated_values=1000 imported_skeleton=1 animation=idle")
	else:
		for failure: String in failures:
			push_error(failure)
	quit(0 if failures.is_empty() else 1)
