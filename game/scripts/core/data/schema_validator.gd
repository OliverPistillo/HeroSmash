class_name CanonicalSchemaValidator
extends RefCounted
## Evaluates the documented Draft 2020-12 subset, never silently ignores keywords.

const KEYWORDS: Array[String] = ["$schema", "$id", "type", "properties", "required", "additionalProperties", "items", "minItems", "maxItems", "uniqueItems", "enum", "const", "minimum", "maximum", "minLength", "maxLength", "pattern"]
var errors: Array[String] = []

func validate(value: Variant, schema: Dictionary, path: String = "$") -> Array[String]:
	errors.clear()
	_check_schema(schema, "schema")
	if errors.is_empty():
		_visit(value, schema, path)
	return errors.duplicate()

func _check_schema(schema: Dictionary, path: String) -> void:
	for key: String in schema:
		if not KEYWORDS.has(key):
			errors.append("%s: unsupported_schema_keyword %s" % [path, key])
	for key: String in schema.get("properties", {}):
		_check_schema(schema["properties"][key], path + "." + key)
	if schema.has("items"):
		_check_schema(schema["items"], path + "[]")

func _is_type(value: Variant, kind: String) -> bool:
	match kind:
		"object": return value is Dictionary
		"array": return value is Array
		"string": return value is String
		"boolean": return value is bool
		"null": return value == null
		"number": return (value is int or value is float) and is_finite(float(value))
		"integer": return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value))
	return false

func _visit(value: Variant, schema: Dictionary, path: String) -> void:
	if schema.has("type"):
		var types: Array = schema["type"] if schema["type"] is Array else [schema["type"]]
		var valid: bool = false
		for kind: String in types:
			valid = valid or _is_type(value, kind)
		if not valid:
			errors.append("%s: expected %s" % [path, str(types)])
			return
	if schema.has("const") and value != schema["const"]:
		errors.append(path + ": unexpected constant/version")
	if schema.has("enum") and not schema["enum"].has(value):
		errors.append(path + ": unknown enum value " + str(value))
	if value is Dictionary:
		var properties: Dictionary = schema.get("properties", {})
		for key: String in schema.get("required", []):
			if not value.has(key):
				errors.append(path + ": missing " + key)
		for key: String in value:
			if properties.has(key):
				_visit(value[key], properties[key], path + "." + key)
			elif schema.get("additionalProperties", true) == false:
				errors.append(path + ": unknown field " + key)
	elif value is Array:
		if value.size() < int(schema.get("minItems", 0)) or value.size() > int(schema.get("maxItems", 2147483647)):
			errors.append(path + ": invalid array length")
		var seen: Array = []
		for index: int in range(value.size()):
			if schema.get("uniqueItems", false) and seen.has(value[index]):
				errors.append(path + ": duplicate array value")
			seen.append(value[index])
			if schema.has("items"):
				_visit(value[index], schema["items"], "%s[%d]" % [path, index])
	elif value is String:
		if value.length() < int(schema.get("minLength", 0)) or value.length() > int(schema.get("maxLength", 2147483647)):
			errors.append(path + ": invalid string length")
		if schema.has("pattern"):
			var regex: RegEx = RegEx.new()
			if regex.compile(schema["pattern"]) != OK or regex.search(value) == null:
				errors.append(path + ": invalid string pattern")
	elif value is int or value is float:
		if float(value) < float(schema.get("minimum", -INF)) or float(value) > float(schema.get("maximum", INF)):
			errors.append(path + ": numeric bounds")
