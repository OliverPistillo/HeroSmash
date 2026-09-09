class_name SolkaelFighter
extends Node3D
## Typed presentation boundary: this scene has no resolver/catalog mutation API.

signal cosmetic_cue(cue: Dictionary)
signal cosmetics_cancelled

const CONTRACT_PATH: String = "res://assets/characters/solkael_lionheart/fighter_presentation.json"
@export var entity_id: String = "A"
var adapter: FighterEventAdapter = FighterEventAdapter.new()
var animation_player: AnimationPlayer
var skeleton: Skeleton3D
var meshes: Array[MeshInstance3D] = []
var contract: Dictionary = {}
var clip_names: Dictionary = {}
var _last_clip: String = ""


func _ready() -> void:
	contract = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT_PATH)) as Dictionary
	_collect(self)
	assert(animation_player != null and skeleton != null)
	for full_name: StringName in animation_player.get_animation_list():
		clip_names[String(full_name).get_slice("/", String(full_name).get_slice_count("/") - 1)] = String(full_name)
	for clip: Dictionary in contract["clips"]:
		var name: String = String(clip["name"])
		if clip_names.has(name):
			var animation: Animation = animation_player.get_animation(StringName(clip_names[name]))
			animation.loop_mode = Animation.LOOP_LINEAR if bool(clip["loop"]) else Animation.LOOP_NONE
	adapter.configure(entity_id, contract["clips"])
	# Timeline controls playback; AnimationPlayer does not advance on a second clock.
	animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	show_clip("idle", 0.0)


func _collect(node: Node) -> void:
	if node is AnimationPlayer:
		animation_player = node as AnimationPlayer
	if node is Skeleton3D:
		skeleton = node as Skeleton3D
	if node is MeshInstance3D:
		meshes.append(node as MeshInstance3D)
	for child: Node in node.get_children():
		_collect(child)


func present(events: Array, timeline_ms: int) -> void:
	var was_dead: bool = adapter.dead
	adapter.enqueue(events)
	var cues: Array[Dictionary] = adapter.advance(timeline_ms)
	if adapter.dead and not was_dead:
		cosmetics_cancelled.emit()
	show_clip(adapter.current_clip, adapter.pose_seconds())
	for cue: Dictionary in cues:
		cosmetic_cue.emit(cue.duplicate(true))


func seek_replay(events: Array, timeline_ms: int) -> void:
	cosmetics_cancelled.emit()
	adapter.seek(events, timeline_ms)
	show_clip(adapter.current_clip, adapter.pose_seconds())


func show_clip(name: String, seconds: float) -> void:
	if not clip_names.has(name):
		adapter.errors.append("missing_imported_clip:" + name)
		name = "idle"
	if not clip_names.has(name):
		return
	var full_name: StringName = StringName(clip_names[name])
	var animation: Animation = animation_player.get_animation(full_name)
	if _last_clip != name:
		animation_player.play(full_name)
		_last_clip = name
	var position: float = fposmod(seconds, animation.length) if animation.loop_mode == Animation.LOOP_LINEAR else clampf(seconds, 0.0, animation.length)
	animation_player.seek(position, true, true)
	set_expression({"attack_light":"focused", "attack_heavy":"aggressive", "skill_cast":"casting", "hit_react":"pain_light", "dodge":"focused", "ko":"ko", "victory":"victory"}.get(name, "neutral"))


func set_expression(expression: String, strength: float = 1.0) -> void:
	for instance: MeshInstance3D in meshes:
		if instance.mesh == null:
			continue
		for index: int in range(instance.mesh.get_blend_shape_count()):
			var name: String = String(instance.mesh.get_blend_shape_name(index))
			instance.set_blend_shape_value(index, clampf(strength, 0.0, 1.0) if name == "expr_" + expression.to_lower() else 0.0)


func socket_transform(socket_name: String) -> Transform3D:
	var index: int = skeleton.find_bone(socket_name)
	assert(index >= 0, "Unknown documented socket")
	return skeleton.global_transform * skeleton.get_bone_global_pose(index)
