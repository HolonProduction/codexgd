@tool
extends EditorPlugin


const __AnnotationLayer := preload("res://addons/codexgd/annotation_layer.gd")

var annotation_layer: __AnnotationLayer
var color_map: Dictionary

var thread: Thread = null

func _enter_tree() -> void:
	setup_editor_settings()

	color_map = {
		"warn": get_editor_interface().get_base_control().get_theme_color(&"warning_color", &"Editor"),
		"error": get_editor_interface().get_base_control().get_theme_color(&"error_color", &"Editor"),
	}
	annotation_layer = __AnnotationLayer.new()
	get_editor_interface().get_script_editor().add_child(annotation_layer)

	get_editor_interface().get_resource_filesystem().filesystem_changed.connect(__on_filesystem_changed, CONNECT_DEFERRED)
	__on_filesystem_changed()


func _exit_tree() -> void:
	annotation_layer.queue_free()

	thread.wait_to_finish()


func setup_editor_settings():
	var settings = get_editor_interface().get_editor_settings()

	if not settings.has_setting("codexgd/general/command_path"):
		settings.set_setting("codexgd/general/command_path", "codexgd")
	settings.set_initial_value("codexgd/general/command_path", "codexgd", false)
	settings.add_property_info({
		"name": "codexgd/general/command_path",
		"type": TYPE_STRING,
		"hint": PROPERTY_HINT_GLOBAL_FILE,
	})

	if not settings.has_setting("codexgd/general/load_unsafe_rules"):
		settings.set_setting("codexgd/general/load_unsafe_rules", false)
	settings.set_initial_value("codexgd/general/load_unsafe_rules", false, false)
	settings.add_property_info({
		"name": "codexgd/general/load_unsave_rules",
		"type": TYPE_BOOL,
	})


func scan():
	var res := []
	var settings = get_editor_interface().get_editor_settings()
	var options = [ProjectSettings.globalize_path("res://"), "--json"]
	if settings.get_setting("codexgd/general/load_unsafe_rules"):
		options.append("--load-unsafe-code")
	OS.execute(settings.get_setting("codexgd/general/command_path"), options, res)
	annotation_layer.clear_annotations()
	for i in JSON.parse_string(res[0]):
		var script = load(i["file"])
		var color = color_map[i["severity"]]
		var start = Vector2i(i["start"][0], i["start"][1])
		var end = Vector2i(i["end"][0], i["end"][1])
		var annotation = __AnnotationLayer.AnnotationData.new(script, color, start, end, i["info"])
		annotation_layer.add_annotation(annotation)


func __on_filesystem_changed():
	if thread and not thread.is_started():
		print(thread)

	if thread and not thread.is_alive():
		thread.wait_to_finish()
		thread = null

	if not thread:
		thread = Thread.new()
		thread.start(scan)
