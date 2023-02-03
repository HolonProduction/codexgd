@tool
extends Node


## Displays annotations over the opened script editor.


class AnnotationData extends RefCounted:
	var source_script: Script
	var color: Color
	var start: Vector2i
	var end: Vector2i
	var hint: String


	func _init(p_source_script: Script, p_color: Color, p_start: Vector2i, p_end: Vector2i, p_hint: String = ""):
		source_script = p_source_script
		color = p_color
		start = p_start
		end = p_end
		hint = p_hint


var annotations: Array[AnnotationData] = []
var __script_editor: ScriptEditor
var __current_script_annotations: Array[AnnotationData] = []
var __annotation_rects: Array[ColorRect] = []
var __current_base_editor: TextEdit


func _ready() -> void:
	__script_editor = get_parent() as ScriptEditor
	__script_editor.editor_script_changed.connect(__on_script_changed)
	__on_script_changed(__script_editor.get_current_script())



func _exit_tree() -> void:
	for rect in __annotation_rects:
		rect.queue_free()


func clear_annotations() -> void:
	annotations.clear()
	if __script_editor:
		__on_script_changed(__script_editor.get_current_script())


func add_annotation(data: AnnotationData) -> void:
	annotations.append(data)
	if __script_editor:
		__on_script_changed(__script_editor.get_current_script())


func remove_annotation(data: AnnotationData) -> void:
	annotations.erase(data)
	if __script_editor:
		__on_script_changed(__script_editor.get_current_script())


# HACK: Typing on p_script makes problems.
func __on_script_changed(p_script = null) -> void:
	if is_instance_valid(__current_base_editor) and __current_base_editor.gui_input.is_connected(__on_base_editor_gui_input):
		__current_base_editor.get_h_scroll_bar().value_changed.disconnect(__on_should_draw)
		__current_base_editor.get_v_scroll_bar().value_changed.disconnect(__on_should_draw)
		__current_base_editor.gui_input.disconnect(__on_base_editor_gui_input)
	var current_editor = __script_editor.get_current_editor()
	if is_instance_valid(current_editor):
		__current_base_editor = current_editor.get_base_editor()
		__current_base_editor.get_h_scroll_bar().value_changed.connect(__on_should_draw)
		__current_base_editor.get_v_scroll_bar().value_changed.connect(__on_should_draw)
		__current_base_editor.gui_input.connect(__on_base_editor_gui_input)

	__current_script_annotations = []
	for annotation in annotations:
		if p_script and annotation.source_script == p_script:
			__current_script_annotations.append(annotation)
	__on_should_draw()


func __on_base_editor_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.is_pressed() and not event.is_echo():
		__on_should_draw()
	if event is InputEventShortcut:
		__on_should_draw()


func __on_should_draw(_value1: int = 0, _value2: int = 0) -> void:
	await get_tree().create_timer(0.0).timeout
	for rect in __annotation_rects:
		rect.hide()
		rect.queue_free()
	__annotation_rects = []

	for annotation in __current_script_annotations:
		# The values are transfered with 1 as starting line and column.
		# In code a start at 0 is more convenient.
		var end = annotation.end - Vector2i.ONE
		var pos = annotation.start - Vector2i.ONE

		# Resolve -1 in file position as start/end of file/line.
		if pos.x < 0:
			pos.x = 0
		if pos.y < 0:
			pos.y = 0

		if end.x < 0:
			end.x = __current_base_editor.get_line_count()
		if end.y < 0:
			end.y = len(__current_base_editor.get_line(end.x))

		var rect = null

		while true:
			if end.x < pos.x or (end.x == pos.x and end.y <= pos.y):
				if rect:
					__draw_annotation(rect, annotation)
				rect = null
				break

			if len(__current_base_editor.get_line(pos.x)) == 0:
				var r = __current_base_editor.get_rect_at_line_column(pos.x, 0)
				if r.position.abs() == r.position:
					# Get width of a space char.
					r.size.x += __current_base_editor.get_theme_font(&"font").get_char_size(32, __current_base_editor.get_theme_font_size(&"font_size")).x
					__draw_annotation(r, annotation)
			elif rect != null:
				var n_rect = __current_base_editor.get_rect_at_line_column(pos.x, pos.y + 1)
				if n_rect.position.abs() == n_rect.position:
					rect.size.x += n_rect.size.x
				else:
					__draw_annotation(rect, annotation)
					rect = null
			else:
				rect = __current_base_editor.get_rect_at_line_column(pos.x, pos.y + 1)
				if rect.position.abs() != rect.position:
					rect = null

			pos.y += 1
			if len(__current_base_editor.get_line(pos.x)) <= pos.y:
				if rect:
					__draw_annotation(rect, annotation)
				rect = null
				pos.y = 0
				pos.x += 1


func __draw_annotation(rect, annotation):
	var color_rect = ColorRect.new()
	color_rect.position = rect.position
	color_rect.tooltip_text = annotation.hint
	color_rect.size = rect.size
	color_rect.mouse_filter = Control.MOUSE_FILTER_PASS
	color_rect.color = Color(annotation.color, 0.4)
	__current_base_editor.add_child(color_rect)
	__annotation_rects.append(color_rect)
